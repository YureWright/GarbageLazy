import tempfile

from flask import Flask, jsonify, render_template, request

from classify import PRICE_PER_KG, calculate_reward, classify_image

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/classify", methods=["POST"])
def api_classify():
    """上传图片识别"""
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "未上传图片"}), 400
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    file.save(tmp.name)
    try:
        results = classify_image(tmp.name)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reward", methods=["POST"])
def api_reward():
    """计算垃圾分类总价值，输入: [{"category": ..., "weight": ...}, ...]"""
    items = request.get_json(force=True).get("items", [])
    details, total = [], 0.0
    for item in items:
        try:
            reward = calculate_reward(item["category"], float(item["weight"]))
        except (ValueError, KeyError) as e:
            return jsonify({"error": str(e)}), 400
        details.append({**item, "reward": reward})
        total += reward
    return jsonify({"details": details, "total": round(total, 2)})


@app.route("/api/prices")
def api_prices():
    """返回每公斤价格表，供前端展示"""
    return jsonify(PRICE_PER_KG)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
