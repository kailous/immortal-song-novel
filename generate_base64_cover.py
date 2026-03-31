import os
import base64
import sys
import json

base_dir = "/Users/lipeng/Documents/Repository/ceshi new"
book_info_path = os.path.join(base_dir, "book_info.json")

cover_filename = "my_real_cover.jpg"
output_filename = "title.cover"
if os.path.exists(book_info_path):
    with open(book_info_path, "r", encoding="utf-8") as f:
        try:
            info = json.load(f)
            if "cover_image" in info:
                cover_filename = info["cover_image"]
            if "cover_image_base64" in info:
                output_filename = info["cover_image_base64"]
        except Exception as e:
            print(f"⚠️ 读取 book_info.json 失败: {e}")

input_jpg = os.path.join(base_dir, cover_filename)
output_cover = os.path.join(base_dir, output_filename)

if not os.path.exists(input_jpg):
    print(f"❌ 查无此图: {cover_filename}。请确认图片名称并与 book_info.json 保持一致。")
    sys.exit(1)

print(f"🚀 正在提取图片 {cover_filename} 的原生特征，准备输出为 {output_filename}...")
with open(input_jpg, "rb") as f_in:
    binary_data = f_in.read()
    
# 将图片转换为 base64 文本
b64_string = base64.b64encode(binary_data).decode('utf-8')

# 在最前面强行加上带换行符的中文干扰头
obfuscated_content = "cover封面文件\n" + b64_string

with open(output_cover, "w", encoding="utf-8") as f_out:
    f_out.write(obfuscated_content)

print(f"✅ 加密成功！已生成带抗检测首行的安全文本文件: {output_cover}")

# 自动销毁原图，彻底隐藏工作痕迹
try:
    os.remove(input_jpg)
    print(f"🧹【阅后即焚】：原版高清无码图 {cover_filename} 已经从硬盘中自动粉碎销毁！")
except Exception as e:
    print(f"⚠️ 无法自动删除图片: {e}")

print(f"👍 万事俱备，您可以放心地一键打包 EPUB 了。")
