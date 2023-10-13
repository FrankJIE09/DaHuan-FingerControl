#  This is a program to read & send command. Created by Frank.

import serial
import time
import crcmod


def convert_to_bytes(num):
    b1 = (num >> 24) & 0xFF
    b2 = (num >> 16) & 0xFF
    b3 = (num >> 8) & 0xFF
    b4 = num & 0xFF
    return [b4, b3, b2, b1]


class ControlRoot(object):
    # 初始化串口
    def __init__(self, com="/dev/ttyACM0"):
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
        time.sleep(0.008)
        readContent = self.sc.read_all()
        return readContent

    # 发送指令
    def sendCmd(self, ModbusHighAddress, ModbusLowAddress, Value=0x01, is_write=True, isReadSerial=True):
        if is_write:
            SetAddress = 0x01
        else:
            SetAddress = 0x00
        # Value = Value if Value >= 0 else Value - 1
        Value_hex_part1,Value_hex_part2,Value_hex_part3,Value_hex_part4 = convert_to_bytes(Value)
        # Value_hex_part1 = int.from_bytes(bytes_[0:1], byteorder='big', signed=True)
        # Value_hex_part1 = int.from_bytes(bytes_[0:1], byteorder='big', signed=True)
        # Value_hex_part1 = int.from_bytes(bytes_[0:1], byteorder='big', signed=True)
        # Value_hex_part1 = int.from_bytes(bytes_[0:1], byteorder='big', signed=True)

        # ValueHexH = int.from_bytes(bytes_[1:2], byteorder='big', signed=True)

        setValueCmd = [0xFF,0xFE,0xFD,0xFC, 0x01, ModbusHighAddress, ModbusLowAddress, SetAddress, 0x00, Value_hex_part1,
                       Value_hex_part2, Value_hex_part3, Value_hex_part4, 0xFB]
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
            time.sleep(0.01)
            return
