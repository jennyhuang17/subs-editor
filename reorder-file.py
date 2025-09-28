import os

def rename_mp3_files(root_folder):
    # 遍历 A/01, A/02, ...
    for folder in sorted(os.listdir(root_folder)):
        subfolder_path = os.path.join(root_folder, folder)
        if not os.path.isdir(subfolder_path):
            continue
        
        print(f"正在处理文件夹: {subfolder_path}")
        
        # 获取所有 mp3 文件
        mp3_files = [f for f in os.listdir(subfolder_path) if f.endswith(".mp3")]
        mp3_files.sort()  # 按原始文件名排序（可以换成 os.listdir 的自然顺序）

        # 重新编号
        for idx, filename in enumerate(mp3_files, start=1):
            old_path = os.path.join(subfolder_path, filename)

            # 拆分出 "内容" 部分
            try:
                # 原命名格式 "01-020 内容.mp3"
                parts = filename.split(" ", 1)
                if len(parts) < 2:
                    print(f"⚠️ 文件名格式不符合预期: {filename}")
                    continue
                header, content = parts
                # header = "01-020"
                episode = header.split("-")[0]
            except Exception as e:
                print(f"⚠️ 解析出错: {filename} - {e}")
                continue

            new_number = f"{idx:03d}"  # 三位编号
            new_filename = f"{episode}-{new_number} {content}"
            new_path = os.path.join(subfolder_path, new_filename)

            # 重命名
            os.rename(old_path, new_path)
            print(f"{filename}  →  {new_filename}")

    print("✅ 重命名完成！")

if __name__ == "__main__":
    rename_mp3_files("output-audio")
