import os
import subprocess
import textwrap

from PIL import Image, ImageFilter, ImageDraw, ImageFont


def draw_multiline_text(
        draw,
        xy: tuple[float, float],
        text: str,
        fill=None,
        font: str = 'fonts/Arial.ttf',
        font_size: int = 90,
        max_width: int = 40,
        dy: int = 35,
        anchor=None,
        spacing=4,
        align="left",
        direction=None,
        features=None,
        language=None,
        stroke_width=0,
        stroke_fill=None,
        embedded_color=False):
    lines = textwrap.wrap(text, width=max_width)
    font_size /= max(1, len(lines))

    try:
        actual_font = ImageFont.truetype(font, font_size)
    except IOError:
        print("Warning: Using default font")
        actual_font = ImageFont.load_default()

    cur_x = xy[0]
    cur_y = xy[1]
    for line in lines:
        draw.text((cur_x, cur_y), line,
                  font=actual_font,
                  anchor=anchor,
                  fill=fill,
                  spacing=spacing,
                  align=align,
                  direction=direction,
                  features=features,
                  language=language,
                  stroke_width=stroke_width,
                  stroke_fill=stroke_fill,
                  embedded_color=embedded_color)
        cur_y += dy


def create_composite_text_image(clip_info, position, output_path):
    """Create a single composite image with all text elements."""
    fg = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    fg_draw = ImageDraw.Draw(fg)

    bg = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)

    # Position color logic
    pos_color = '#C0B207'
    if position > 40:
        pos_color = '#E77101'
    elif position > 30:
        pos_color = '#690B02'
    elif position > 20:
        pos_color = '#040DCB'
    elif position > 10:
        pos_color = '#020202'

    shadow_offset = 12

    # 1. Position number
    pos_text = str(position)
    # bbox = draw.textbbox((0, 0), pos_text, font=bold_font)

    draw_multiline_text(bg_draw, (80 + shadow_offset, 795 + shadow_offset), pos_text, font='fonts/ArialBold.ttf',
                        font_size=215, fill='#00000059', stroke_width=9,
                        stroke_fill='#00000059')
    draw_multiline_text(fg_draw, (80, 795), pos_text, font='fonts/ArialBold.ttf', font_size=215, fill=pos_color,
                        stroke_width=9, stroke_fill='white')

    # 2. Author and title
    author_x = 380 if position >= 10 else 290
    author_text = clip_info['author']
    title_text = clip_info['title']

    # Shadow effect
    draw_multiline_text(bg_draw, (author_x + shadow_offset, 815 + shadow_offset), author_text, font_size=90,
                        fill='#00000059', stroke_width=3, stroke_fill='#00000059')
    draw_multiline_text(bg_draw, (author_x + shadow_offset, 925 + shadow_offset), title_text, font_size=90,
                        fill='#00000059', stroke_width=3, stroke_fill='#00000059')

    # Main text
    draw_multiline_text(fg_draw, (author_x, 815), author_text, font_size=90, fill='gray', stroke_width=3,
                        stroke_fill='black')
    draw_multiline_text(fg_draw, (author_x, 925), title_text, font_size=90, fill='gray', stroke_width=3,
                        stroke_fill='black')

    # 3. Delta if exists
    if clip_info.get('delta'):
        delta_color = '#FF8200'
        if clip_info['delta'].startswith('-'):
            delta_color = '#FF1A00'
        elif clip_info['delta'].startswith('+'):
            delta_color = '#03C400'
        draw_multiline_text(bg_draw, (104 + shadow_offset, 335 + shadow_offset), clip_info['delta'], font_size=130,
                            fill='#00000059', stroke_width=3, stroke_fill='#00000059')
        draw_multiline_text(fg_draw, (104, 335), clip_info['delta'], font_size=130, fill=delta_color, stroke_width=3,
                            stroke_fill='black')

    # 4. Right Labels
    label_y = 40
    for label in clip_info.get('labels', {}).get('right', []):
        draw_multiline_text(bg_draw, (1305 + shadow_offset, label_y + shadow_offset), label, font_size=85,
                            fill='#00000059', stroke_width=3, stroke_fill='#00000059')
        draw_multiline_text(fg_draw, (1305, label_y), label, font_size=85, fill='gray', stroke_width=3,
                            stroke_fill='black')
        label_y += 100

    # 4. Left Labels
    label_y = 40
    for label in clip_info.get('labels', {}).get('left', []):
        draw_multiline_text(bg_draw, (25 + shadow_offset, label_y + shadow_offset), label, font_size=40,
                            fill='#00000059', stroke_width=2, stroke_fill='#00000059')
        draw_multiline_text(fg_draw, (25, label_y), label, font_size=40, fill='gray', stroke_width=2,
                            stroke_fill='black')
        label_y += 50

    bg = bg.filter(ImageFilter.BoxBlur(7))
    bg.paste(fg, fg)

    bg.save(output_path)


