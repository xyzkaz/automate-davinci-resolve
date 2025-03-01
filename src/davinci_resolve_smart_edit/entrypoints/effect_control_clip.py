from ..resolve_types import PyRemoteComposition
from ..smart_edit.effect_control import EffectControl
from ..smart_edit.ui.loading_window import LoadingWindow
from .script_utils import ScriptUtils


def on_reload_for_all():
    with LoadingWindow("Effect Control", "Reloading Template..."):
        EffectControl.reload_all()


def on_reload_for_clip(composition: PyRemoteComposition):
    with LoadingWindow("Effect Control", "Reloading Template..."):
        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        EffectControl.reload_clip(timeline_item)


def on_apply_effect_for_all():
    with LoadingWindow("Effect Control", "Applying Effects..."):
        EffectControl.apply_effect_for_all()


def on_apply_effect_for_clip(composition: PyRemoteComposition):
    with LoadingWindow("Effect Control", "Applying Effects..."):
        timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
        EffectControl.apply_effect_for_clip(timeline_item)


def on_toggle_keyword(composition: PyRemoteComposition, keyword: str):
    timeline_item = ScriptUtils.get_timeline_item_from_composition(composition)
    EffectControl.toggle_keyword(timeline_item, keyword)
