Automatically render Top-N music videos.

https://github.com/user-attachments/assets/cad75cc3-e8a4-4364-aa37-274ccc455294

### Requirements

* `ffmpeg` in `$PATH`
* `depthflow` in `$PATH`

### Usage

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


