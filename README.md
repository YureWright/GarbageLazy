# 你是什么垃圾

> **智能识别 · 精准分类 · 循环价值** —— 基于视觉大模型的垃圾分类与价值回馈系统

## 简介

**"你是什么垃圾"** 是一套集 **视觉识别、四分类、价值测算、自动投放** 于一体的垃圾分类智能系统。

只需对垃圾拍一张照片，系统就会调用视觉大模型（qwen-vl-max）自动识别垃圾名称、判定所属分类（可回收物 / 有害垃圾 / 厨余垃圾 / 其他垃圾），并给出正确的投放方式。确认重量后，系统会按分类单价计算垃圾的回收价值；点击"投入"，还可联动开发板上的舵机，将对应分类的垃圾桶盖自动打开，完成一次完整的"识别 → 分类 → 投放 → 计价"闭环。

我们想用 AI 让垃圾分类不再困扰每一个人——让资源回到资源，让废弃止步于此。

## 功能特性

- 📷 **多方式识别**：摄像头拍照识别 / 上传图片识别（支持拖拽、多轮追加）
- 🤖 **AI 精准分类**：视觉大模型识别垃圾名称、四分类判定与投放建议
- 🧮 **价值测算**：按分类每公斤单价计算垃圾分类总价值
- 🦾 **舵机自动投入**：点击"投入"，开发板舵机自动打开对应分类的桶盖（支持 4 个分类，引脚可配置）
- ✏️ **人工修正**：识别结果可修改分类、标注重量、删除、手动补录
- 🎨 **现代交互 UI**：响应式环保主题界面（RE:EARTH 风格），动效细腻，移动端友好

## 项目结构

```
├── app.py               # Flask 后端接口（含 /api/put 舵机投入接口）
├── classify.py          # 核心模块：classify_image() 图像识别、calculate_reward() 价值计算
├── tranC.py             # 舵机串口控制器：ServoFlipController、handle_garbage()
├── config.py            # API 配置（API_KEY、MODEL）
├── camera_app.py        # 桌面版摄像头识别（tkinter）
├── example.py           # 命令行调用示例
├── requirements.txt     # 依赖
├── servo_control.py     # 舵机串口控制函数（command 行/脚本调用）
├── servo_test.py        # 舵机测试脚本（让舵机来回摆动验证）
├── servo_diag.py        # 舵机故障诊断脚本
├── hardware_connection.md  # 硬件连接图与排查清单
├── skill/
│   └── SKILL.md         # 垃圾分类专家 skill（作为 system prompt 传入模型）
├── static/
│   └── images/          # 前端静态资源
└── templates/
    └── index.html       # Web 前端（四步流程 + 投入操作）
```

## 安装

```powershell
pip install -r requirements.txt
```

在 [config.py](config.py) 中填入你的阿里云百炼 API Key：

```python
API_KEY = "sk-你的密钥"
MODEL = "qwen-vl-max"
```

## 使用

**Web 应用（推荐）：**

```powershell
python app.py
```

浏览器访问 http://127.0.0.1:5000/

**命令行调用：**

```powershell
python example.py
```

**桌面摄像头应用：**

```powershell
python camera_app.py
```

## 舵机硬件接入

系统支持通过串口控制开发板舵机，实现垃圾自动投入：

| 分类 | 开发板引脚 |
|------|-----------|
| 可回收垃圾 | GPIO 4 |
| 不可回收垃圾 | GPIO 20 |
| 厨余垃圾 | GPIO 29 |
| 有害垃圾 | GPIO 48 |

- 固件工程位于 `esp32_servo/`（ESP32-P4 / ESP-IDF），烧录后在串口等待 `<通道> <open|close>` 命令
- Python 侧通过 [tranC.py](tranC.py) 的 `ServoFlipController` 与开发板通信
- 接线与排查详见 [hardware_connection.md](hardware_connection.md)

## 函数接口

```python
from classify import classify_image, calculate_reward

# 图像识别：输入图片路径，返回垃圾列表 [{"name", "category", "advice"}, ...]
results = classify_image("test.jpg")

# 价值计算：输入分类和重量（kg），返回奖励金额（元）
reward = calculate_reward("可回收物", 2.5)  # 1.0
```

```python
from servo_control import control_servo

# 串口控制开发板舵机开关（channel 1~4，action "open"/"close"）
control_servo(1, "open")
```

## 定价（每公斤）

| 分类 | 价格 |
|------|------|
| 可回收物 | ¥0.4 |
| 有害垃圾 | ¥0.3 |
| 厨余垃圾 | ¥0.15 |
| 其他垃圾 | ¥0.02 |

## 后端接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/api/classify` | POST | 上传图片识别垃圾（multipart 表单，字段 `image`） |
| `/api/reward` | POST | 计算分类价值（JSON：`{"items": [{"category", "weight"}]}`） |
| `/api/prices` | GET | 返回每公斤价格表 |
| `/api/put` | POST | 投入垃圾，触发舵机（JSON：`{"category": "可回收物"}`） |
