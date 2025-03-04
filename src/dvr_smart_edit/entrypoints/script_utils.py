from ..extended_resolve import davinci_resolve_module
from ..resolve_types import PyRemoteComposition


class ScriptUtils:
    @classmethod
    def get_timeline_item_from_composition(cls, composition: PyRemoteComposition):
        resolve = davinci_resolve_module.get_resolve()
        timeline = resolve.get_current_timeline()
        timeline_item = timeline.find_item(lambda item: str(item._item.GetFusionCompByIndex(1)) == str(composition), track_type="video")

        return timeline_item
