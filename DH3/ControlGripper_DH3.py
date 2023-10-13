#  This is a program to send command to DaHuan grippers. Created by Frank.
import serial
import time
import crcmod
from ControlRoot_DH3 import ControlRoot


def isRange(value, min_, max_):
    if not min_ <= value <= max_:
        raise RuntimeError('Out of range')


class SetCmd(object):
    def __init__(self, ControlInstance=ControlRoot()):
        self.Hand = ControlInstance

    # 初始化夹爪
    def HandInit(self):
        self.Hand.sendCmd(ModbusHighAddress=0x08, ModbusLowAddress=0x01, Value=-1)

    # 力值
    def Force(self, value):
        isRange(value, 10, 90)
        self.Hand.sendCmd(ModbusHighAddress=0x05, ModbusLowAddress=0x02, Value=value)

    # 位置
    def Position(self, value):
        isRange(value, 0, 95)
        self.Hand.sendCmd(ModbusHighAddress=0x06, ModbusLowAddress=0x02, Value=value)

    # 旋转角度
    def angle(self, cmd):
        isRange(cmd, 0, 100)
        self.Hand.sendCmd(ModbusHighAddress=0x07, ModbusLowAddress=0x02, Value=cmd)


if __name__ == "__main__":
    CR = ControlRoot()
    cs = SetCmd(CR)
    cs.Force(10)
    time.sleep(0.2)

    cs.Position(10)
    time.sleep(0.2)

    cs.angle(50)
    time.sleep(2)

    cs.Position(95)
    time.sleep(0.2)

    cs.angle(0)
    time.sleep(0.2)
