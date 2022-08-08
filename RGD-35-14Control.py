'''

'''
import serial
import time
import crcmod
import threading
from tqdm import *

close_cmd = [0xA0, 0x01, 0x01, 0xA2]


class ComSwitch(object):
    def __init__(self, com="/dev/ttyUSB0"):
        self.sc = serial.Serial(port=com, baudrate=115200)
        self.crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

    def calCrc(self, array):
        bytes_ = b''
        for i in range(array.__len__()):
            bytes_ = bytes_ + array[i].to_bytes(1, byteorder='little', signed=True)
        crc = hex(self.crc16(bytes_))
        print(bytes_)
        print(crc)
        crcQ = '0x' + crc[-2] + crc[-1]
        crcH = '0x' + crc[-4] + crc[-3]
        return int(crcQ.encode(), 16), int(crcH.encode(), 16)

    def readSerial(self):
        # BTime = time.time()
        time.sleep(0.025)
        readContent = self.sc.read_all()
        # self.sc.flush()
        return readContent

    # 初始化夹爪
    def InitFinger(self):
        init_cmd = [0x01, 0x06, 0x01, 0x00, 0x00, 0x01, 0x49, 0xF6]
        self.sc.write(init_cmd)
        print(self.readSerial())

    # 力值
    def setForce(self, Force):
        array = [0x01, 0x06, 0x01, 0x01, 0x00, Force]
        crcQ, crcH = self.calCrc(array)
        ForceCmd = [0x01, 0x06, 0x01, 0x01, 0x00, Force, crcQ, crcH]
        self.sc.write(ForceCmd)
        print(self.readSerial())

    # 读取设定位置
    def readSetPosition(self):
        # 01 03 01 03 00 01 75 F6
        readPositionCmd = [0x01, 0x03, 0x01, 0x03, 0x00, 0x01, 0x75, 0xF6]
        self.sc.write(readPositionCmd)
        data = self.readSerial()
        divData = str(data).split("\\x")
        PosInt = int((divData[-4] + divData[-3]).encode(), 16)
        return PosInt

    # 读取实时位置
    def readCurrentPosition(self, loop):
        # 01 03 01 03 00 01 75 F6
        readPositionCmd = [0x01, 0x03, 0x02, 0x02, 0x00, 0x01, 0x24, 0x72]
        self.sc.write(readPositionCmd)
        data = self.readSerial()
        divData = str(data).split("\\x")
        PosInt = int((divData[-4] + divData[-3]).encode(), 16)
        print(PosInt)
        return PosInt

    # 设置夹爪位置
    def setPosition(self, Position):
        PositionHex = hex(Position)
        if PositionHex.__len__() <= 4:
            array = [0x01, 0x06, 0x01, 0x03, 0x00, Position]
            currentPositionQ, currentPositionH = self.calCrc(array)
            setPositionCmd = [0x01, 0x06, 0x01, 0x03, 0x00, Position, currentPositionQ, currentPositionH]
        else:
            PositionHex = hex(Position)
            PositionHexQ = int(PositionHex[0] + PositionHex[1] + PositionHex[2], 16)
            PositionHexH = int(PositionHex[0] + PositionHex[1] + PositionHex[-2] + PositionHex[-1], 16)
            array = [0x01, 0x06, 0x01, 0x03, PositionHexQ, PositionHexH]
            currentPositionQ, currentPositionH = self.calCrc(array)
            setPositionCmd = [0x01, 0x06, 0x01, 0x03, PositionHexQ, PositionHexH, currentPositionQ, currentPositionH]
        self.sc.write(setPositionCmd)
        print(self.readSerial())

    # 初始化反馈
    def initFeedback(self):
        cmd = [0x01, 0x03, 0x02, 0x00, 0x00, 0x01, 0x85, 0xB2]
        self.sc.write(cmd)
        print(self.readSerial())

    # 夹持状态反馈
    def clampState(self):
        cmd = [0x01, 0x03, 0x02, 0x01, 0x00, 0x01, 0xD4, 0x72]
        self.sc.write(cmd)
        back = self.readSerial()
        print(back)
        back = self.readSerial()
        divBack = str(back).split("\\x")
        state = int(divBack[-3].encode(), 16)
        print(state)

    # IO开关
    def IOSwitch(self, mode):
        cmd = [0x01, 0x06, 0x04, 0x02, 0x00, 0x00, 0x29, 0x3A]
        self.sc.write(cmd)
        back = self.readSerial()

    # 设置相对旋转位置
    def setRelativeRotation(self, Rotation):
        if Rotation < 0:
            RotationHex = hex(Rotation)
            if RotationHex.__len__() <= 5:
                array = [0x01, 0x06, 0x01, 0x09, 0x00, Rotation]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x09, 0x00, Rotation, currentRotationQ, currentRotationH]
            else:
                RotationHex = hex(Rotation)
                RotationHexQ = int(RotationHex[0] + RotationHex[1] + RotationHex[2] + RotationHex[3], 16) - 1
                RotationHexH = int(RotationHex[0] + RotationHex[1] + RotationHex[2] + RotationHex[-2] + RotationHex[-1],
                                   16) - 1
                array = [0x01, 0x06, 0x01, 0x09, RotationHexQ, RotationHexH]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x09, RotationHexQ, RotationHexH, currentRotationQ,
                                  currentRotationH]
        else:
            RotationHex = hex(Rotation)
            if RotationHex.__len__() <= 4:
                array = [0x01, 0x06, 0x01, 0x09, 0x00, Rotation]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x09, 0x00, Rotation, currentRotationQ, currentRotationH]
            else:
                RotationHex = hex(Rotation)
                RotationHexQ = int(RotationHex[0] + RotationHex[1] + RotationHex[2], 16)
                RotationHexH = int(RotationHex[0] + RotationHex[1] + RotationHex[-2] + RotationHex[-1], 16)
                array = [0x01, 0x06, 0x01, 0x09, RotationHexQ, RotationHexH]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x09, RotationHexQ, RotationHexH, currentRotationQ,
                                  currentRotationH]
        self.sc.write(setRotationCmd)
        print(self.readSerial())

    # 设置绝对旋转位置
    def setAbsoluteRotation(self, Rotation):
        if Rotation < 0:
            RotationHex = hex(Rotation)
            if RotationHex.__len__() <= 5:
                array = [0x01, 0x06, 0x01, 0x05, 0x00, Rotation]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x05, 0x00, Rotation, currentRotationQ, currentRotationH]
            else:
                RotationHex = hex(Rotation)
                RotationHexQ = int(RotationHex[0] + RotationHex[1] + RotationHex[2] + RotationHex[3], 16) - 1
                RotationHexH = int(RotationHex[0] + RotationHex[1] + RotationHex[2] + RotationHex[-2] + RotationHex[-1],
                                   16) - 1
                array = [0x01, 0x06, 0x01, 0x05, RotationHexQ, RotationHexH]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x05,
                                  int('0x' + (RotationHexQ.to_bytes(1, byteorder='big', signed=True).hex()), 16),
                                  int('0x' + RotationHexH.to_bytes(1, byteorder='big', signed=True).hex(), 16),
                                  currentRotationQ,
                                  currentRotationH]

        else:
            RotationHex = hex(Rotation)
            if RotationHex.__len__() <= 4:
                array = [0x01, 0x06, 0x01, 0x05, 0x00, Rotation]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x05, 0x00, Rotation, currentRotationQ, currentRotationH]
            else:
                RotationHex = hex(Rotation)
                RotationHexQ = int(RotationHex[0] + RotationHex[1] + RotationHex[2], 16)
                RotationHexH = int(RotationHex[0] + RotationHex[1] + RotationHex[-2] + RotationHex[-1], 16)
                array = [0x01, 0x06, 0x01, 0x05, RotationHexQ, RotationHexH]
                currentRotationQ, currentRotationH = self.calCrc(array)
                setRotationCmd = [0x01, 0x06, 0x01, 0x05, RotationHexQ, RotationHexH, currentRotationQ,
                                  currentRotationH]
        self.sc.write(setRotationCmd)
        print(self.readSerial())

    # 设置旋转速度
    def setRotationVel(self, vel):
        array = [0x01, 0x06, 0x01, 0x07, 0x00, vel]
        crcQ, crcH = self.calCrc(array)
        ForceCmd = [0x01, 0x06, 0x01, 0x07, 0x00, vel, crcQ, crcH]
        self.sc.write(ForceCmd)
        print(self.readSerial())

    # 设置旋转力
    def setRotationForce(self, Force):
        array = [0x01, 0x06, 0x01, 0x08, 0x00, Force]
        crcQ, crcH = self.calCrc(array)
        ForceCmd = [0x01, 0x06, 0x01, 0x08, 0x00, Force, crcQ, crcH]
        self.sc.write(ForceCmd)
        print(self.readSerial())


if __name__ == "__main__":
    cs = ComSwitch()
    cs.InitFinger()
    time.sleep(0.2)
    for i in tqdm(range(1000)):
        # cs.setForce(100)
        cs.setAbsoluteRotation(-360)
        time.sleep(1)
        # cs.setPosition(300)
        # cs.setForce(20)
        cs.setAbsoluteRotation(360)
        time.sleep(1)
