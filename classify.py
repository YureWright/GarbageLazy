import base64
import json
import sys
from pathlib import Path
from config import API_KEY, MODEL
from openai import OpenAI

# 替换为你的阿里云百炼 API Key

# 读取 skill 文件作为 system prompt
SKILL_PATH = Path(__file__).parent / "skill" / "SKILL.md"
SYSTEM_PROMPT = SKILL_PATH.read_text(encoding="utf-8")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def classify_image(image_path: str) -> list:
    """输入本地图片路径，返回垃圾分类结果列表，每个元素含 name/category/advice"""
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    completion = client.chat.completions.create(
        model="MODEL",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                    {"type": "text", "text": "请识别图片中的垃圾并按 JSON 格式输出分类结果。"},
                ],
            },
        ],
    )

    text = completion.choices[0].message.content.strip()
    # 去掉可能的 markdown 代码块包裹
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


# 每公斤垃圾分类奖励价格（元）
PRICE_PER_KG = {
    "可回收物": 0.4,
    "有害垃圾": 0.3,
    "厨余垃圾": 0.15,
    "其他垃圾": 0.02,
}


def calculate_reward(category: str, weight_kg: float) -> float:
    """输入垃圾类型和重量（公斤），返回垃圾分类奖励金额（元）"""
    if category not in PRICE_PER_KG:
        raise ValueError(f"未知垃圾类型: {category}，应为 {list(PRICE_PER_KG)} 之一")
    return round(PRICE_PER_KG[category] * weight_kg, 2)


if __name__ == "__main__":
    result = classify_image(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