def process_clip(clip_info, position, clip_num, temp_dir, target_width=1920, target_height=1080):
    """Process a single clip with proper FFmpeg command structure."""
    # 1. Process source media

    if 'video' in clip_info:
        input_displayable_file = clip_info['video']
        # First detect the orientation
        detect_cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            clip_info['video']
        ]
        result = subprocess.run(detect_cmd, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split(',')[0:2])

        if width > height:
            scale_filter = f'scale={target_width}:-2'
        else:
            scale_filter = f'scale=-2:{target_height}'

        duration = clip_info['endTime'] - clip_info['startTime']
        # Extract video segment
        video_segment = os.path.join(temp_dir, f"clip_{clip_num}.mp4")
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-ss', str(clip_info['startTime']),
            '-to', str(clip_info['endTime']),
            '-i', clip_info['video'],
            '-vf', f'{scale_filter}',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-an',
            video_segment
        ]
        subprocess.run(cmd, check=True)

        # Extract audio
        audio_file = os.path.join(temp_dir, f"audio_{clip_num}.aac")
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-ss', str(clip_info['startTime']),
            '-to', str(clip_info['endTime']),
            '-i', clip_info['video'],
            '-c:a', 'aac', '-b:a', '192k',
            audio_file
        ]
        subprocess.run(cmd, check=True)
    else:
        input_displayable_file = clip_info['image']
        # First detect the orientation
        detect_cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            clip_info['image']
        ]
        result = subprocess.run(detect_cmd, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split(',')[0:2])

        if width > height:
            scale_filter = f'scale={target_width}:-2'
        else:
            scale_filter = f'scale=-2:{target_height}'

        # Handle image+audio case
        duration = clip_info['endTime'] - clip_info['startTime']
        video_segment = os.path.join(temp_dir, f"clip_{clip_num}.mp4")
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-loop', '1', '-i', clip_info['image'],
            '-t', str(duration),
            '-vf', f'{scale_filter}',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p', '-an',
            video_segment
        ]
        subprocess.run(cmd, check=True)

        # Extract audio
        audio_file = os.path.join(temp_dir, f"audio_{clip_num}.aac")
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-ss', str(clip_info['startTime']),
            '-to', str(clip_info['endTime']),
            '-i', clip_info['audio'],
            '-c:a', 'aac', '-b:a', '192k',
            audio_file
        ]
        subprocess.run(cmd, check=True)

    # 2. Create blurred background (separate command)
    bg_file = os.path.join(temp_dir, f"bg_{clip_num}.mp4")

    # First detect the orientation
    detect_cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        input_displayable_file
    ]
    result = subprocess.run(detect_cmd, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split(',')[0:2])

    scale_filter = ''

    while width < target_width or height < target_height:
        if (width > height) and (height != target_height):  # Landscape
            scale_filter += f'scale=-2:{target_height},'
            width = round(width * target_height / height)
            height = target_height
            print(width, height)
        else:  # Portrait
            scale_filter += f'scale={target_width}:-2,'
            height = round(height * target_width / width)
            width = target_width
            print(width, height)

    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'debug',
        '-i', input_displayable_file,
        '-vf', (
            f'{scale_filter}'  # Scale based on orientation
            f'crop={target_width}:{target_height},'  # Center crop
            'gblur=sigma=10,'  # Blur equivalent to intensity=5
            'setsar=1'  # Set pixel aspect ratio
        ),
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-an',
        bg_file
    ]
    subprocess.run(cmd, check=True)

    # 3. Create single composite text image
    text_img_path = os.path.join(temp_dir, f"text_{clip_num}.png")
    create_composite_text_image(clip_info, position, text_img_path)

    # 5. Create base composition (background + main video)
    base_composition = os.path.join(temp_dir, f"base_{clip_num}.mp4")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', bg_file,
        '-i', video_segment,
        '-filter_complex', '[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-an',
        base_composition
    ]
    subprocess.run(cmd, check=True)

    # 6. Final composition with text and fades
    final_clip = os.path.join(temp_dir, f"final_{clip_num}.mp4")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', base_composition,  # Background + main video
        '-i', text_img_path,  # Text image (must be PNG with alpha)
        '-i', audio_file,  # Audio track
        '-filter_complex',
        # Process text image with proper alpha handling
        f'[1:v]scale={target_width}:{target_height},format=rgba,'
        'loop=loop=-1:size=1:start=0,'  # Loop single frame for duration
        # 'setpts=N/FRAME_RATE/TB,'  # Set proper timestamps
        'fade=in:st=0:d=1:alpha=1,'  # Fade in over 1 second
        f'fade=out:st={duration - 1}:d=1:alpha=1,'  # Fade out
        f'trim=duration={duration},'  # Trim to exact duration
        'format=rgba[text];'  # Maintain alpha channel

        # Overlay text on base video
        '[0:v][text]overlay=0:0:shortest=1,fps=24',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',  # Ensure compatible pixel format
        '-c:a', 'aac',
        '-b:a', '192k',
        '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st={duration}:d=0.5'
        .format(duration=duration - 0.5),
        '-shortest',
        final_clip
    ]
    subprocess.run(cmd, check=True)

    return final_clip


if __name__ == '__main__':
    import argparse
    import json
    import tempfile
    import shutil

    parser = argparse.ArgumentParser()
    parser.add_argument('input_json')
    parser.add_argument('--preview', action=argparse.BooleanOptionalAction)
    parser.add_argument('output_file')
    args = parser.parse_args()

    with open(args.input_json) as f:
        clip_data = json.load(f)

    temp_dir = tempfile.gettempdir()
    print('Processing clip...')
    target_width = 480 if args.preview else 1920
    target_height = 270 if args.preview else 1080
    clip_file = process_clip(clip_data, clip_data['pos'], 0, temp_dir, target_width, target_height)
    shutil.copyfile(clip_file, args.output_file)

    try:
        os.remove(clip_file)
    except:
        pass

    print(f"Successfully created: {args.output_file}")
