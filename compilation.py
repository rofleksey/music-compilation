import json
import argparse
import textwrap
from dataclasses import dataclass

import numpy as np
from PIL import ImageFilter, ImageDraw, Image
from moviepy import TextClip, concatenate_videoclips, VideoFileClip, CompositeVideoClip, AudioFileClip, ImageClip, \
    Effect, Clip
from moviepy.video.fx import *
from moviepy.audio.fx import *
from scipy.ndimage import gaussian_filter

parser = argparse.ArgumentParser(description='Create a video compilation from JSON input.')
parser.add_argument('input_json', help='Input JSON file with video clip information')
parser.add_argument('output_file', help='Output video file (MP4)')
parser.add_argument('--preview', action=argparse.BooleanOptionalAction)
args = parser.parse_args()

# TODO: test weird source video size
# TODO: gradient

# Set ImageMagick path if needed (uncomment and modify for your system)
# change_settings({"IMAGEMAGICK_BINARY": "/path/to/convert"})

@dataclass
class Blur(Effect):
    intensity: float = None

    def apply(self, clip: Clip) -> Clip:
        def filter(gf, t):
            im = gf(t).copy()
            image = Image.fromarray(im)
            blurred = image.filter(ImageFilter.GaussianBlur(radius=self.intensity))
            return np.array(blurred)

        return clip.transform(filter)

def blur(clip, sigma):
    return clip.image_transform(lambda image: gaussian_filter(image, sigma=sigma), apply_to=['mask'])

def create_animated_text(
        text='?',
        x=0,
        y=0,
        max_width=40,
        dy=40,
        color='#FF0000',
        stroke_color=None,
        stroke_width=0,
        font='fonts/Arial.ttf',
        size=30,
        duration=1,
        text_align='left',
):
    wrapped_text = textwrap.wrap(text, max_width)
    size /= len(wrapped_text)

    result = []
    cur_y = 0
    for text in wrapped_text:
        text_clip = TextClip(
            text=text,
            font_size=size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            font=font,
            text_align=text_align,
            margin=(100, 100, 100, 100),
            # transparent=True,
        ).with_position((0, cur_y))

        shadow_clip = TextClip(
            text=text,
            font_size=size,
            color='#00000059',
            stroke_color='#00000059',
            stroke_width=stroke_width,
            font=font,
            text_align=text_align,
            margin=(100, 100, 100, 100),
            transparent=True,
        ).with_position((15, cur_y + 10))
        shadow_clip = blur(shadow_clip, sigma=2) # sigma male

        composite = CompositeVideoClip([shadow_clip, text_clip])
        result.append(composite)
        cur_y += dy

    return CompositeVideoClip(result).with_position((x, y)).with_duration(duration).with_effects([CrossFadeIn(1), CrossFadeOut(1)])


def process_clip(clip_info, position):
    if 'video' in clip_info:
        video = VideoFileClip(clip_info['video']).subclipped(
            clip_info['startTime'],
            clip_info['endTime']
        )
    elif 'image' in clip_info and 'audio' in clip_info:
        audio_clip = AudioFileClip(clip_info['audio']).subclipped(
            clip_info['startTime'],
            clip_info['endTime']
        )
        video = ImageClip(clip_info['image']).with_duration(audio_clip.duration)
        video = video.with_audio(audio_clip)
    else:
        raise ValueError('clip must be either video or image+audio')

    if video.h > video.w:
        video = video.resized(height=1080)
    else:
        video = video.resized(width=1920)

    video = video.with_position(('center', 'center'))

    if video.w != 1920 or video.h != 1080:
        background = video.without_audio()
        if background.h > background.w:
            background = background.resized(width=1920)
        else:
            background = background.resized(height=1080)
        background = background.cropped(x_center=background.w/2, y_center=background.h/2, width=1920, height=1080)
        background = background.with_effects([Blur(intensity=5)])
        video = CompositeVideoClip([background, video])

    text_clips = []

    pos_color = '#C0B207'
    if position > 40:
        pos_color = '#E77101'
    elif position > 30:
        pos_color = '#690B02'
    elif position > 20:
        pos_color = '#040DCB'
    elif position > 10:
        pos_color = '#020202'

    pos_clip = create_animated_text(
        text=str(position),
        font='fonts/ArialBold.ttf',
        size=215,
        x=-22,
        y=728,
        color=pos_color,
        stroke_width=9,
        stroke_color='white',
        text_align='center',
        duration=video.duration
    )
    text_clips.append(pos_clip)

    author_x = 285
    if position < 10:
        author_x = 195

    author_clip = create_animated_text(
        text=clip_info['author'],
        size=90,
        max_width=50,
        x=author_x,
        y=720,
        color='gray',
        stroke_color='black',
        stroke_width=3,
        duration=video.duration
    )
    text_clips.append(author_clip)

    title_clip = create_animated_text(
        text=clip_info['title'],
        size=90,
        max_width=50,
        x=author_x,
        y=820,
        color='gray',
        stroke_color='black',
        stroke_width=3,
        duration=video.duration
    )
    text_clips.append(title_clip)

    if clip_info['delta']:
        delta_color = '#FF8200'
        if clip_info['delta'].startswith('-'):
            delta_color = '#FF1A00'
        elif clip_info['delta'].startswith('+'):
            delta_color = '#03C400'

        diff_clip = create_animated_text(
            text=clip_info['delta'],
            size=125,
            x=4,
            y=245,
            color=delta_color,
            duration=video.duration
        )
        text_clips.append(diff_clip)

    label_y = -52
    for label in clip_info.get('labels', []):
        title_clip = create_animated_text(
            text=label,
            size=85,
            max_width=35,
            dy=30,
            x=1205,
            y=label_y,
            color='gray',
            stroke_color='black',
            stroke_width=3,
            duration=video.duration
        )
        text_clips.append(title_clip)
        label_y += 100

    if text_clips:
        video = CompositeVideoClip([video] + text_clips)

    return video.with_effects([AudioFadeIn(0.5), AudioFadeOut(0.5)])


def create_video_compilation(json_file, output_file):
    with open(json_file) as f:
        clips_data = json.load(f)

    processed_clips = []
    for i, clip_info in enumerate(clips_data):
        clip = process_clip(clip_info, len(clips_data) - i)
        processed_clips.append(clip)

    final_video = concatenate_videoclips(processed_clips, method="compose")

    if args.preview:
        final_video.preview(fps=5)
    else:
        final_video.write_videofile(
            output_file,
            codec='libx264',
            audio_codec='aac',
            fps=24,
            threads=8,
            preset='fast',
            ffmpeg_params=['-crf', '23']
        )

    final_video.close()
    for clip in processed_clips:
        clip.close()

create_video_compilation(args.input_json, args.output_file)