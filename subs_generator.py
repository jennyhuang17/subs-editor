import subsgen as sg
import sys

file_name = sys.argv[1]

sg.write_srt(file_name)
sg.write_txt(file_name)