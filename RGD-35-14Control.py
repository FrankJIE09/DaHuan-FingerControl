'''

'''
import serial
import time
import crcmod
import threading
from tqdm import *
from ControlRoot import ControlRoot


def isRange(value, min_, max_):
    if not min_ <= value <= max_:
        raise RuntimeError('Out of range')


class SetCmd(object):
    def __init__(self, ControlInstance=ControlRoot()):
        self.Hand = ControlInstance

    # 初始化夹爪
    def HandInit(self):
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x00, Value=1)

    # 力值
    def Force(self, value):
        isRange(value, 20, 100)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x01, Value=value)

    # 位置
    def Position(self, value):
        isRange(value, 0, 1000)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x03, Value=value)

    # 速度
    def Velocity(self, value):
        isRange(value, 0, 1000)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x04, Value=value)

    # 绝对旋转角度
    def AbsoluteRotate(self, cmd):
        isRange(cmd, -32768, 32767)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x05, Value=cmd, isReadSerial=False)

    # 旋转速度
    def RotateVelocity(self, value):
        isRange(value, 1, 100)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x07, Value=value, isReadSerial=False)

    # 旋转力值
    def RotateForce(self, value):
        isRange(value, 20, 100)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x08, Value=value)

    # 相对旋转角度
    def RelativeRotate(self, cmd):
        isRange(cmd, -32768, 32767)
        self.Hand.sendCmd(ModbusHighAddress=0x01, ModbusLowAddress=0x09, Value=cmd)

    def InitFeedback(self):
        back = self.Hand.sendCmd(ModbusHighAddress=0x02, ModbusLowAddress=0x00, isSet=False)
        while back == 0:
            self.HandInit()
            back = self.Hand.sendCmd(ModbusHighAddress=0x02, ModbusLowAddress=0x00, isSet=False)
            print(back)
        while back == 2:
            time.sleep(0.1)
            back = self.Hand.sendCmd(ModbusHighAddress=0x02, ModbusLowAddress=0x00, isSet=False)
            print(back)


class ReadStatus(object):
    def __init__(self, ControlInstance=ControlRoot()):
        self.Hand = ControlInstance

    def RTRotateAngle(self):
        back = self.Hand.sendCmd(ModbusHighAddress=0x02, ModbusLowAddress=0x08, isSet=False)
        print(back)


if __name__ == "__main__":
    CR = ControlRoot()
    cs = SetCmd(CR)
    re = ReadStatus(CR)
    cs.HandInit()
    cs.InitFeedback()
    time.sleep(0.2)
    # cs.RotateForce(20)
    cs.RotateVelocity(5)
    time.sleep(0.5)
    setTime = 3
    BTime = time.time()
    num = 0
    while time.time() - BTime < setTime:
        cs.AbsoluteRotate(-200)
        re.RTRotateAngle()
        cs.RelativeRotate(-360)
        re.RTRotateAngle()
        num = num + 1
    print(setTime / (2 * num))
    # cs.setPosition(300)
    # cs.setForce(20)
