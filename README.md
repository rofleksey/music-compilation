Automatically render Top-N music videos.

https://github.com/user-attachments/assets/cad75cc3-e8a4-4364-aa37-274ccc455294

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


