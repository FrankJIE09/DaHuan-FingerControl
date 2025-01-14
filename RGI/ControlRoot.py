# 这是一个读取和发送命令的程序，由Frank创建。

import serial  # 导入串口通信库
import time    # 导入时间库，用于控制延时
import crcmod  # 导入crcmod库，用于计算CRC校验码

# 定义ControlRoot类，用于管理串口通信
class ControlRoot(object):
    # 初始化串口
    def __init__(self, port="COM3"):
        self.serial_conn = serial.Serial(port=port, baudrate=115200,timeout=1)  # 打开串口，设置波特率为115200
        self.crc16_func = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)  # 初始化CRC16校验函数

    # 计算CRC校验码
    def calculate_crc(self, data_array):
        data_bytes = b''
        for i in range(len(data_array)):
            data_bytes += data_array[i].to_bytes(1, byteorder='big', signed=True)  # 将每个元素转为字节并拼接
        crc = self.crc16_func(data_bytes).to_bytes(2, byteorder='big', signed=False)  # 计算CRC校验码并转为字节
        crc_high = int.from_bytes(crc[0:1], byteorder='big', signed=False)  # 获取高位字节
        crc_low = int.from_bytes(crc[1:2], byteorder='big', signed=False)  # 获取低位字节
        return crc_low, crc_high

    # 读取串口接收的数据
    def read_serial_data(self):
        time.sleep(0.08)  # 等待0.08秒
        received_data = self.serial_conn.read_all()  # 读取所有串口数据
        return received_data

    # 发送指令
    def send_command(self, modbus_high_address, modbus_low_address, value=0x01, is_set=True, read_response=True):
        if is_set:
            command_type = 0x06  # 设置操作的命令码
        else:
            command_type = 0x03  # 读取操作的命令码

        value = value if value >= 0 else value - 1  # 处理负数值
        value_bytes = value.to_bytes(2, byteorder='big', signed=True)  # 将Value转换为两个字节
        value_high = int.from_bytes(value_bytes[0:1], byteorder='big', signed=True)  # 高位字节
        value_low = int.from_bytes(value_bytes[1:2], byteorder='big', signed=True)  # 低位字节

        command_array = [0x01, command_type, modbus_high_address, modbus_low_address, value_high, value_low]  # 构建命令数组
        crc_low, crc_high = self.calculate_crc(command_array)  # 计算CRC校验码
        full_command = [0x01, command_type, modbus_high_address, modbus_low_address, value_high, value_low, crc_low, crc_high]  # 构建完整命令

        for i in range(len(full_command)):
            full_command[i] = full_command[i] if full_command[i] >= 0 else full_command[i] + 256  # 处理负数值

        self.serial_conn.write(full_command)  # 发送命令到串口

        if read_response:
            response = self.read_serial_data()  # 读取串口返回的数据
            response_value = int.from_bytes(response[3:5], byteorder='big', signed=True)  # 从返回数据中获取值
            if response_value < 0:
                response_value += 1  # 处理负数值
            self.serial_conn.flush()  # 清空串口接收缓存
            return response_value
        else:
            time.sleep(0.01)  # 等待0.005秒
            return
