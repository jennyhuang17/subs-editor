import subsgen as sg
import sys

# 修改mp3文件中“artist”信息

if __name__ == "__main__":
    # Specify the folder containing MP3 files
    folder_path = sys.argv[1]

    # Specify the artist name to update
    artist_name = "lnlychee"

    # Call the function
    sg.update_artist_metadata(folder_path, artist_name)
