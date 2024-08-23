# 这是一个向DaHuan夹爪发送命令的程序，由Frank创建。
import serial  # 导入串口通信库
import time  # 导入时间库，用于控制延时
import crcmod  # 导入crcmod库，用于计算校验和
import random  # 导入random模块
from ControlRoot import ControlRoot


# 定义函数检查值是否在指定范围内
def check_range(value, min_value, max_value):
    if not min_value <= value <= max_value:
        raise RuntimeError('Out of range')  # 如果值不在范围内，抛出异常


# 定义SetCommand类，用于设置夹爪的命令
class SetCommand(object):
    def __init__(self, control_instance=ControlRoot()):
        self.gripper = control_instance  # 初始化ControlInstance并赋值给gripper

    # 初始化夹爪
    def initialize_gripper(self,blocking=True):
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x00, value=165)  # 发送初始化命令
        if blocking:
            # 阻塞模式：等待位置到达目标值
            while True:
                current_status = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x00,
                                                             is_set=False)
                if current_status == 1:
                    break
                time.sleep(0.01)  # 小延时以防止过度占用CPU
    # 设置力值
    def set_force(self, value):
        check_range(value, 20, 100)  # 检查力值是否在20到100之间
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x01, value=value)  # 发送力值命令

    # 设置位置
    def set_position(self, value, blocking=True):
        check_range(value, 0, 1000)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x03, value=value)

        if blocking:
            # 阻塞模式：等待位置到达目标值
            while True:
                current_position = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x02,
                                                             is_set=False)
                if current_position == value:
                    break
                time.sleep(0.01)  # 小延时以防止过度占用CPU
                self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x03, value=value)
        else:
            time.sleep(0.5)

    # 设置速度
    def set_velocity(self, value):
        check_range(value, 0, 1000)  # 检查速度值是否在0到1000之间
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x04, value=value)  # 发送速度命令

    # 设置绝对旋转角度
    def set_absolute_rotation(self, value):
        check_range(value, -32768, 32767)  # 检查角度值是否在-32768到32767之间
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x05, value=value,
                                  read_response=False)  # 发送绝对旋转角度命令

    # 设置旋转速度
    def set_rotation_velocity(self, value):
        check_range(value, 1, 100)  # 检查旋转速度值是否在1到100之间
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x07, value=value,
                                  read_response=False)  # 发送旋转速度命令

    # 设置旋转力值
    def set_rotation_force(self, value):
        check_range(value, 20, 100)  # 检查旋转力值是否在20到100之间
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x08, value=value)  # 发送旋转力值命令

    # 设置相对旋转角度
    def set_relative_rotation(self, value):
        check_range(value, -32768, 32767)  # 检查相对旋转角度值是否在-32768到32767之间
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x09, value=value)  # 发送相对旋转角度命令

    # 初始化反馈处理
    def initialize_feedback(self):
        response = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x00,
                                             is_set=False)  # 发送初始化反馈命令
        while response == 0:
            self.initialize_gripper()  # 如果反馈为0，重新初始化
            response = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x00,
                                                 is_set=False)  # 再次发送反馈命令
        while response == 2:
            time.sleep(0.1)  # 等待0.1秒
            response = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x00,
                                                 is_set=False)  # 再次发送反馈命令


# 读取状态的类
class ReadStatus(object):
    def __init__(self, control_instance=ControlRoot()):
        self.gripper = control_instance  # 初始化ControlInstance并赋值给gripper

    # 读取旋转角度
    def read_rotation_angle(self):
        response = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x08,
                                             is_set=False)  # 发送读取旋转角度命令
        print(response)  # 打印反馈值


if __name__ == "__main__":
    control_root = ControlRoot()  # 创建ControlRoot实例

    set_command = SetCommand(control_root)  # 创建SetCommand实例
    read_status = ReadStatus(control_root)  # 创建ReadStatus实例
    set_command.initialize_gripper()  # 初始化夹爪

    # 100次循环实验
    for i in range(2):
        random_position = random.randint(0, 1000)  # 生成0到1000之间的随机位置
        print(f"实验 {i + 1} 次 - 设置随机位置为 {random_position}")
        set_command.set_position(random_position, blocking=True)  # 设置随机位置并等待到达
