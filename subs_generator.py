import sys

import subsgen as sg

file_name = sys.argv[1]
pattern = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None

sg.write_srt(file_name, pattern)
sg.write_txt(file_name, pattern)
