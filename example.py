from classify import classify_image

# 替换为你的图片路径
results = classify_image("C:\\Users\\86136\\Desktop\\vscode项目\\垃圾识别\\测试图片\\08.jpg")

for item in results:
    print(f"垃圾名称: {item['name']}")
    print(f"垃圾分类: {item['category']}")
    print(f"投放方式: {item['advice']}")
    print()
