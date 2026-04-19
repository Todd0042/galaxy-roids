from .base_boss import BaseBoss

class Boss3(BaseBoss):
    """
    Boss 3 — Template
    Add movement + attacks later.
    """
    def __init__(self, screen_w, screen_h, level, speed):
        super().__init__(screen_w, screen_h, level, speed)

        self.max_health = 1000 * (1.25 ** (level - 1))
        self.health = self.max_health

        # TODO: Add sprite + attacks
