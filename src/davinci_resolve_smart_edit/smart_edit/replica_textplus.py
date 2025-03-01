import itertools
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import srt

from ..extended_resolve import davinci_resolve_module
from ..extended_resolve.media_pool_item import MediaPoolItem
from ..extended_resolve.resolve import MediaPoolItemInsertInfo
from ..extended_resolve.timecode import Timecode
from ..extended_resolve.timeline import Timeline
from ..extended_resolve.timeline_item import TimelineItem
from ..extended_resolve.track import TrackHandle
from .errors import UserError
from .smart_edit_bin import SmartEditBin
from .ui.loading_window import LoadingWindow
from ..utils.math import FrameRange
from .constants import GeneratedTrackName


class ReplicaTextPlus:
    SMART_EDIT_CLIP_ID = "ReplicaTextPlus"

    @classmethod
    def generate_textplus_clips(cls, auto_snap: bool):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        media_pool_item = SmartEditBin.get_or_import_replica_textplus()
        active_subtitle_track_handle = next((e for e in timeline.iter_tracks("subtitle") if timeline.get_track_enabled(e)), None)

        if active_subtitle_track_handle is None:
            raise UserError("Failed to find enabled subtitle track")

        subtitle_timeline_items = list(timeline.iter_items_in_track(active_subtitle_track_handle))
        subtitle_ranges = cls._compute_subtitle_insert_ranges(timeline, subtitle_timeline_items, auto_snap)

        track_handle = timeline.get_or_add_track_by_name("video", GeneratedTrackName.TEXT)

        with timeline.rollback_playhead_on_exit():
            old_items = list(timeline.iter_items_in_track(track_handle))
            LoadingWindow.set_message(f"Deleting {len(old_items)} clips...")
            timeline.delete_items(old_items)

            LoadingWindow.set_message(f"Inserting {len(subtitle_ranges)} clips...")
            textplus_timeline_items = resolve.insert_to_timeline(
                [
                    MediaPoolItemInsertInfo(
                        media_pool_item=media_pool_item,
                        start_frame=subtitle_range.start,
                        end_frame=subtitle_range.end,
                        track_handle=track_handle,
                    )
                    for subtitle_range in subtitle_ranges
                ]
            )

            LoadingWindow.set_message(f"Setting {len(textplus_timeline_items)} Text+ content...")
            for textplus_item, subtitle_item in zip(textplus_timeline_items, subtitle_timeline_items):
                textplus_tool = textplus_item._item.GetFusionCompByIndex(1).Template
                textplus_tool.SetInput("StyledText", subtitle_item._item.GetName())

        timeline.set_track_locked(track_handle, True)

    @classmethod
    def copy_style_for_all(cls, source_item: MediaPoolItem):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        dst_timeline_items = list(timeline.iter_items(lambda item: cls._is_replicate_textplus_clip(item), track_type="video"))

        LoadingWindow.set_message(f"Copying Style to {len(dst_timeline_items)} clips...")
        cls.copy_style_for_clips(dst_timeline_items, source_item)

    @classmethod
    def copy_style_for_track(cls, track_handle: TrackHandle, source_item: MediaPoolItem):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        dst_timeline_items = list(timeline.iter_items_in_track(track_handle, lambda item: cls._is_replicate_textplus_clip(item)))

        LoadingWindow.set_message(f"Copying Style to {len(dst_timeline_items)} clips at track {track_handle.get_short_name()}...")
        cls.copy_style_for_clips(dst_timeline_items, source_item)

    @classmethod
    def copy_style_for_clip(cls, destinated_item: TimelineItem, source_item: MediaPoolItem):
        cls.copy_style_for_clips([destinated_item], source_item)

    @classmethod
    def copy_style_for_clips(cls, destinated_items: list[TimelineItem], source_item: MediaPoolItem):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()

        with (
            timeline.rollback_playhead_on_exit(),
            resolve.temp_timeline_item(source_item) as src_timeline_item,
        ):
            cls._copy_style(src_timeline_item, destinated_items)

    @classmethod
    def export_srt_for_track(cls, track_handle: TrackHandle, file_path: Path):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()

        LoadingWindow.set_message(f"Collecting subtitle content...")

        subtitle_timeline_items = timeline.iter_items_in_track(track_handle, lambda item: cls._is_replicate_textplus_clip(item))
        subtitles = cls._transform_to_subtitles(timeline, subtitle_timeline_items)

        LoadingWindow.set_message(f"Exporting {len(subtitles)} subtitles to file `{file_path}` ...")

        file_content = srt.compose(subtitles)
        file_path.write_text(file_content, encoding="utf-8")

    @classmethod
    def import_srt_for_track(cls, source_timeline_item: TimelineItem, file_path: Path):
        LoadingWindow.set_message(f"Reading srt file `{file_path}`...")

        file_content = file_path.read_text(encoding="utf-8")

        try:
            subtitles = list(srt.parse(file_content))
        except:
            traceback.print_exc()
            raise UserError(f"Failed to parse srt file `{file_path}`. See console for details.")

        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        track_handle = source_timeline_item.get_track_handle()

        src_comp = source_timeline_item._item.GetFusionCompByIndex(1)
        src_tool = src_comp.Template
        src_settings = src_comp.CopySettings(src_tool)

        old_items = list(timeline.iter_items_in_track(track_handle))
        LoadingWindow.set_message(f"Deleting {len(old_items)} clips...")
        timeline.delete_items(old_items)

        media_pool_item = SmartEditBin.get_or_import_replica_textplus()
        if media_pool_item is None:
            raise Exception(f"Failed to import clip `{SmartEditBin.ClipName.REPLICA_TEXTPLUS}`")

        LoadingWindow.set_message(f"Inserting {len(subtitles)} clips...")
        insert_infos = [
            MediaPoolItemInsertInfo(
                media_pool_item=media_pool_item,
                start_frame=Timecode.from_timedelta(subtitle.start, timeline.get_timecode_settings(), False).get_frame(True),
                end_frame=Timecode.from_timedelta(subtitle.end, timeline.get_timecode_settings(), False).get_frame(True),
                track_handle=track_handle,
            )
            for subtitle in subtitles
        ]
        inserted_items = resolve.insert_to_timeline(insert_infos)

        LoadingWindow.set_message(f"Setting {len(subtitles)} clips content...")
        for i, item in enumerate(inserted_items):
            if item is None:
                raise UserError(f"Failed to insert clip `{SmartEditBin.ClipName.REPLICA_TEXTPLUS}` with info {insert_infos[i]}")

            tool = item._item.GetFusionCompByIndex(1).Template
            tool.SetInput("StyledText", subtitles[i].content)

        cls._copy_style_from_settings(src_settings, inserted_items)

    @classmethod
    def _transform_to_subtitles(cls, timeline: Timeline, timeline_items: Iterable[TimelineItem]):
        subtitles = []

        for item in timeline_items:
            subtitles.append(
                srt.Subtitle(
                    index=None,
                    start=timeline.get_item_start_timecode(item).get_timedelta(False),
                    end=timeline.get_item_end_timecode(item).get_timedelta(False),
                    content=item._item.GetFusionCompByIndex(1).Template.GetInput("StyledText"),  # TODO: support character level styling
                )
            )

        return subtitles

    @classmethod
    def _is_replicate_textplus_clip(cls, item: TimelineItem):
        if item._item.GetFusionCompCount() == 0:
            return False

        comp = item._item.GetFusionCompByIndex(1)

        if comp.Template is None:
            return False

        return comp.Template.GetData("SmartEdit.ClipId") == cls.SMART_EDIT_CLIP_ID

    @classmethod
    def _copy_style(cls, src_item: TimelineItem, dst_items: Iterable[TimelineItem]):
        src_comp = src_item._item.GetFusionCompByIndex(1)
        src_tool = src_comp.Template
        src_settings = src_comp.CopySettings(src_tool)

        cls._copy_style_from_settings(src_settings, dst_items)

    @classmethod
    def _copy_style_from_settings(cls, src_settings: dict, dst_items: Iterable[TimelineItem]):
        new_settings = src_settings

        for dst_item in dst_items:
            dst_comp = dst_item._item.GetFusionCompByIndex(1)
            dst_tool = dst_comp.Template
            old_settings = dst_comp.CopySettings(dst_tool)

            cls._find_text_input(new_settings)["Value"] = cls._find_text_input(old_settings)["Value"]
            new_settings["Tools"]["Template"]["Inputs"]["GlobalOut"] = old_settings["Tools"]["Template"]["Inputs"]["GlobalOut"]
            new_settings["Tools"]["Template"]["CustomData"] = old_settings["Tools"]["Template"]["CustomData"]

            dst_tool.LoadSettings(new_settings)

    @classmethod
    def _find_text_input(cls, textplus_settings):
        textplus_tool = next((tool for tool in textplus_settings["Tools"].values() if tool["__ctor"] == "TextPlus"))
        character_level_styling_tool = next((tool for tool in textplus_settings["Tools"].values() if tool["__ctor"] == "StyledTextCLS"), None)

        if character_level_styling_tool is not None:
            return character_level_styling_tool["Inputs"]["Text"]
        else:
            return textplus_tool["Inputs"]["StyledText"]

    @classmethod
    def _compute_subtitle_insert_ranges(cls, timeline: Timeline, subtitle_timeline_items: list[TimelineItem], auto_snap: bool):
        subtitle_ranges = [FrameRange(item._item.GetStart(), item._item.GetEnd()) for item in subtitle_timeline_items]

        if not subtitle_ranges or not auto_snap:
            return subtitle_ranges

        snap_target_track_handle = cls._get_audio_track_with_most_clips(timeline)
        snap_target_ranges = [FrameRange(item._item.GetStart(), item._item.GetEnd()) for item in timeline.iter_items_in_track(snap_target_track_handle)]

        return cls._snap_ranges(subtitle_ranges, snap_target_ranges)

    @classmethod
    def _get_audio_track_with_most_clips(cls, timeline: Timeline):
        return sorted(timeline.iter_tracks("audio"), key=lambda t: len(list(timeline.iter_items_in_track(t))), reverse=True)[0]

    @classmethod
    def _snap_ranges(cls, from_ranges: list[FrameRange], to_ranges: list[FrameRange]) -> list[FrameRange]:
        if not to_ranges:
            return from_ranges

        to_ranges = cls._fill_ranges_gap(to_ranges)
        associated_ranges = []

        for from_range in from_ranges:
            to_ranges = list(itertools.dropwhile(lambda to_range: not FrameRange.is_overlapped(from_range, to_range), to_ranges))
            associable_ranges = [
                to_range
                for to_range in itertools.takewhile(lambda to_range: FrameRange.is_overlapped(from_range, to_range), to_ranges)
                if FrameRange.is_overlapped_by_percentage(from_range, to_range)
            ]

            if len(associable_ranges) > 0:
                associated_ranges.append(FrameRange(associable_ranges[0].start, associable_ranges[-1].end))
            else:
                associated_ranges.append(None)

        snapped_ranges = []

        for i, from_range in enumerate(from_ranges):
            associated_range = associated_ranges[i]

            if associated_range is None:
                snapped_ranges.append(from_range)
            else:
                snapped_start = associated_range.start
                snapped_end = associated_range.end

                if i > 0:
                    snapped_start = max(snapped_start, snapped_ranges[-1].end)

                if i < len(from_ranges) - 1:
                    may_overlap_with_next_range = associated_ranges[i + 1] is not None and FrameRange.is_overlapped(associated_range, associated_ranges[i + 1])
                    if may_overlap_with_next_range:
                        snapped_end = min(snapped_end, from_ranges[i + 1].start)

                snapped_ranges.append(FrameRange(snapped_start, snapped_end))

        return snapped_ranges

    @classmethod
    def _fill_ranges_gap(cls, ranges: list[FrameRange]) -> list[FrameRange]:
        filled_ranges = []

        for i, curr_range in enumerate(ranges[:-1]):
            next_range = ranges[i + 1]

            filled_ranges.append(curr_range)

            if next_range.start > curr_range.end:
                filled_ranges.append(FrameRange(curr_range.end, next_range.start))

        filled_ranges += ranges[-1:]

        return filled_ranges
