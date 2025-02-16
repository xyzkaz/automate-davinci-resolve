import traceback
from contextlib import ContextDecorator

from ...extended_resolve import davinci_resolve_module
from ...utils import log
from ..errors import UserError


class LoadingWindow(ContextDecorator):
    instances: list["LoadingWindow"] = []

    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message

        self.ui_dispatcher = davinci_resolve_module.create_ui_dispatcher()
        self._window = None

    def __enter__(self):
        ui = self.ui_dispatcher._ui_manager
        disp = self.ui_dispatcher._ui_dispatcher

        window = disp.AddWindow(
            {
                "WindowTitle": f"Smart Edit - {self.title}",
                "ID": "SmartEditLoading",
                "Geometry": [500, 500, 500, 100],
            },
            [
                ui.Label(
                    {
                        "ID": "Message",
                        "Text": self.message,
                        "Alignment": {
                            "AlignVCenter": True,
                            "AlignHCenter": True,
                        },
                        "WordWrap": True,
                    }
                ),
            ],
        )
        window.On.SmartEditLoading.Close = lambda ev: disp.ExitLoop()
        window.Show()
        disp.StepLoop()

        self._window = window
        self.instances.append(self)

        return self

    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type is None:
            self._set_message("Finish")
            self.ui_dispatcher._ui_dispatcher.ExitLoop()
        elif issubclass(exc_type, UserError):
            log.error(exc)
            self._set_message(f"Error:\n{exc}")
            self.ui_dispatcher._ui_dispatcher.RunLoop()
        else:
            traceback.print_exc()
            self._set_message(f"Unexpected error occurred. Check console for details.")
            self.ui_dispatcher._ui_dispatcher.RunLoop()

        self.instances.remove(self)
        self._window.Hide()

        return True

    def _set_message(self, message: str):
        items = self._window.GetItems()
        items["Message"]["Text"] = message
        self.ui_dispatcher._ui_dispatcher.StepLoop()

    @classmethod
    def set_message(cls, message: str):
        log.info(f"{cls.instances[-1].title} - {message}")
        cls.instances[-1]._set_message(message)
