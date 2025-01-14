# 这是一个向DaHuan夹爪发送命令的程序，由Frank创建。
import serial  # 导入串口通信库
import time  # 导入时间库，用于控制延时
import crcmod  # 导入crcmod库，用于计算校验和
import random  # 导入random模块
from ControlRoot import ControlRoot  # 导入ControlRoot模块


def check_range(value, min_value, max_value):
    """
    检查值是否在指定范围内。

    参数：
        value (int/float): 要检查的值。
        min_value (int/float): 最小值。
        max_value (int/float): 最大值。

    抛出：
        RuntimeError: 如果值不在指定范围内。
    """
    if not min_value <= value <= max_value:
        raise RuntimeError('Out of range')


class SetCommand:
    """
    定义SetCommand类，用于控制DaHuan夹爪。
    """

    def __init__(self, control_instance):
        """
        初始化SetCommand对象。

        参数：
            control_instance (ControlRoot): 夹爪控制实例。
        """
        self.gripper = control_instance

    def initialize_gripper(self, blocking=True):
        """
        初始化夹爪。

        参数：
            blocking (bool): 是否阻塞等待初始化完成。

        功能：
            - 发送初始化命令。
            - 阻塞模式下等待夹爪完成初始化。
        """
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x00, value=165)
        if blocking:
            while True:
                current_status = self.gripper.send_command(
                    modbus_high_address=0x02, modbus_low_address=0x00, is_set=False
                )
                if current_status == 1:
                    break
                time.sleep(0.01)

    def set_force(self, value):
        """
        设置夹爪的力值。

        参数：
            value (int): 力值，范围为20-100。

        地址：
            - 写入地址：0x0101
        """
        check_range(value, 20, 100)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x01, value=value)

    def set_position(self, value, blocking=True):
        """
        设置夹爪的位置。

        参数：
            value (int): 目标位置，范围为0-1000。
            blocking (bool): 是否阻塞等待夹爪到达位置。

        地址：
            - 写入地址：0x0103
            - 读取地址：0x0202
        """
        check_range(value, 0, 1000)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x03, value=value)
        if blocking:
            while True:
                current_position = self.gripper.send_command(
                    modbus_high_address=0x02, modbus_low_address=0x02, is_set=False
                )
                if current_position == value:
                    break
                time.sleep(0.01)

    def set_velocity(self, value):
        """
        设置夹爪的速度。

        参数：
            value (int): 速度值，范围为0-1000。

        地址：
            - 写入地址：0x0104
        """
        check_range(value, 0, 1000)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x04, value=value)
    def set_absolute_rotation(self, value, blocking=True, tolerance=5):
        """
        设置绝对旋转角度。

        参数：
            value (int): 目标绝对旋转角度，范围为-32768*160 ~ 32767*160。
            blocking (bool): 是否阻塞等待旋转完成。
            tolerance (int): 允许的误差范围。

        地址：
            - 写入低位地址：0x0105
            - 写入高位地址：0x0106
            - 读取状态地址：0x020B
        """
        # 检查输入角度范围
        check_range(value, -32768 * 160, 32767 * 160)

        # 处理低位和高位，并根据正负值调整
        if value < 0:
            low_value = value % -32768  # 低位值
            high_value = value // -32768  # 高位值
        else:
            low_value = value % 32768  # 低位值
            high_value = value // 32768  # 高位值
        # 发送低位绝对旋转角度命令
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x05, value=low_value,
                                  read_response=False)

        # 发送高位绝对旋转角度命令
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x06, value=high_value,
                                  read_response=False)

        if blocking:
            # 阻塞模式：等待位置到达目标值或操作完成
            while True:
                # 读取旋转状态反馈
                rotation_status = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x0B,
                                                            is_set=False)
                if rotation_status == 1:  # 到达位置
                    break
                elif rotation_status == 2:  # 旋转卡住
                    raise Exception("Rotation is stuck")

                time.sleep(0.1)  # 小延时以防止过度占用CPU

        else:
            pass

    def stop_rotation(self):
        """
        停止夹爪的旋转。

        地址：
            - 写入地址：0x0502
        """
        self.gripper.send_command(modbus_high_address=0x05, modbus_low_address=0x02, value=1, read_response=True)

    def get_gripper_status(self):
        """
        获取夹爪的当前状态。

        地址：
            - 读取地址：0x0201

        返回值：
            - 0: 夹爪处于正在运动状态。
            - 1: 夹爪停止运动，且未检测到实物。
            - 2: 夹爪停止运动，且检测到实物。
            - 3: 检测到实物体掉落。
        """
        status = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x01, is_set=False)
        if status not in [0, 1, 2, 3]:
            raise ValueError(f"Unexpected status value: {status}")
        return status

    def set_rotation_speed(self, speed):
        """
        设置夹爪的旋转速度。

        参数：
            speed (int): 旋转速度，范围为1-100。

        地址：
            - 写入地址：0x0107
        """
        check_range(speed, 1, 100)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x07, value=speed, read_response=False)

    def set_rotation_torque(self, torque):
        """
        设置夹爪的旋转力。

        参数：
            torque (int): 旋转力值，范围为20-100。

        地址：
            - 写入地址：0x0108
        """
        check_range(torque, 20, 100)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x08, value=torque, read_response=False)

    def set_relative_rotation(self, angle, blocking=True, tolerance=5):
        """
        设置夹爪的相对旋转角度。

        参数：
            angle (int): 相对旋转角度，范围为-32768 ~ 32767。
            blocking (bool): 是否阻塞等待旋转完成。
            tolerance (int): 允许的误差范围。

        地址：
            - 写入地址：0x0109
            - 读取状态地址：0x020B
        """
        check_range(angle, -32768, 32767)
        self.gripper.send_command(modbus_high_address=0x01, modbus_low_address=0x09, value=angle, read_response=False)
        if blocking:
            while True:
                rotation_status = self.gripper.send_command(
                    modbus_high_address=0x02, modbus_low_address=0x0B, is_set=False
                )
                if rotation_status == 1:
                    break
                elif rotation_status == 2:
                    raise Exception("Rotation is stuck")
                time.sleep(0.1)

    def initialize_feedback(self):
        """
        处理夹爪的初始化反馈。

        地址：
            - 读取地址：0x0200
        """
        response = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x00, is_set=False)
        while response == 0:
            self.initialize_gripper()
            response = self.gripper.send_command(modbus_high_address=0x02, modbus_low_address=0x00, is_set=False)
        while response == 2:
            time.sleep(0.1)


if __name__ == "__main__":
    control_root = ControlRoot()
    set_command = SetCommand(control_root)

    set_command.initialize_gripper()
    set_command.set_rotation_torque(20)
    set_command.set_rotation_speed(1)

    for i in range(100):
        random_position = random.randint(0, 1000)
        print(f"实验 {i + 1} 次 - 设置随机位置为 {random_position}")
        set_command.set_position(random_position, blocking=True)

        random_rotation = random.randint(-100, 100)
        print(f"实验 {i + 1} 次 - 设置随机相对旋转位置为 {random_rotation}")
        set_command.set_relative_rotation(random_rotation)

        print(f"实验 {i + 1} 次 - 设置随机绝对旋转位置为 {random_rotation}")
        set_command.set_absolute_rotation(random_rotation)
