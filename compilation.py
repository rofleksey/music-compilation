import json
import tempfile
import subprocess
import os

from process_clip import process_clip


def create_video_compilation(json_file, output_file):
    """Main compilation function with proper command structure."""
    with open(json_file) as f:
        clips_data = json.load(f)

    temp_dir = tempfile.gettempdir()
    clip_files = []

    for i, clip_info in enumerate(clips_data):
        position = len(clips_data) - i
        print(f"Processing clip {i + 1}/{len(clips_data)} (Position {position})")
        clip_files.append(process_clip(clip_info, position, i, temp_dir))

    # Concatenate all clips (simple command)
    concat_file = os.path.join(temp_dir, 'concat.txt')
    with open(concat_file, 'w') as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")

    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-c', 'copy',
        output_file
    ]
    subprocess.run(cmd, check=True)

    # Cleanup
    for f in clip_files + [concat_file]:
        try:
            os.remove(f)
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_json')
    parser.add_argument('output_file')
    args = parser.parse_args()

    create_video_compilation(args.input_json, args.output_file)
    print(f"Successfully created: {args.output_file}")