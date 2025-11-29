import os

def extract_content_from_filename(filename):
    # 文件名格式示例: "21-001 这位兄弟没见过啊 不介绍一下.mp3"
    if filename.lower().endswith(".mp3"):
        name_without_ext = os.path.splitext(filename)[0]
        # 去掉前面的 "21-001 " 部分
        parts = name_without_ext.split(" ", 1)
        if len(parts) == 2:
            return parts[1].strip()
    return None

def main(root_dir, output_file):
    # 获取所有子文件夹并按数字顺序排序
    subfolders = sorted([f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))])

    with open(output_file, "w", encoding="utf-8") as out:
        for folder in subfolders:
            folder_path = os.path.join(root_dir, folder)
            # 写子文件夹标题
            out.write(folder + "\n")

            # 获取该子文件夹里的所有 mp3 文件，按编号排序
            mp3_files = sorted(os.listdir(folder_path))

            for mp3 in mp3_files:
                content = extract_content_from_filename(mp3)
                if content:
                    out.write("◦ " + content + "\n")

            # 每个子文件夹之间空一行
            out.write("\n")

if __name__ == "__main__":
    root_directory = "骆为昭/"  # TODO: 修改成你的根目录路径
    output_txt = "骆为昭.txt"
    main(root_directory, output_txt)
    print("完成！已生成", output_txt)
