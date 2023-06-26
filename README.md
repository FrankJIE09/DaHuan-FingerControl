# DaHuan手爪控制
## 项目说明
这个项目包含了机械臂夹爪控制的相关代码，本文件夹下包含两个主要的Python文件`ControlGripper.py`和`ControlRoot.py`。

>* ControlGripper.py: 控制机械臂夹爪姿态，执行操作。
>* ControlRoot.py: 通过串口通讯和crc校验，发送和读取机械臂控制命令和返回值。
## Setup
### 硬件要求
>* DaHuan手爪
>* 串口通讯设备
### 软件要求
>*    Python 2.x 或 Python 3.x
>*    ubuntu
### 配置
#### 打开串口权限
>sudo chmod 777 /dev/ttyUSB0 
> 
>sudo usermod -aG　dialout {userName}
> 
> reboot
#### 安装必要项
>* pip install crcmod
>* pip install pyserial
## 使用

>* 确保硬件设备正确连接，串口通讯端口正确设置。
>*    运行ControlGripper.py程序。测试运行。
>*    根据实际需求，调用相关的命令实现夹爪控制。

![img.png](pdfInfor/img.png)
![img_1.png](pdfInfor/img_1.png)

上表功能一一对应[DaHuanFinger.py](/ControlRoot.py)中SetCmd中函数。
