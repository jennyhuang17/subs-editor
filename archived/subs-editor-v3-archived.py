import pandas as pd
import numpy as np

# Created: July 9th, 2024
# Change log:
#   1. 为了简化流程，减少每次输入的次数，取消了从终端中让用户输入文件名和选择功能，而是在程序中写死
#   2. 将生成台词本和生成整合字幕文件打包成了函数，方便后续调用

# 功能1：生成txt台词本
def csv_to_txt(new_fname, subs_arr):
    csv_to_txt_list, idx_ls, name_ls = [list() for i in range(3)]

    for row in range(subs_arr.shape[0]):
            idx_ls.append(subs_arr[row][0]) #存储每一句的编号
            name_ls.append(subs_arr[row][3]) #存储每一句的角色
            char_name = '【' + str(subs_arr[row][3]) + '】' #角色名的新格式

            # 初始化，第一行为：【角色】台词1
            if row == 0:
                csv_to_txt_list.extend([char_name, str(subs_arr[row][2])])

            # 其他情况需考虑：1.前后两行是否是同一角色？2.如为同一角色，前后两行编号是否连续？
            # 若以上两种两况都不满足，则输出文本中需要换行，否则只需加空格，之后再添加新台词
            else:
                diff = idx_ls[row] - idx_ls[row-1]
                if name_ls[row] == name_ls[row-1] and diff == 1:
                    csv_to_txt_list.append(' ')
                else:
                    csv_to_txt_list.extend(['\n', char_name])
                csv_to_txt_list.append(str(subs_arr[row][2]))

    ftxt = 'output-text/txt/' + new_fname + '.txt'
    f1 = open(ftxt, 'w')
    csv_to_txt_list = [str(s).replace('-', '') for s in csv_to_txt_list]
    csv_to_txt_list = ''.join(csv_to_txt_list)
    f1.write(csv_to_txt_list)
    f1.close()
    print(new_fname + '台词本已生成！')

# 功能2：生成按角色整合的字幕文件
def csv_to_compressed_srt(new_fname, subs_arr):
    # 创建新列表来储存标号、角色、每行台词、整合后台词
    # 如果是同一个角色的连贯台词，会先被储存在line_list列表中，待确认下一行不属于本场次的台词，将目前line_list中的台词整合、存储进csv_to_srt_combined_list后，清空line_list列表，用于储存下一场次的台词
    idx_ls, name_ls, line_ls, csv_to_srt_combined_list = [list() for i in range(4)]
    count = 0
    # time_start为每一个场次的第一句台词对应的时间戳，当读取到本场次的最后一句台词时，会将time_start的结束时间更改为最后一句台词对应的结束时间
    time_start = ''

    for row in range(subs_arr.shape[0]):
        idx_ls.append(subs_arr[row][0])
        name_ls.append(subs_arr[row][3])
        char_name = '【' + str(subs_arr[row][3]) + '】'

        if row == 0:
            count = count + 1
            csv_to_srt_combined_list.append(str(count))
            line_ls.extend([char_name, str(subs_arr[row][2])])
            time_start = subs_arr[row][1]

        else:
            diff = idx_ls[row] - idx_ls[row-1]
            # 当处在同一角色、同一场次时，直接往line_ls里添加新的散台词
            if name_ls[row] == name_ls[row-1] and diff == 1:
                line_ls.append(str(subs_arr[row][2]))
            # 剩余情况（同一角色但不同场次，或不同角色），需要将目前line_ls储存进csv_to_srt_combined_list，再清空line_ls
            else:
                t_new_split = time_start.split()
                t_end_split = subs_arr[row-1][1].split()
                t_new_split[2] = t_end_split[2]
                csv_to_srt_combined_list.append(' '.join(t_new_split))
                csv_to_srt_combined_list.append(' '.join(line_ls))

                count = count + 1
                csv_to_srt_combined_list.append(str(count))
                line_ls = []
                line_ls.extend([char_name, str(subs_arr[row][2])])
                time_start = subs_arr[row][1]
            
            # 如果是最后一行，则把此行的结束时间和台词直接写入
            if row == (subs_arr.shape[0] - 1):
                t_new_split = time_start.split()
                t_end_split = subs_arr[row][1].split()
                t_new_split[2] = t_end_split[2]
                csv_to_srt_combined_list.append(' '.join(t_new_split))
                csv_to_srt_combined_list.append(' '.join(line_ls))

    np_list = np.array(csv_to_srt_combined_list)
    n = 3
    m = int(len(csv_to_srt_combined_list)/n)
    np_list_new = np_list.reshape(m,n)

    combined_srt_list = list()
    for x in range(np_list_new.shape[0]):
        for y in range(np_list_new.shape[1]):
            if y == 2:
                new_line = np_list_new[x][y].replace("】 ", "】").replace("-】", "】")
                np_list_new[x][y] = new_line
            combined_srt_list.extend([np_list_new[x][y],'\n'])
        combined_srt_list.append('\n')

    fsrt = 'output-text/srt/' + new_fname + '.srt'
    f2 = open(fsrt, 'w')
    csv_to_srt_list = ''.join(combined_srt_list)
    f2.write(csv_to_srt_list)
    f2.close()
    print(new_fname + '字幕文件（整合）已生成！')


# 需要自定义的部分
fname = '赵熵'

for i in range(11, 16):
    episode = f"{i:02}"

    # 读取文件
    full_fname = fname + episode
    input_fpath = 'input-csv/' + full_fname + '.csv'
    input_csv = pd.read_csv(input_fpath, header=None)
    subs_arr = np.array(input_csv)

    # 调用函数
    csv_to_txt(full_fname, subs_arr)
    csv_to_compressed_srt(full_fname, subs_arr)

