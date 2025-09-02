import pandas as pd
import numpy as np

fname = input('目前只支持单人台词，请输入csv文件名称（不带后缀）：')
option = input('1.csv转txt（台词本）\n2.csv转srt（砍音频）\n请选择操作：')

fn = fname + '.csv'
subs = pd.read_csv(fn, header=None)
subs_arr = np.array(subs)

if option == '1':
    csv_to_txt_list = list()
    cp_ls = list()
    for row in range(subs_arr.shape[0]):
        cp_ls.append(subs_arr[row][0])
        if row == 0:
            csv_to_txt_list.append(subs_arr[row][2])
        else:
            diff = cp_ls[row] - cp_ls[row-1]
            if diff == 1:
                csv_to_txt_list.append(' ')
            else:
                csv_to_txt_list.append('\n')
            csv_to_txt_list.append(subs_arr[row][2])
    ftxt = fname + '.txt'
    f1 = open(ftxt, 'w')
    csv_to_txt_list = ''.join(csv_to_txt_list)
    f1.write(csv_to_txt_list)
    f1.close()
    print('台词本已生成！')

if option == '2':
    csv_to_srt_list = list()
    for row in range(subs_arr.shape[0]):
        csv_to_srt_list.append(str(row+1))
        csv_to_srt_list.append('\n')
        csv_to_srt_list.append(subs_arr[row][1])
        csv_to_srt_list.append('\n')
        csv_to_srt_list.append(subs_arr[row][2])
        csv_to_srt_list.append('\n\n')
    fsrt = fname + '.srt'
    f2 = open(fsrt, 'w')
    csv_to_srt_list = ''.join(csv_to_srt_list)
    f2.write(csv_to_srt_list)
    f2.close()
    print('字幕文件已生成！')
