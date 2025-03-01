# Video Captioning

## Overview
Video Captioning is a Python project that adds subtitles to video files. The project uses various libraries such as Whisper, MoviePy, and Deep Translator to transcribe and translate audio from videos into subtitles. It also has the capability to separate vocals from music to improve transcription accuracy.

## Features
- python 3.11

- Extracts audio from video files

- Separates vocals from music

- Transcribes audio to text

- Generates subtitle files in .srt format

- Translates subtitles into different languages

- Overlays subtitles onto video files

## Requirements

- Whisper

- MoviePy

- srt

- [demucs](https://github.com/facebookresearch/demucs)

- Deep Translator

- [ImageMagick](https://imagemagick.org/)

## USAGE

```
from video_captioning import VideoCaptioning
vc = VideoCaptioning(font="Courier", fontsize=24)

vc.run(video_path="path/to/your/video.mp4", separate=False, translate_to="fr")
```

## Code Overview

VideoCaptioning Class
- __init__(self, font: str = "Courier", fontsize: int = 24) Initializes the class with default values for font, font size, video size, language, and directories.

- format_time(self, seconds: int) -> str Converts time in seconds to SRT format (hh:mm:ss,ms).

- get_audio(self, video_path: str, output_ext: str = "mp3") -> str Extracts audio from a video file and saves it as an audio file.

- get_vocals(self) -> str Separates vocals from music using Demucs.

- transcribe(self, audio) Transcribes the audio file to text and detects the language.

- generate_subtitle_file(self, segments) -> str Creates an SRT subtitle file based on the transcription output.

- translate_subtitles(self, dest_lang="fr") -> str Translates the SRT subtitle file to the specified language.

- generate_text_clips(self, subtitle_file) Generates text clips for the subtitles to overlay onto the video.

- run(self, video_path, separate=False, translate_to=None) Runs the entire captioning process, including audio extraction, vocal separation, transcription, subtitle generation, and translation.

## TODO
- Improve transcription for dialogue

- Find a better way to extract audio

## Contributing
Contributions are welcome! Feel free to submit a Pull Request or raise an issue if you find any bugs or have suggestions for improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.