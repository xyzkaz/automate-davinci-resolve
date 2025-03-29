from ..resolve_types import PyRemoteTimelineItem
from .track import TrackHandle
from ..utils.math import FrameRange
from .media_pool_item import MediaPoolItem


class TimelineItem:
    def __init__(self, _item: PyRemoteTimelineItem):
        self._item = _item

    def get_track_handle(self):
        track_type, index = self._item.GetTrackTypeAndIndex()

        return TrackHandle(track_type, index)

    def get_frame_range(self):
        return FrameRange(self._item.GetStart(), self._item.GetEnd())

    def get_media_pool_item(self):
        _media_pool_item = self._item.GetMediaPoolItem()

        return MediaPoolItem(_media_pool_item) if _media_pool_item is not None else None
