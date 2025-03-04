from types import ModuleType

from ..resolve_types import PyRemoteFusion, PyRemoteResolve
from .resolve import Resolve
from .ui_dispatcher import UiDispatcher


class DavinciResolveModule:
    _module: ModuleType = None
    _resolve: PyRemoteResolve = None
    _fusion: PyRemoteFusion = None

    resolve: Resolve = None

    @classmethod
    def init(cls, _module: ModuleType, _resolve: PyRemoteResolve, _fusion: PyRemoteFusion):
        cls._module = _module
        cls._resolve = _resolve
        cls._fusion = _fusion

        cls.resolve = Resolve(cls._resolve)

    @classmethod
    def get_resolve(cls):
        return cls.resolve

    @classmethod
    def create_ui_dispatcher(cls):
        ui_manager = cls._fusion.UIManager
        ui_dispatcher = UiDispatcher(cls._module.UIDispatcher(ui_manager))

        return ui_dispatcher


get_resolve = DavinciResolveModule.get_resolve
create_ui_dispatcher = DavinciResolveModule.create_ui_dispatcher
