Automatically render Top-N music videos.

### Usage

input.json
```json
[
  {
    "video": "clips/alley.mkv", // video source
    "startTime": 38, // clip start
    "endTime": 48, // clip end
    "pos": 2, // displayed position
    "delta": "+1", // displayed delta [-N, =, +N]
    "author": "Dorohedoro",
    "title": "Alley",
    "labels": [ // text in the upper right corner of the video
      "Your text",
      "Goes here"
    ]
  },
  {
    "image": "clips/smoke.jpg", // audio + image source
    "audio": "clips/smoke.mp3",
    "startTime": 16,
    "endTime": 26,
    "pos": 1,
    "delta": "=",
    "author": "Dorohedoro",
    "title": "Smoke",
    "labels": [
      "Your text",
      "Goes here"
    ]
  }
]
```

Command line
```bash
python compilation.py input.json output.mp4
```


