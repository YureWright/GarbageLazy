import tempfile

from flask import Flask, jsonify, render_template, request

from classify import PRICE_PER_KG, calculate_reward, classify_image
from tranC import ServoFlipController, handle_garbage

app = Flask(__name__)

# 前端分类 → tranC 分类 映射
FRONTEND_TO_TRANC = {
    "可回收物": "可回收垃圾",
    "有害垃圾": "有害垃圾",
    "厨余垃圾": "厨余垃圾",
    "其他垃圾": "其他垃圾",
}

# 串口舵机控制器（全局单例）
try:
    CONTROLLER = ServoFlipController(port="COM9")
    print("[app] 舵机控制器已连接")
except Exception as e:
    CONTROLLER = None
    print(f"[警告] 舵机控制器初始化失败: {e}")


@app.route("/")
def index():
    """宣传海报页，作为系统入口"""
    return render_template("promo.html")


@app.route("/app")
def app_index():
    """主应用"""
    return render_template("index.html")


@app.route("/promo")
def promo():
    """宣传落地页（直达）"""
    return render_template("promo.html")


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


@app.route("/api/put", methods=["POST"])
def api_put():
    """投入垃圾：调用 tranC.handle_garbage 翻转对应分类的舵机"""
    category = request.get_json(force=True).get("category", "")
    tranc_cat = FRONTEND_TO_TRANC.get(category)
    if not tranc_cat:
        return jsonify({"error": f"未知分类: {category}"}), 400
    if CONTROLLER is None:
        return jsonify({"error": "舵机控制器未连接，请检查串口"}), 500
    try:
        handle_garbage(tranc_cat, CONTROLLER)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True})


if __name__ == "__main__":
    # use_reloader=False：禁用自动重载，避免双进程争抢串口导致 COM9 打开失败
    app.run(debug=True, port=5000, use_reloader=False)
