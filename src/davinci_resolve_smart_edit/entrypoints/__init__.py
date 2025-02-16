from types import ModuleType

from ..resolve_types import PyRemoteFusion, PyRemoteResolve


def setup_module(_module: ModuleType, _resolve: PyRemoteResolve, _fusion: PyRemoteFusion):
    from .module_utils import ModuleUtils

    ModuleUtils.reload_module()

    from ..extended_resolve.davinci_resolve_module import DavinciResolveModule

    DavinciResolveModule.init(_module, _resolve, _fusion)
