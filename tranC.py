import serial
import time

class ServoFlipController:
    """
    Arduino 舵机翻转控制器（通过串口）
    支持引脚：4, 20, 29, 48
    """
    def __init__(self, port='COM9', baudrate=115200, timeout=1):
        """
        初始化串口连接
        :param port: 串口号，Windows 如 'COM9'，Linux 如 '/dev/ttyUSB0'
        :param baudrate: 波特率，需与 Arduino 一致（115200）
        :param timeout: 串口读取超时（秒）
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # 等待 Arduino 复位完成
        print(f"[ServoFlipController] 已连接到 {port}")

    def flip(self, pin):
        """
        翻转指定引脚上的舵机（0° ↔ 180°）
        :param pin: 引脚号，必须为 4, 20, 29, 48 之一
        :return: Arduino 返回的确认信息（字符串）
        """
        if pin not in (4, 20, 29, 48):
            raise ValueError(f"无效引脚号：{pin}，请使用 4, 20, 29 或 48")

        # 发送命令（引脚号 + 换行符）
        cmd = f"{pin}\n"
        self.ser.write(cmd.encode())

        # 读取 Arduino 的反馈（至少两行，直到空或超时）
        responses = []
        while True:
            line = self.ser.readline().decode().strip()
            if not line:
                break
            responses.append(line)
            # 如果读到 "翻转完成" 或 "错误"，跳出
            if "翻转完成" in line or "错误" in line:
                break
        # 合并所有响应
        full_response = "\n".join(responses)
        print(f"[Arduino] {full_response}")
        return full_response

    def close(self):
        """关闭串口连接"""
        self.ser.close()
        print("[ServoFlipController] 串口已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

import time

# 映射字典
GARBAGE_MAP = {
    "可回收垃圾": 4,
    "不可回收垃圾": 20,
    "厨余垃圾": 29,
    "有害垃圾": 48
}

def handle_garbage(garbage_type, controller, hold_seconds=4):
    """
    处理一种垃圾：对应舵机翻转 → 保持 hold_seconds 秒 → 翻转回来
    :param garbage_type: 字符串，如 "可回收垃圾"
    :param controller: ServoFlipController 实例
    :param hold_seconds: 保持翻转状态的时间（秒），默认4秒
    """
    pin = GARBAGE_MAP.get(garbage_type)
    if pin is None:
        print(f"未知垃圾类型：{garbage_type}，可用类型：{list(GARBAGE_MAP.keys())}")
        return

    controller.flip(pin)          # 翻转
    time.sleep(hold_seconds)      # 保持
    controller.flip(pin)          # 翻回
    print(f"{garbage_type} 处理完成\n")

# 创建控制器（确保端口正确）
ctrl = ServoFlipController(port='COM9')

# 处理一种垃圾
handle_garbage("可回收垃圾", ctrl)   # 引脚4翻转，4秒后翻回
handle_garbage("不可回收垃圾", ctrl) # 引脚20翻转，4秒后翻回
# 依次处理...

# 最后关闭连接
ctrl.close()


