from subsgen import extract_srt_lines
import os

ep_name = input("剧名： ")
ep_start = input("开始集数： ")
ep_end = input("结束集数： ")

while True:
    char_name = input("角色： ")
    # 按关键词生成子srt文件
    if char_name != "":
        for i in range(int(ep_start), int(ep_end)+1):
            input_path = "output-text/srt/"+ep_name+"/"+ep_name+str(i)+".srt"
            output_folder = "output-text/srt/"+char_name
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)
            output_path = output_folder+"/"+char_name+str(i)+".srt"
            print(input_path)
            extract_srt_lines(input_path, output_path, "【"+char_name)
    else:
        break

# # Example usage
# ep_start = 27
# ep_end = 28
# ep_name = "赴山海"
# char_name = "李沉舟"

# for i in range(ep_start, ep_end+1):
#     input_path = "output-text/srt/"+ep_name+"/"+ep_name+str(i)+".srt"
#     output_path = "output-text/srt/"+ep_name+"/"+char_name+str(i)+".srt"
#     extract_srt_lines(input_path, output_path, "【"+char_name)