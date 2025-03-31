import os
import subprocess
import textwrap

from PIL import Image, ImageFilter, ImageDraw, ImageFont


def draw_multiline_text(
        draw,
        xy: tuple[float, float],
        text: str,
        fill=None,
        font: str = 'fonts/AnonymousPro-Regular.ttf',
        font_size: int = 90,
        max_width: int = 35,
        dy: int = 35,
        anchor=None,
        spacing=2,
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
    pos_text = str(position)

    draw_multiline_text(bg_draw, (80 + shadow_offset, 795 + shadow_offset), pos_text, font='fonts/AnonymousPro-Bold.ttf',
                        font_size=215, fill='#00000059', stroke_width=9,
                        stroke_fill='#00000059')
    draw_multiline_text(fg_draw, (80, 795), pos_text, font='fonts/AnonymousPro-Bold.ttf', font_size=215, fill=pos_color,
                        stroke_width=9, stroke_fill='white')
    author_x = 380 if position >= 10 else 290
    author_text = clip_info['author']
    title_text = clip_info['title']
    draw_multiline_text(bg_draw, (author_x + shadow_offset, 805 + shadow_offset), author_text, font_size=90,
                        fill='#00000059', stroke_width=3, stroke_fill='#00000059')
    draw_multiline_text(bg_draw, (author_x + shadow_offset, 915 + shadow_offset), title_text, font_size=90,
                        fill='#00000059', stroke_width=3, stroke_fill='#00000059')
    draw_multiline_text(fg_draw, (author_x, 805), author_text, font_size=90, fill='gray', stroke_width=3,
                        stroke_fill='black')
    draw_multiline_text(fg_draw, (author_x, 915), title_text, font_size=90, fill='gray', stroke_width=3,
                        stroke_fill='black')
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
    label_y = 40
    for label in clip_info.get('labels', {}).get('right', []):
        draw_multiline_text(bg_draw, (1305 + shadow_offset, label_y + shadow_offset), label, font_size=85,
                            fill='#00000059', stroke_width=3, stroke_fill='#00000059')
        draw_multiline_text(fg_draw, (1305, label_y), label, font_size=85, fill='gray', stroke_width=3,
                            stroke_fill='black')
        label_y += 100
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
    parallax_segment = os.path.join(temp_dir, f"parallax_{clip_num}.mp4")
    duration = int(clip_info['endTime'] - clip_info['startTime'])
    cmd = [
        'depthflow', 'input', '-i', clip_info['image'], 'main',
        '--time', str(duration), '--speed', '0.4', '-o', parallax_segment
    ]
    print('Creating parallax animation...')
    subprocess.run(cmd, check=True)
    input_displayable_file = parallax_segment

    detect_cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        input_displayable_file
    ]
    print('Detecting orientation...')
    result = subprocess.run(detect_cmd, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split(',')[0:2])

    if width > height:
        scale_filter = f'scale={target_width}:-2'
    else:
        scale_filter = f'scale=-2:{target_height}'

    duration = clip_info['endTime'] - clip_info['startTime']
    video_segment = os.path.join(temp_dir, f"clip_{clip_num}.mp4")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', input_displayable_file,
        '-t', str(duration),
        '-vf', f'{scale_filter}',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p', '-an',
        video_segment
    ]
    print('Scaling video...')
    subprocess.run(cmd, check=True)

    audio_file = os.path.join(temp_dir, f"audio_{clip_num}.aac")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-ss', str(clip_info['startTime']),
        '-to', str(clip_info['endTime']),
        '-i', clip_info['audio'],
        '-c:a', 'aac', '-b:a', '192k',
        audio_file
    ]
    print('Cutting audio...')
    subprocess.run(cmd, check=True)

    audio_visual = os.path.join(temp_dir, f"audio_visual_{clip_num}.mp4")
    cmd = [
        'python', 'audio_visual.py', audio_file, audio_visual
    ]
    print('Creating audio visual...')
    subprocess.run(cmd, check=True)

    bg_file = os.path.join(temp_dir, f"bg_{clip_num}.mp4")
    detect_cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        input_displayable_file
    ]
    print('Detecting orientation...')
    result = subprocess.run(detect_cmd, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split(',')[0:2])

    scale_filter = ''

    while width < target_width or height < target_height:
        if (width > height) and (height != target_height):
            scale_filter += f'scale=-2:{target_height},'
            width = round(width * target_height / height)
            height = target_height
        else:
            scale_filter += f'scale={target_width}:-2,'
            height = round(height * target_width / width)
            width = target_width

    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', input_displayable_file,
        '-vf', (
            f'{scale_filter}'
            f'crop={target_width}:{target_height},'
            'gblur=sigma=10,'
            'setsar=1'
        ),
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-an',
        bg_file
    ]
    print('Creating background...')
    subprocess.run(cmd, check=True)
    text_img_path = os.path.join(temp_dir, f"text_{clip_num}.png")
    create_composite_text_image(clip_info, position, text_img_path)
    base_composition = os.path.join(temp_dir, f"base_{clip_num}.mp4")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', bg_file,
        '-i', video_segment,
        '-i', audio_visual,  # Add the 3rd overlay input
        '-filter_complex',
        '[2:v]colorkey=black:0.1:0.1[transparent];'  # First make 3rd overlay's black pixels transparent
        '[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[bg_vid];'  # Center main video
        '[bg_vid][transparent]overlay=main_w-overlay_w-20:main_h-overlay_h-20',  # Overlay processed 3rd image
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-an',
        base_composition
    ]
    print('Creating base composition...')
    subprocess.run(cmd, check=True)
    final_clip = os.path.join(temp_dir, f"final_{clip_num}.mp4")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', base_composition,
        '-i', text_img_path,
        '-i', audio_file,
        '-filter_complex',
        f'[1:v]scale={target_width}:{target_height},format=rgba,'
        'loop=loop=-1:size=1:start=0,'
        'fade=in:st=0:d=1:alpha=1,'
        f'fade=out:st={duration - 1}:d=1:alpha=1,'
        f'trim=duration={duration},'
        'format=rgba,setpts=PTS-STARTPTS[text];'
        '[0:v][text]overlay=0:0:shortest=1,'
        'fps=24,setpts=PTS-STARTPTS[video];'
        f'[2:a]afade=t=in:st=0:d=0.5,afade=t=out:st={duration - 0.5}:d=0.5,'
        f'atrim=0:{duration},asetpts=PTS-STARTPTS[audio]',
        '-map', '[video]',
        '-map', '[audio]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',  # Explicit sample rate
        '-movflags', '+faststart',
        final_clip
    ]
    print('Rendering final clip...')
    subprocess.run(cmd, check=True)

    return final_clip


if __name__ == '__main__':
    import argparse
    import json
    import tempfile
    import shutil

    parser = argparse.ArgumentParser()
    parser.add_argument('input_json')
    parser.add_argument('output_file')
    args = parser.parse_args()

    with open(args.input_json) as f:
        clip_data = json.load(f)

    temp_dir = tempfile.gettempdir()
    print('Processing clip...')
    clip_file = process_clip(clip_data, clip_data['pos'], 0, temp_dir)
    shutil.copyfile(clip_file, args.output_file)

    try:
        os.remove(clip_file)
    except:
        pass

    print(f"Successfully created: {args.output_file}")
