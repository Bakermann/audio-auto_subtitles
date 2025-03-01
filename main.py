import math

import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import srt
import demucs.separate
from deep_translator import GoogleTranslator
from moviepy.config import change_settings
import os
change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.1-Q16/magick.exe"})


# todo improve for dialogue
# todo find better way to extract audio
class Video_captionning:
    """Class to add subtitles to video file."""

    def __init__(self, font: str = "Courier", fontsize: int = 24, ):
        """Initializes the class with default values for font, font size, video size, language, and directories."""
        # load transcription model
        self.model = whisper.load_model("turbo").eval()

        # fill with default value
        self.video = None
        self.font = font
        self.font_size = fontsize
        self.video_size = tuple()
        self.language = ""
        self.filename = ""
        self.input_directory = "audio/"
        self.output_directory = "subtitles/"

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def format_time(self, seconds: int) -> str:
        """Converts time in seconds to SRT format (hh:mm:ss,ms).

        :param seconds: time in seconds
        :return: string containing seconds converted to hours minutes seconds and milliseconds
        """

        hours = math.floor(seconds / 3600)
        seconds %= 3600
        minutes = math.floor(seconds / 60)
        seconds %= 60
        milliseconds = round((seconds - math.floor(seconds)) * 1000)
        seconds = math.floor(seconds)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

        return formatted_time

    def get_audio(self, video_path: str, output_ext: str = "mp3") -> str:
        """Extracts audio from a video file and saves it as an audio file.

        :param video_path: path of the video
        :param output_ext: output extension format
        :return: extracted audio path
        """

        self.video = VideoFileClip(video_path)
        self.video_size = self.video.size
        self.filename = video_path.rsplit("/", 1)[1].split(".")[0]

        self.video.audio.write_audiofile(f"{self.input_directory}/{self.filename}.{output_ext}")

        return f"{self.input_directory}/{self.filename}.{output_ext}"

    def get_vocals(self) -> str:
        """
        Separate music from vocals using demucs.

        :return: vocals file path
        """
        demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", f"audio/{self.filename}.mp3"])

        return f"separated/mdx_extra/{self.filename}/vocals.mp3"

    def transcribe(self, audio):
        """
        Transcribe audio file.

        :param audio: audio file
        :return: audio language and text
        """
        tr = self.model.transcribe(audio)
        segments = tr["segments"]
        language = tr["language"]
        self.language = language

        return language, segments

    def generate_subtitle_file(self, segments) -> str:
        """
        Create srt file based on transcription output.

        :param segments: transcription output
        :return: srt file name
        """
        subtitle_file = f"sub-{self.filename}.{self.language}.srt"
        text = ""
        for index, segment in enumerate(segments):
            segment_start = self.format_time(segment["start"])
            segment_end = self.format_time(segment["end"])
            text += f"{str(index + 1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment['text']} \n"
            text += "\n"

        f = open(f"{self.output_directory}/{subtitle_file}", "w", encoding="utf-8")
        f.write(text)
        f.close()

        return subtitle_file

    def translate_subtitles(self, dest_lang="fr") -> str:
        """
        Translate srt file into another language.

        :param dest_lang: language to translate
        :return: new translation srt file path
        """
        # open original srt file
        with open(f"subtitles/sub-{self.filename}.{self.language}.srt", 'r', encoding="utf-8") as f:
            og_text = f.readlines()
            txt = [x for i, x in enumerate(og_text) if i in range(2, len(og_text), 4)]

            translated = GoogleTranslator(self.language, dest_lang).translate_batch(txt)[::-1]

            text = ""
            for i, x in enumerate(og_text):
                if i not in range(2, len(og_text), 4):
                    text += str(og_text[i])
                else:
                    text += f"{translated.pop()}\n"
        self.language = dest_lang
        f = open(f"subtitles/{self.filename}.{self.language}.srt", 'w', encoding="utf-8")
        f.write(text)
        f.close()

        return f"{self.filename}.{dest_lang}.srt"

    def generate_text_clips(self, subtitle_file):
        """
        Generates video subtitles.

        :param subtitle_file: srt file name
        :return: video subtitles
        """
        with open(f"subtitles/{subtitle_file}", 'r', encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))

        text_clips = []
        for subtitle in subtitles:
            text = TextClip(subtitle.content, fontsize=self.font_size, color='white', size=(self.video.w, None),
                            method='caption', font=self.font)
            text = (text.set_position(("center", "bottom")).set_start(subtitle.start.total_seconds()).set_duration(
                subtitle.end.total_seconds() - subtitle.start.total_seconds()))

            text_clips.append(text)

        return text_clips

    def run(self, video_path, separate=False, translate_to=None):
        """
        Runs the entire captioning process, including audio extraction, vocal separation, transcription, subtitle generation, and translation.

        :param video_path: path of the video
        :param separate: whether to separate vocals from music or not
        :param translate_to: lanuage to translate subtitles to. Default is None
        """
        # get audio from video
        audio = self.get_audio(video_path)

        # separate vocals from music to improve transcription
        if separate:
            audio = self.get_vocals()

        # extract text and language
        language, segments = self.transcribe(audio=audio)

        # get srt file path
        subtitle_file = self.generate_subtitle_file(
            segments=segments
        )

        # translate srt file and get new file path
        if translate_to:
            subtitle_file = self.translate_subtitles(translate_to)

        # Generate text clips from subtitles
        subtitles = self.generate_text_clips(subtitle_file)

        # Create a composite video with the text clips
        final_video = CompositeVideoClip([self.video, *subtitles])

        # Write the final video to a file
        final_video.write_videofile(f"{self.output_directory}/{self.filename}_{self.language}.mp4", codec='libx264')


if __name__ == '__main__':
    video = "audio/ohno.mp4"
    caption = Video_captionning()
    caption.run(video_path=video, separate=False, translate_to="fr")
