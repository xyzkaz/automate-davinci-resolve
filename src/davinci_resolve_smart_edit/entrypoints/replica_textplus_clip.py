import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from ..extended_resolve import davinci_resolve_module
from ..resolve_types import PyRemoteComposition
from ..smart_edit.errors import UserError
from ..smart_edit.replica_textplus import ReplicaTextPlus
from ..smart_edit.ui.loading_window import LoadingWindow
from .script_utils import ScriptUtils


def on_copy_style_for_all():  # TODO: preserve style on regeneration
    with LoadingWindow("ReplicaText+", "Copying Style..."):
        resolve = davinci_resolve_module.get_resolve()
        media_pool = resolve.get_media_pool()
        media_pool_item = media_pool.find_selected_item(lambda item: item.GetClipProperty("Type") == "Fusion Title")

        if media_pool_item is None:
            raise UserError("No Media Pool Text+ clip selected")

        ReplicaTextPlus.copy_style_for_all(media_pool_item)


def on_copy_style_for_track(composition: PyRemoteComposition):
    with LoadingWindow("ReplicaText+", "Copying Style..."):
        resolve = davinci_resolve_module.get_resolve()
        media_pool = resolve.get_media_pool()
        media_pool_item = media_pool.find_selected_item(lambda item: item.GetClipProperty("Type") == "Fusion Title")

        if media_pool_item is None:
            raise UserError("No Media Pool Text+ clip selected")

        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        ReplicaTextPlus.copy_style_for_track(timeline_item.get_track_handle(), media_pool_item)


def on_copy_style_for_clip(composition: PyRemoteComposition):
    with LoadingWindow("ReplicaText+", "Copying Style..."):
        resolve = davinci_resolve_module.get_resolve()
        media_pool = resolve.get_media_pool()
        media_pool_item = media_pool.find_selected_item(lambda item: item.GetClipProperty("Type") == "Fusion Title")

        if media_pool_item is None:
            raise UserError("No Media Pool Text+ clip selected")

        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        ReplicaTextPlus.copy_style_for_clip(timeline_item, media_pool_item)


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

    with LoadingWindow("ReplicaText+", "Exporting Srt..."):
        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        ReplicaTextPlus.export_srt_for_track(timeline_item.get_track_handle(), Path(file_path))


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

    with LoadingWindow("ReplicaText+", "Importing Srt..."):
        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        ReplicaTextPlus.import_srt_for_track(timeline_item, Path(file_path))
