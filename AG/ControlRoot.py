#  This is a program to read & send command. Created by Frank.

import serial
import time
import crcmod


class ControlRoot(object):
    # 初始化串口
    def __init__(self, com="/dev/ttyUSB0"):
        self.sc = serial.Serial(port=com, baudrate=115200)
        self.crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

    # 计算CRC校验码
    def calCrc(self, array):
        bytes_ = b''
        for i in range(array.__len__()):
            bytes_ = bytes_ + array[i].to_bytes(1, byteorder='big', signed=True)
        crc = self.crc16(bytes_).to_bytes(2, byteorder='big', signed=False)
        crcH = int.from_bytes(crc[0:1], byteorder='big', signed=False)
        crcQ = int.from_bytes(crc[1:2], byteorder='big', signed=False)
        return crcQ, crcH

    # 读取串口接收的数据
    def readSerial(self):
        # BTime = time.time()
        time.sleep(0.08)
        readContent = self.sc.read_all()
        return readContent

    # 发送指令
    def sendCmd(self, ModbusHighAddress, ModbusLowAddress, Value=0x01, isSet=True, isReadSerial=True):
        if isSet:
            SetAddress = 0x06
        else:
            SetAddress = 0x03
        Value = Value if Value >= 0 else Value - 1
        bytes_ = Value.to_bytes(2, byteorder='big', signed=True)
        ValueHexQ = int.from_bytes(bytes_[0:1], byteorder='big', signed=True)
        ValueHexH = int.from_bytes(bytes_[1:2], byteorder='big', signed=True)
        array = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, ValueHexQ, ValueHexH]
        currentValueQ, currentValueH = self.calCrc(array)
        setValueCmd = [0x01, SetAddress, ModbusHighAddress, ModbusLowAddress, ValueHexQ, ValueHexH,
                       currentValueQ,
                       currentValueH]
        for i in range(setValueCmd.__len__()):
            setValueCmd[i] = setValueCmd[i] if setValueCmd[i] >= 0 else setValueCmd[i] + 256
        self.sc.write(setValueCmd)

        if isReadSerial:
            back = self.readSerial()  # 读取串口返回的数据
            value = int.from_bytes(back[3:5], byteorder='big', signed=True)
            if value < 0:
                value = value + 1
            self.sc.flush()  # 清空串口接收缓存
            return value
        else:
            time.sleep(0.005)
            return
