Automatically render Top-N music videos.

https://github.com/user-attachments/assets/22575516-0bd5-4959-8c1e-7d238cb5356f

### Requirements

* `ffmpeg` in `$PATH`

### Usage

input.json
```json
[
  {
    "image": "clips/logo.jpg",
    "audio": "clips/alley.mp3",
    "startTime": 38,
    "endTime": 48,
    "delta": "+1",
    "author": "Dorohedoro",
    "title": "Alley",
    "labels": {
      "left": [
        "Your text",
        "Goes here"
      ],
      "right": [
        "Your text",
        "Goes here"
      ]
    }
  },
  {
    "video": "clips/smoke.mkv",
    "startTime": 16,
    "endTime": 26,
    "delta": "=",
    "author": "Dorohedoro",
    "title": "Smoke",
    "labels": {
      "left": [
        "Your text",
        "Goes here"
      ],
      "right": [
        "Your text",
        "Goes here"
      ]
    }
  }
]
```

Command line
```bash
python compilation.py input.json output.mp4
```


