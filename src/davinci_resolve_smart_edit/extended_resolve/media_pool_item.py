from ..resolve_types import PyRemoteMediaPoolItem
from .timecode import TimecodeUtils


class MediaPoolItem:
    def __init__(self, _item: PyRemoteMediaPoolItem):
        self._item = _item

    def get_clip_name(self) -> str:
        return self._item.GetClipProperty("Clip Name")

    def get_type(self) -> str:
        return self._item.GetClipProperty("Type")

    def get_frame_rate(self) -> float:
        return self._item.GetClipProperty("FPS")

    def get_duration(self):
        fps = self.get_frame_rate()
        duration_timecode = self._item.GetClipProperty("Duration")

        return TimecodeUtils.str_to_frame(duration_timecode, fps)

    def get_duration_as_timedelta(self):
        fps = self.get_frame_rate()
        duration_timecode = self._item.GetClipProperty("Duration")

        return TimecodeUtils.str_to_timedelta(duration_timecode, fps)

    def get_keyword(self) -> str:
        return self._item.GetClipProperty("Keyword")
