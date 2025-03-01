from enum import Enum


class GeneratedTrackName:
    EFFECT_CONTROL = "Generated Control"
    TEXT = "Generated Text+"
    VISUAL_EFFECT = "Generated Effect"
    SOUND_EFFECT = "Generated SE"


class EffectType(Enum):
    TEXT_STYLE = 0
    TEXT_VISUAL_EFFECT = 1
    VISUAL_EFFECT = 2
    SOUND_EFFECT = 3
    TRANSITION = 4
    BACKGROUND_MUSIC = 5
