Automatically render Top-N music videos.

https://github.com/user-attachments/assets/93dcfbc6-725c-4bbc-ab2c-40ee2e71f735

### Requirements

* `ffmpeg` in `$PATH`

### Usage

input.json
```json
[
  {
    "video": "clips/alley.mkv",
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


