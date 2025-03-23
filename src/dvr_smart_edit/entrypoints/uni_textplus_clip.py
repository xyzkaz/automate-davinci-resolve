import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from ..extended_resolve import davinci_resolve_module
from ..extended_resolve.constants import MediaPoolItemType
from ..extended_resolve.media_pool_item import MediaPoolItem
from ..resolve_types import PyRemoteComposition
from ..smart_edit.errors import UserError
from ..smart_edit.ui.loading_window import LoadingWindow
from ..smart_edit.uni_textplus import UniTextPlus, UniTextPlusControl
from .script_utils import ScriptUtils


def _is_textplus_item(item: MediaPoolItem):
    return item.get_clip_type() == MediaPoolItemType.FUSION_TITLE


def on_copy_style_for_all():  # TODO: preserve style on regeneration
    with LoadingWindow("UniText+", "Copying Style..."):
        resolve = davinci_resolve_module.get_resolve()
        media_pool = resolve.get_media_pool()
        media_pool_item = media_pool.find_selected_item(_is_textplus_item)

        if media_pool_item is None:
            raise UserError("No Media Pool Text+ clip selected")

        UniTextPlus.copy_style_for_all(media_pool_item)


def on_copy_style_for_track(composition: PyRemoteComposition):
    with LoadingWindow("UniText+", "Copying Style..."):
        resolve = davinci_resolve_module.get_resolve()
        media_pool = resolve.get_media_pool()
        media_pool_item = media_pool.find_selected_item(_is_textplus_item)

        if media_pool_item is None:
            raise UserError("No Media Pool Text+ clip selected")

        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        UniTextPlus.copy_style_for_track(timeline_item.get_track_handle(), media_pool_item)


def on_copy_style_for_clip(composition: PyRemoteComposition):
    with LoadingWindow("UniText+", "Copying Style..."):
        resolve = davinci_resolve_module.get_resolve()
        media_pool = resolve.get_media_pool()
        media_pool_item = media_pool.find_selected_item(_is_textplus_item)

        if media_pool_item is None:
            raise UserError("No Media Pool Text+ clip selected")

        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        UniTextPlus.copy_style_for_clip(timeline_item, media_pool_item)


def on_export_srt_for_track(composition: PyRemoteComposition):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Smart Edit - Export Subtitle",
        initialfile="*.srt",
        filetypes=[("Subtitle files", "*.srt")],
    )

    if not file_path:
        return

    with LoadingWindow("UniText+", "Exporting Srt..."):
        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        UniTextPlus.export_srt_for_track(timeline_item.get_track_handle(), Path(file_path))


def on_import_srt_for_track(composition: PyRemoteComposition):  # TODO: preserve style
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Smart Edit - Import Subtitle",
        initialfile="*.srt",
        filetypes=[("Subtitle files", "*.srt")],
    )

    if not file_path:
        return

    with LoadingWindow("UniText+", "Importing Srt..."):
        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        UniTextPlus.import_srt_for_track(timeline_item, Path(file_path))


def on_enable_fit_to_textarea(composition: PyRemoteComposition, tool_name: str):
    if composition is None:
        return

    if composition.FindTool is None:
        # happen when drag in the clip to where not shown in preview (e.g. composition=<nil> [App: 'Resolve' on 127.0.0.1, UUID: 08934f92-4270-467a-bb2d-1148505d8e26])
        return

    tool = composition.FindTool(tool_name)

    if tool is not None:
        UniTextPlusControl.enable_fit_to_textarea(tool)


def on_disable_fit_to_textarea(composition: PyRemoteComposition, tool_name: str):
    if composition is None:
        return

    if composition.FindTool is None:
        return

    tool = composition.FindTool(tool_name)

    if tool is not None:
        UniTextPlusControl.disable_fit_to_textarea(tool)
