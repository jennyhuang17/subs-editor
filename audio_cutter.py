import pysrt
import subprocess
import os
import re
import sys
from datetime import datetime, timedelta
import subsgen as sg


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def adjust_time(time_obj, delta):
    dt = datetime.combine(datetime.today(), time_obj)
    return (dt + delta).time()


def srt_to_audio_segments(drama, episode_start, episode_end,
                           start_time_adjust, end_time_adjust,
                           artist_name="lnlychee"):
    base_output_dir = "output-audio"

    for episode in range(episode_start, episode_end + 1):
        n = f"{episode:02}"
        file_name = drama + n

        srt_file   = os.path.join("output-srt", drama, f"{file_name}.srt")
        audio_file = os.path.join("input-audio", f"{file_name}.mp3")
        episode_output_dir = os.path.join(base_output_dir, file_name)

        if not os.path.exists(audio_file):
            print(f"跳过（音频不存在）: {audio_file}")
            continue

        subs = pysrt.open(srt_file)
        os.makedirs(episode_output_dir, exist_ok=True)

        for index, sub in enumerate(subs, start=1):
            start_time = adjust_time(sub.start.to_time(), timedelta(seconds=start_time_adjust))
            end_time   = adjust_time(sub.end.to_time(),   timedelta(seconds=end_time_adjust))

            # 确保起始时间不为负
            zero = datetime.min.time()
            if datetime.combine(datetime.today(), start_time) < datetime.combine(datetime.today(), zero):
                start_time = zero

            fmt = lambda t: f"{t.hour:02}:{t.minute:02}:{t.second:02}.{t.microsecond // 1000:03}"
            output_path = os.path.join(
                episode_output_dir,
                f"{n}-{index:03} {sanitize_filename(sub.text)[:200]}.mp3"
            )

            subprocess.run(
                ["ffmpeg", "-i", audio_file, "-ss", fmt(start_time), "-to", fmt(end_time), "-c", "copy", output_path],
                check=True
            )
            print(f"截取: {output_path}")

        # 切完当集后直接打 artist 标签
        sg.update_artist_metadata(episode_output_dir, artist_name)
        print(f"已标记 artist='{artist_name}': {episode_output_dir}")


if __name__ == "__main__":
    # ── 配置区 ──────────────────────────────────────────────────────────────
    drama             = "水龙吟"
    episode_start     = 35
    episode_end       = 40
    start_time_adjust = -0.4
    end_time_adjust   =  0.4
    artist_name       = "lnlychee"
    # ────────────────────────────────────────────────────────────────────────

    srt_to_audio_segments(drama, episode_start, episode_end,
                           start_time_adjust, end_time_adjust, artist_name)
