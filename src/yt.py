from typing import Optional

from pydantic import BaseModel
import yt_dlp


class VideoFormatRaw(BaseModel):
    format_id: str
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None


class VideoInfoRaw(BaseModel):
    title: str
    formats: list[VideoFormatRaw]


class VideoFormat(BaseModel):
    format_id: int
    fps: float
    width: int
    height: int


class AudioFormat(BaseModel):
    format_id: int


class VideoInfo(BaseModel):
    title: str
    formats: list[VideoFormat | AudioFormat]


class YT:
    def __init__(self):
        ydl_opts = {}
        self._ydl = yt_dlp.YoutubeDL(ydl_opts)

    def _get_video_info_raw(self, uri: str) -> VideoInfoRaw:
        info = self._ydl.extract_info(uri, download=False)
        return VideoInfoRaw.model_validate(self._ydl.sanitize_info(info))

    def get_video_info(self, uri: str) -> VideoInfo:
        info_raw = self._get_video_info_raw(uri)
        formats: list[VideoFormat | AudioFormat] = list()
        for format in info_raw.formats:
            if not format.format_id.isdigit():
                continue
            if format.fps is None:
                formats.append(AudioFormat.model_validate(format.model_dump()))
            else:
                formats.append(VideoFormat.model_validate(format.model_dump()))
        return VideoInfo(title=info_raw.title, formats=formats)
