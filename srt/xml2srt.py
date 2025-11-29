import os
import xml.etree.ElementTree as ET
import sys

def ms_to_srt_time(ms):
    """毫秒转 SRT 格式时间 (hh:mm:ss,SSS)"""
    ms = int(ms)
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def xml_to_srt(xml_file, srt_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    with open(srt_file, "w", encoding="utf-8") as f:
        for idx, dia in enumerate(root.findall("dia"), start=1):
            st = dia.find("st").text
            et = dia.find("et").text
            sub = dia.find("sub").text.strip()

            start_time = ms_to_srt_time(st)
            end_time = ms_to_srt_time(et)

            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{sub}\n\n")

if __name__ == "__main__":
    folder = "."  # 当前目录，可以改成别的路径
    for file in os.listdir(folder):
        if file.endswith(".xml"):
            xml_path = os.path.join(folder, file)
            srt_path = os.path.splitext(xml_path)[0] + ".srt"
            xml_to_srt(xml_path, srt_path)
            print(f"转换完成: {srt_path}")
