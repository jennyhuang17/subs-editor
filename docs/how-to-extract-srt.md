# 如何从mkv视频文件中获得字幕文件？
将mkv内嵌的srt/ass文件提取出来

## Pre-requisites
- mkv格式、内嵌字幕的视频文件
- 安装[MKVToolNix](https://mkvtoolnix.download/downloads.html)
	> 注：mkvtoolnix的作者表示Mac上没有GUI应用，因此mac上用homebrew安装，并通过terminal里的指令交互

## Procedures
1. 运行如下指令获得字幕所在轨道：
	> mkvinfo *<file_name>*.mkv

2. 获得所在轨道信息后，运行以下指令分离字幕文件：
	> mkvextract tracks *<file_name>*.mkv *<track_number>*:*<new_file_name>*.srt

