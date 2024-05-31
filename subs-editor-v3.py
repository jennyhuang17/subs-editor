import os
from funcslibs import csv_to_srt, srt_to_csv, process_csv

with open('welcome.txt', 'r') as file:
	welcome_msg = file.read()
print(welcome_msg)

while True:
	option = input('请输入要进行的操作前的数字（或输入“tc”来退出程序）：')

	if option.lower() == 'tc':
		print('已退出')
		break

	if option == '1':
		# Read the input file
		input_name = input('请先将文件存在“原始srt”文件夹下，输入srt文件名称（不带后缀）：')
		input_dir = '1原始字幕'
		input_path = os.path.join(input_dir, f'{input_name}.srt')

		# The output name is the same as the input
		output_name = input_name
		output_dir = '1无角色csv'
		# Ensure the output directory exists
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		output_path = os.path.join(output_dir, f'{output_name}.csv')

		# Run the srt to csv converter
		srt_to_csv(input_path, output_path)
		print('已成功创建csv文件！')

	elif option == '2':
		# Read the input file
		input_name = input('请先将文件存在“已标记角色csv”文件夹下，输入srt文件名称（不带后缀）：')
		input_dir = '2有角色csv'
		input_path = os.path.join(input_dir, f'{input_name}.csv')
		transformed_input_path = os.path.join(input_dir, f'{input_name}_transformed.csv')

		# The output name is the same as the input
		output_name = input_name
		output_dir = '砍柴用字幕'
		# Ensure the output directory exists
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		output_path = os.path.join(output_dir, f'{output_name}.srt')

		process_csv(input_path, transformed_input_path)
		csv_to_srt(transformed_input_path, output_path)
		os.remove(transformed_input_path)
		print('已成功创建根据角色整理的srt文件！')

		

