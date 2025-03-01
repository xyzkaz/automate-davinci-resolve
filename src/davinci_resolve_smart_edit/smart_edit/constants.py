from enum import Enum


class EffectType(Enum):
    TEXT_STYLE = 0
    # TEXT_VISUAL_EFFECT =
    VISUAL_EFFECT = 1
    SOUND_EFFECT = 2
    TRANSITION = 3
    BACKGROUND_MUSIC = 4


class GeneratedTrackName:
    EFFECT_CONTROL = "Generated Control"
    TEXT = "Generated Text+"
    VISUAL_EFFECT = "Generated Effect"
    SOUND_EFFECT = "Generated SE"


EFFECT_TRACK_MAP = {
    EffectType.VISUAL_EFFECT: ("video", GeneratedTrackName.VISUAL_EFFECT),
    EffectType.SOUND_EFFECT: ("audio", GeneratedTrackName.SOUND_EFFECT),
}
