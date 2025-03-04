from ..extended_resolve import davinci_resolve_module
from ..smart_edit.effect_control import EffectControl
from ..smart_edit.uni_textplus import UniTextPlus
from ..smart_edit.ui.loading_window import LoadingWindow


def on_generate_textplus_clips(auto_snap: bool):
    with LoadingWindow("UniText+", "Generating clips..."):
        UniTextPlus.generate_textplus_clips(auto_snap)


def on_generate_effect_control_clips():
    with LoadingWindow("EffectControl", "Generating clips..."):
        EffectControl.generate_effect_control_clips()


def on_debug(items):
    with LoadingWindow("Debug", "Debug..."):
        print("on_debug")


def smart_edit_menu():
    ui_dispatcher = davinci_resolve_module.create_ui_dispatcher()
    ui = ui_dispatcher._ui_manager
    disp = ui_dispatcher._ui_dispatcher

    window = disp.AddWindow(
        {
            "WindowTitle": "Smart Edit Menu",
            "ID": "SmartEditMenu",
            "Geometry": [100, 100, 300, 200],
        },
        [
            ui.VGroup(
                {"Spacing": 30},
                [
                    ui.VGroup(
                        {"Weight": 0.0},
                        [
                            ui.CheckBox(
                                {
                                    "ID": "AutoSnap",
                                    "Text": "Auto Snap",
                                    "ToolTip": "Snap Text+ clips to audio clips during generation",
                                    "Checked": True,
                                    "Weight": 0.0,
                                }
                            ),
                            ui.Button(
                                {
                                    "ID": "GenerateTextPlusClips",
                                    "Text": "Generate Text+ Clips",
                                    "ToolTip": "Generate Text+ clips according to enabled subtitle track.\nOverwrite `Generated Text+` track if already exist.",
                                    "Geometry": [0, 0, 30, 50],
                                    "Weight": 0.0,
                                }
                            ),
                        ],
                    ),
                    ui.Button(
                        {
                            "ID": "GenerateEffectControlClips",
                            "Text": "Generate EffectControl Clips",
                            "ToolTip": "Generate EffectControl clips according to `Generated Text+` track.\nOverwrite `Generated Control` track if already exist.",
                            "Geometry": [0, 0, 30, 50],
                            "Weight": 0.0,
                        }
                    ),
                    ui.Button({"ID": "Debug", "Text": "Debug", "Geometry": [0, 0, 30, 50], "Weight": 0.0}),
                ],
            ),
        ],
    )

    items = window.GetItems()

    window.On.SmartEditMenu.Close = lambda ev: disp.ExitLoop()
    window.On.GenerateTextPlusClips.Clicked = lambda ev: on_generate_textplus_clips(items["AutoSnap"].Checked)
    window.On.GenerateEffectControlClips.Clicked = lambda ev: on_generate_effect_control_clips()
    window.On.Debug.Clicked = lambda ev: on_debug(items)

    window.Show()
    disp.RunLoop()
    window.Hide()
