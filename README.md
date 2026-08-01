# 垃圾分类识别系统

调用视觉大模型（qwen-vl-max）识别图片中的垃圾，进行四分类（可回收物/有害垃圾/厨余垃圾/其他垃圾），并根据重量计算垃圾分类奖励。

## 功能

- 摄像头拍照识别 / 上传图片识别（支持拖拽、多轮追加）
- 识别结果可修改分类、标注重量、删除、手动补录
- 按每公斤价格计算垃圾分类总价值

## 项目结构

```
├── classify.py          # 核心模块：classify_image() 图像识别、calculate_reward() 价值计算
├── app.py               # Flask 后端接口
├── camera_app.py        # 桌面版摄像头识别（tkinter）
├── example.py           # 命令行调用示例
├── requirements.txt     # 依赖
├── skill/
│   └── SKILL.md         # 垃圾分类专家 skill（作为 system prompt 传入模型）
├── templates/
│   └── index.html       # Web 前端（四步流程）
└── 测试图片/             # 测试用图片
```

## 安装

```powershell
pip install -r requirements.txt
```

在 [classify.py](classify.py) 中将 `API_KEY` 替换为你的阿里云百炼 API Key。

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

## 函数接口

```python
from classify import classify_image, calculate_reward

# 图像识别：输入图片路径，返回垃圾列表 [{"name", "category", "advice"}, ...]
results = classify_image("test.jpg")

# 价值计算：输入分类和重量（kg），返回奖励金额（元）
reward = calculate_reward("可回收物", 2.5)  # 1.0
```

## 定价（每公斤）

| 分类 | 价格 |
|------|------|
| 可回收物 | ¥0.4 |
| 有害垃圾 | ¥0.3 |
| 厨余垃圾 | ¥0.15 |
| 其他垃圾 | ¥0.02 |
