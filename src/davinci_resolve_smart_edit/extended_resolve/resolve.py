from contextlib import contextmanager
from typing import NamedTuple

from ..extended_resolve.track import TrackHandle
from ..resolve_types import PyRemoteResolve
from .media_pool import MediaPool
from .media_pool_item import MediaPoolItem
from .timecode import TimecodeUtils
from .timeline import Timeline
from .timeline_item import TimelineItem


class MediaPoolItemInsertInfo(NamedTuple):
    media_pool_item: MediaPoolItem
    start_frame: int
    end_frame: int | None = None
    frames: int | None = None
    track_handle: TrackHandle | None = None


class Resolve:
    def __init__(self, _resolve: "PyRemoteResolve"):
        self._resolve = _resolve
        self._project_manager = self._resolve.GetProjectManager()

    def _get_current_project(self):
        return self._project_manager.GetCurrentProject()

    def get_current_timeline(self):
        return Timeline(self._get_current_project().GetCurrentTimeline())

    def get_media_pool(self):
        return MediaPool(self._get_current_project().GetMediaPool())

    def get_ui_manager(self):
        pass

    @contextmanager
    def temp_timeline_item(self, media_pool_item: MediaPoolItem, start_frame=None, end_frame=None):
        timeline = self.get_current_timeline()

        timecode = timeline.get_current_timecode()
        start_frame = start_frame or timecode.get_frame(True)

        item_fps = media_pool_item._item.GetClipProperty()["FPS"]
        timeline_fps = timeline.get_frame_rate()
        min_frames = max(TimecodeUtils.timedelta_to_frame(TimecodeUtils.frame_to_timedelta(1, item_fps), timeline_fps), 1)

        with timeline.temp_track("video") as track_handle:
            timeline_items = self.insert_to_timeline(
                [
                    MediaPoolItemInsertInfo(
                        media_pool_item=media_pool_item,
                        start_frame=start_frame,
                        end_frame=end_frame,
                        frames=min_frames if end_frame is None else None,
                        track_handle=track_handle,
                    )
                ]
            )
            timeline_item = timeline_items[0]

            yield timeline_item

            if timeline_item is not None:
                timeline.delete_items([timeline_item])

    def insert_to_timeline(self, insert_infos: list[MediaPoolItemInsertInfo], auto_unlock=True):
        MEDIA_TYPE_MAP = {"video": 1, "audio": 2}

        timeline = self.get_current_timeline()
        timeline_fps = timeline.get_frame_rate()
        convert_from_timeline_fps = lambda frame, fps: TimecodeUtils.timedelta_to_frame(TimecodeUtils.frame_to_timedelta(frame, timeline_fps), fps)

        resolve_clip_infos = []

        for insert_info in insert_infos:
            item_fps = insert_info.media_pool_item._item.GetClipProperty()["FPS"]

            resolve_clip_info = {
                "mediaPoolItem": insert_info.media_pool_item._item,
                "startFrame": 0,
                "endFrame": convert_from_timeline_fps(insert_info.frames or insert_info.end_frame - insert_info.start_frame, item_fps),
                "recordFrame": insert_info.start_frame,
            }

            if insert_info.track_handle is not None:
                resolve_clip_info["mediaType"] = MEDIA_TYPE_MAP[insert_info.track_handle.type]
                resolve_clip_info["trackIndex"] = insert_info.track_handle.index

            resolve_clip_infos.append(resolve_clip_info)

        track_handles_to_unlock = set(insert_info.track_handle for insert_info in insert_infos if insert_info.track_handle is not None) if auto_unlock else []

        with timeline.temp_unlock_tracks(*track_handles_to_unlock):
            inserted_items = self.get_media_pool()._media_pool.AppendToTimeline(resolve_clip_infos)
            return [TimelineItem(item) if item is not None else None for item in inserted_items]
