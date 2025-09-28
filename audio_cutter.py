import pysrt
import subprocess
import os
import re
from datetime import datetime, timedelta

def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing unsafe characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def adjust_time(time_obj, delta):
    """Adjust a datetime.time object by a timedelta."""
    datetime_obj = datetime.combine(datetime.today(), time_obj)
    adjusted_datetime = datetime_obj + delta
    return adjusted_datetime.time()

def srt_to_audio_segments(drama, episode_start, episode_end, start_time_adjust, end_time_adjust):

    for episode in range(episode_start, episode_end+1):
        n = f"{episode:02}"
        file_name = drama+n

        srt_dir = "output-text/srt/" + file_name[:-2]
        audio_dir = "input-audio"

        audio_name = file_name
        audio_format = "mp3"

        srt_file = os.path.join(srt_dir, f"{file_name}.srt")
        audio_file = os.path.join(audio_dir, f"{audio_name}.{audio_format}")
        output_dir = os.path.join(f"output-audio", audio_name)

        if not os.path.exists(audio_file):
            continue

        # Load the subtitles
        subs = pysrt.open(srt_file)

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for index, sub in enumerate(subs, start=1):
            # Extract and adjust start and end times
            start_time = adjust_time(sub.start.to_time(), timedelta(seconds=start_time_adjust))
            end_time = adjust_time(sub.end.to_time(), timedelta(seconds=end_time_adjust))

            # Ensure start time is not negative
            if datetime.combine(datetime.today(), start_time) < datetime.combine(datetime.today(), datetime.min.time()):
                start_time = datetime.min.time()

            # Convert times to the format hh:mm:ss.xxx for FFmpeg
            start_str = f"{start_time.hour:02}:{start_time.minute:02}:{start_time.second:02}.{int(start_time.microsecond / 1000):03}"
            end_str = f"{end_time.hour:02}:{end_time.minute:02}:{end_time.second:02}.{int(end_time.microsecond / 1000):03}"

            # Use the subtitle text for the output file name, sanitized for file system compatibility
            output_filename = sanitize_filename(sub.text)[:200]  # Limit filename length for practicality
            output_path = os.path.join(output_dir, f"{file_name[-2:]}-{index:03} {output_filename}.{audio_format}")

            # FFmpeg command to extract the audio segment
            cmd = [
                "ffmpeg",
                "-i", audio_file,
                "-ss", start_str,
                "-to", end_str,
                "-c", "copy",
                output_path
            ]

            # Run the command
            subprocess.run(cmd, check=True)
            print(f"Extracted: {output_path}")

# 调整句长
start_time_adjust = -0.3
end_time_adjust = 0.3
episode_start = 21
episode_end = 22
drama = "光渊"
srt_to_audio_segments(drama, episode_start, episode_end, start_time_adjust, end_time_adjust)