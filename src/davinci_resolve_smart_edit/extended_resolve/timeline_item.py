from ..resolve_types import PyRemoteTimelineItem
from .track import TrackHandle


class TimelineItem:
    def __init__(self, _item: PyRemoteTimelineItem):
        self._item = _item

    def get_track_handle(self):
        track_type, index = self._item.GetTrackTypeAndIndex()

        return TrackHandle(track_type, index)
