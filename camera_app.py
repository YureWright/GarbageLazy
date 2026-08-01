import json
import tempfile
import tkinter as tk

import cv2
from PIL import Image, ImageTk

from classify import classify_image


class CameraApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("垃圾分类识别")

        # 打开默认摄像头
        self.cap = cv2.VideoCapture(0)

        # 视频画面显示区域
        self.video_label = tk.Label(root)
        self.video_label.pack()

        # 识别按钮
        self.capture_btn = tk.Button(
            root, text="识别", font=("微软雅黑", 14), command=self.capture
        )
        self.capture_btn.pack(pady=5)

        # 识别结果显示区域
        self.result_text = tk.Text(root, height=10, font=("微软雅黑", 10))
        self.result_text.pack(fill="x", padx=10, pady=5)

        self.update_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        """实时刷新摄像头画面"""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = ImageTk.PhotoImage(Image.fromarray(frame))
            self.video_label.img = image  # 防止被垃圾回收
            self.video_label.config(image=image)
        self.root.after(30, self.update_frame)

    def capture(self):
        """拍照并调用 classify_image 识别"""
        ret, frame = self.cap.read()
        if not ret:
            return
        self.capture_btn.config(state="disabled", text="识别中...")

        # 保存为临时图片文件
        tmp_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        cv2.imwrite(tmp_path, frame)

        try:
            results = classify_image(tmp_path)
            self.show_results(results)
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"识别失败: {e}")
        finally:
            self.capture_btn.config(state="normal", text="识别")

    def show_results(self, results: list):
        self.result_text.delete("1.0", "end")
        for item in results:
            self.result_text.insert(
                "end",
                f"垃圾名称: {item['name']}\n"
                f"垃圾分类: {item['category']}\n"
                f"投放方式: {item['advice']}\n\n",
            )

    def on_close(self):
        self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
