import argparse
import subprocess
import sys
import tempfile

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


def create_audio_visualization(input_file, output_file, resolution=(1920, 1080),
                               dpi=100, fps=30, crf=18, preset='medium'):
    # Load audio file
    y, sr = librosa.load(input_file)
    duration = librosa.get_duration(y=y, sr=sr)
    total_frames = int(duration * fps)

    # Set up matplotlib figure with black background
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(resolution[0] / dpi, resolution[1] / dpi), dpi=dpi)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    # Set figure and axes to have black background
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Create line plot
    line, = ax.plot([], [], lw=1, color='gray')
    ax.set_xlim(0, len(y))
    ax.set_ylim(-1, 1)
    ax.axis('off')  # Turn off all axis elements

    def update(frame):
        current_sample = int(frame * len(y) // total_frames)
        start = max(0, current_sample - sr)
        line.set_data(np.arange(start, current_sample), y[start:current_sample])
        return line,

    # Create temporary directory for frames
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Rendering frames...")

        # Render frames with black background
        for frame in range(total_frames):
            update(frame)
            fig.savefig(
                f"{tmpdir}/frame_{frame:05d}.png",
                dpi=dpi,
                facecolor='black',
                format='png',
                bbox_inches='tight',
                pad_inches=0
            )
            print(f"Rendered frame {frame + 1}/{total_frames}", end='\r')

        print("\nEncoding video with FFmpeg...")

        # FFmpeg command to create MP4 video with H.264 codec
        ffmpeg_cmd = [
            'ffmpeg',
            '-y', '-hide_banner', '-loglevel', 'error',
            '-framerate', str(fps),
            '-i', f'{tmpdir}/frame_%05d.png',
            '-c:v', 'libx264',  # H.264 codec for MP4
            '-preset', preset,
            '-crf', str(crf),
            '-pix_fmt', 'yuv420p',  # Standard pixel format for MP4
            '-an',  # No audio
            output_file
        ]

        # Run FFmpeg
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Successfully created video: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e}", file=sys.stderr)
        except FileNotFoundError:
            print("Error: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Create audio visualization videos with black background using FFmpeg')
    parser.add_argument('input', help='Input audio file')
    parser.add_argument('output', help='Output video file (should be .mp4)')
    parser.add_argument('--width', type=int, default=250,
                        help='Output video width (default: 600)')
    parser.add_argument('--height', type=int, default=100,
                        help='Output video height (default: 300)')
    parser.add_argument('--dpi', type=int, default=100,
                        help='Render DPI (default: 100)')
    parser.add_argument('--fps', type=int, default=24,
                        help='Frames per second (default: 24)')
    parser.add_argument('--crf', type=int, default=23,
                        help='CRF value (0-51 for H.264, lower is better quality, default: 23)')
    parser.add_argument('--preset', default='fast',
                        choices=['ultrafast', 'superfast', 'veryfast', 'faster',
                                 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                        help='FFmpeg preset (default: fast)')

    args = parser.parse_args()

    create_audio_visualization(
        args.input,
        args.output,
        resolution=(args.width, args.height),
        dpi=args.dpi,
        fps=args.fps,
        crf=args.crf,
        preset=args.preset
    )


if __name__ == '__main__':
    main()