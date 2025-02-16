from ..extended_resolve import davinci_resolve_module
from ..extended_resolve.media_pool_item import MediaPoolItem
from ..extended_resolve.resolve import MediaPoolItemInsertInfo
from ..extended_resolve.timeline import Timeline
from ..extended_resolve.timeline_item import TimelineItem
from .errors import UserError
from .smart_edit_bin import SmartEditBin
from .ui.loading_window import LoadingWindow


class EffectControl:
    SMART_EDIT_CLIP_ID = "EffectControl"
    TRACK_NAME = "Generated Control"

    @classmethod
    def generate_effect_control_clips(cls):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()

        media_pool_item = SmartEditBin.get_or_import_effect_control()

        if media_pool_item is None:
            raise Exception(f"Failed to import clip `{SmartEditBin.ClipName.EFFECT_CONTROL}`")

        textplus_track_handle = timeline.find_track_by_name("video", "Generated Text+")

        if textplus_track_handle is None:
            raise UserError("Missing `Generated Text+` track")

        track_handle = cls._get_or_add_effect_control_track(timeline)

        with timeline.rollback_playhead_on_exit():
            old_items = list(timeline.iter_items_in_track(track_handle))
            LoadingWindow.set_message(f"Deleting {len(old_items)} clips...")
            timeline.delete_items(old_items)

            textplus_items = list(timeline.iter_items_in_track(textplus_track_handle))
            LoadingWindow.set_message(f"Inserting {len(textplus_items)} clips...")
            resolve.insert_to_timeline(
                [
                    MediaPoolItemInsertInfo(
                        media_pool_item=media_pool_item,
                        start_frame=textplus_item._item.GetStart(),
                        frames=textplus_item._item.GetDuration(),
                        track_handle=track_handle,
                    )
                    for textplus_item in textplus_items
                ]
            )

        timeline.set_track_locked(track_handle, True)

    @classmethod
    def reload_all(cls):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        media_pool_item = SmartEditBin.get_or_import_effect_control()

        if media_pool_item is None:
            raise Exception(f"Failed to import clip `{SmartEditBin.ClipName.EFFECT_CONTROL}`")

        dst_items = list(timeline.iter_items(lambda item: cls._is_effect_control_clip(item), track_type="video"))

        cls._reinsert_clips(timeline, dst_items, media_pool_item)

    @classmethod
    def reload_clip(cls, destinated_item: TimelineItem):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        media_pool_item = SmartEditBin.get_or_import_effect_control()

        if media_pool_item is None:
            raise Exception(f"Failed to import clip `{SmartEditBin.ClipName.EFFECT_CONTROL}`")

        cls._reinsert_clips(timeline, [destinated_item], media_pool_item)

    @classmethod
    def apply_effect_for_all(cls):
        print("apply_effect_for_all")

    @classmethod
    def apply_effect_for_clip(cls, destinated_item: TimelineItem):
        print("apply_effect_for_clip")

    @classmethod
    def _get_or_add_effect_control_track(cls, timeline: Timeline):
        track_handle = timeline.get_or_add_track_by_name("video", cls.TRACK_NAME)
        timeline.set_track_enabled(track_handle, False)

        return track_handle

    @classmethod
    def _is_effect_control_clip(cls, item: TimelineItem):
        if item._item.GetFusionCompCount() == 0:
            return False

        comp = item._item.GetFusionCompByIndex(1)

        if comp.Template is None:
            return False

        return comp.Template.GetData("SmartEdit.ClipId") == cls.SMART_EDIT_CLIP_ID

    @classmethod
    def _reinsert_clips(cls, timeline: Timeline, effect_control_items: list[TimelineItem], effect_control_media_pool_item: MediaPoolItem):
        resolve = davinci_resolve_module.get_resolve()
        all_keywords = [cls._get_selected_keywords(item) for item in effect_control_items]
        insert_infos = [
            MediaPoolItemInsertInfo(
                media_pool_item=effect_control_media_pool_item,
                start_frame=item._item.GetStart(),
                end_frame=item._item.GetEnd(),
                track_handle=item.get_track_handle(),
            )
            for item in effect_control_items
        ]

        with timeline.rollback_playhead_on_exit():
            LoadingWindow.set_message(f"Deleting {len(effect_control_items)} clips...")
            timeline.delete_items(effect_control_items)
            LoadingWindow.set_message(f"Reinserting {len(insert_infos)} clips...")
            new_timeline_items = resolve.insert_to_timeline(insert_infos)

        for i, (item, keywords) in enumerate(zip(new_timeline_items, all_keywords)):
            if item is None:
                raise UserError(f"Failed to insert clips `{SmartEditBin.ClipName.EFFECT_CONTROL}` with info {insert_infos[i]}")

            cls._set_keywords(item, keywords)

    @classmethod
    def _get_selected_keywords(cls, effect_control_item: TimelineItem):
        comp = effect_control_item._item.GetFusionCompByIndex(1)
        tool = comp.Template
        settings = comp.CopySettings(tool)
        inputs = settings["Tools"]["Template"]["Inputs"]
        user_controls = settings["Tools"]["Template"]["UserControls"]

        keywords = []

        for id, input in inputs.items():
            if id.startswith("Keyword") and input["Value"]:
                keywords.append(user_controls[id]["LINKS_Name"])

        return keywords

    @classmethod
    def _set_keywords(cls, effect_control_item: TimelineItem, keywords: list[str]):  # TODO: unset unselected keywords
        comp = effect_control_item._item.GetFusionCompByIndex(1)
        tool = comp.Template
        settings = comp.CopySettings(tool)
        user_controls = settings["Tools"]["Template"]["UserControls"]

        for id, control in user_controls.items():
            if id.startswith("Keyword") and control["LINKS_Name"] in keywords:
                tool.SetInput(id, 1.0)
