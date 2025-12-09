# =============================================================================
# AudioManager - Control global de volúmenes para música y SFX
# =============================================================================

class AudioManager:
    music_volume = 0.7
    sfx_volume = 0.5

    @classmethod
    def set_music_volume(cls, value):
        cls.music_volume = max(0, min(1, value))

    @classmethod
    def set_sfx_volume(cls, value):
        cls.sfx_volume = max(0, min(1, value))
