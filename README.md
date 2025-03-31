Automatically render Top-N music videos.

https://github.com/user-attachments/assets/cbe41762-24e2-42f5-a85b-05bcc3fcb7f5


### Requirements

* `ffmpeg` in `$PATH`
* `depthflow` in `$PATH` (run it once first before using these scripts)

### Features

* Automatic parallax animation (using `Depthflow`)
* Supports most media formats (thanks to `FFMPEG`)

### Create compilation

input.json
```json
[
  {
    "image": "baki.jpg",
    "audio": "Baki 2018 OST - Fear Sirkosky.opus",
    "startTime": 2,
    "endTime": 12,
    "author": "Baki",
    "title": "Fear Sikorsky",
    "labels": {
      "left": [
        "Label 1",
        "Label 2"
      ],
      "right": [
        "Label 3",
        "Label 4"
      ]
    }
  },
  {
    "image": "jjk_nobara.jpg",
    "audio": "07 Paranom,Kasper - Impatience ft. Paranom and Kasper.flac",
    "startTime": 35,
    "endTime": 45,
    "author": "Jujutsu Kaisen",
    "title": "Impatience ft. Paranom and Kasper.flac",
    "labels": {
      "left": [
        "Label 1",
        "Label 2"
      ],
      "right": [
        "Label 3",
        "Label 4"
      ]
    }
  }
]
```

Command line
```bash
python compilation.py input.json output.mp4
```

### Create a single clip

input.json
```json
{
  "image": "/home/roflex/Pictures/OST Rank/baki.jpg",
  "audio": "/home/roflex/Music/Music/Baki 2018 OST - Fear Sirkosky.opus",
  "startTime": 2,
  "endTime": 12,
  "pos": 1,
  "author": "Baki",
  "title": "Fear Sikorsky",
  "labels": {
    "left": [
      "Label 1",
      "Label 2"
    ],
    "right": [
      "Label 3",
      "Label 4"
    ]
  }
}
```

Command line
```bash
python process_clip.py input.json output.mp4
```

