class InputSettings:
    def __init__(self, _settings: dict):
        self._settings = _settings


class TextPlusToolSettings:
    def __init__(self, _settings: dict):
        self._settings = _settings

    def get_text_input(self):
        return InputSettings(self._settings["Inputs"]["StyledText"])


class CharacterLevelStylingToolSettings:
    def __init__(self, _settings: dict):
        self._settings = _settings

    def get_text_input(self):
        return InputSettings(self._settings["Inputs"]["Text"])

    @property
    def style_array(self):
        return self._settings["Inputs"]["CharacterLevelStyling"]["Value"]["Array"]

    @style_array.setter
    def style_array(self, value):
        self._settings["Inputs"]["CharacterLevelStyling"]["Value"]["Array"] = value


class TextPlusSettings:
    def __init__(self, _settings: dict):
        self._settings = _settings

    def get_textplus_tool(self):
        _tool = next((tool for tool in self._settings["Tools"].values() if tool["__ctor"] == "TextPlus"))
        return TextPlusToolSettings(_tool)

    def find_character_level_styling(self):
        _tool = next((tool for tool in self._settings["Tools"].values() if tool["__ctor"] == "StyledTextCLS"), None)
        return CharacterLevelStylingToolSettings(_tool) if _tool is not None else None

    def get_text_input(self):
        textplus_tool = self.get_textplus_tool()
        character_level_styling_tool = self.find_character_level_styling()

        if character_level_styling_tool is not None:
            return character_level_styling_tool.get_text_input()
        else:
            return textplus_tool.get_text_input()
