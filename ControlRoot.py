'''

'''
import serial
import time
import crcmod
import threading
from tqdm import *


class ControlRoot(object):
    def __init__(self, com="/dev/ttyUSB0"):
        self.sc = serial.Serial(port=com, baudrate=115200)
        self.crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

    def calCrc(self, array):
        bytes_ = b''
        for i in range(array.__len__()):
            bytes_ = bytes_ + array[i].to_bytes(1, byteorder='little', signed=True)
        crc = hex(self.crc16(bytes_))
        crcQ = '0x' + crc[-2] + crc[-1]
        crcH = '0x' + crc[-4] + crc[-3]
        return int(crcQ.encode(), 16), int(crcH.encode(), 16)

    def readSerial(self):
        # BTime = time.time()
        time.sleep(0.008)
        readContent = self.sc.read_all()
        return readContent

    def sendCmd(self, ModbusHighAddress, ModbusLowAddress, Value=0x01, isSet=True, isReadSerial=True):
        if isSet:
            SetAddress = 0x06
        else:
            SetAddress = 0x03
        if Value < 0:
            ValueHex = hex(Value)
            if ValueHex.__len__() <= 5:
                array = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, 0x00, Value]
                currentValueQ, currentValueH = self.calCrc(array)
                setValueCmd = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, 0x00,
                               int('0x' + (Value.to_bytes(1, byteorder='little', signed=True).hex()), 16),
                               currentValueQ,
                               currentValueH]
            elif ValueHex.__len__() == 6:
                ValueHex = hex(Value)
                ValueHexQ = int(ValueHex[0] + ValueHex[1] + ValueHex[2] + ValueHex[3], 16) - 1
                ValueHexH = int(ValueHex[0] + ValueHex[1] + ValueHex[2] + ValueHex[-2] + ValueHex[-1],
                                16) - 1
                array = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, ValueHexQ, ValueHexH]
                currentValueQ, currentValueH = self.calCrc(array)
                setValueCmd = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress,
                               int('0x' + (ValueHexQ.to_bytes(1, byteorder='little', signed=True).hex()), 16),
                               int('0x' + ValueHexH.to_bytes(1, byteorder='little', signed=True).hex(), 16),
                               currentValueQ,
                               currentValueH]
            else:
                ValueHex = hex(Value)
                ValueHexQ = int(ValueHex[0] + ValueHex[1] + ValueHex[2] + ValueHex[3] + ValueHex[4],
                                16) - 1
                ValueHexH = int(ValueHex[0] + ValueHex[1] + ValueHex[2] + ValueHex[-2] + ValueHex[-1],
                                16) - 1
                array = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, ValueHexQ, ValueHexH]
                currentValueQ, currentValueH = self.calCrc(array)
                setValueCmd = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress,
                               int('0x' + (ValueHexQ.to_bytes(1, byteorder='little', signed=True).hex()), 16),
                               int('0x' + ValueHexH.to_bytes(1, byteorder='little', signed=True).hex(), 16),
                               currentValueQ,
                               currentValueH]

        else:
            ValueHex = hex(Value)
            if ValueHex.__len__() <= 4:
                array = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, 0x00, Value]
                currentValueQ, currentValueH = self.calCrc(array)
                setValueCmd = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, 0x00, Value, currentValueQ,
                               currentValueH]
            else:
                ValueHex = hex(Value)
                ValueHexQ = int(ValueHex[0] + ValueHex[1] + ValueHex[2], 16)
                ValueHexH = int(ValueHex[0] + ValueHex[1] + ValueHex[-2] + ValueHex[-1], 16)
                array = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, ValueHexQ, ValueHexH]
                currentValueQ, currentValueH = self.calCrc(array)
                setValueCmd = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, ValueHexQ, ValueHexH,
                               currentValueQ,
                               currentValueH]
        self.sc.write(setValueCmd)
        if isReadSerial:
            back = self.readSerial()
            value = int.from_bytes(back[3:5], byteorder='big', signed=True)
            if value < 0:
                value = value + 1
            self.sc.flush()
            return value
        else:
            time.sleep(0.005)
            return
