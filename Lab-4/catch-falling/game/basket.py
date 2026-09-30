"""
Basket: the player-controlled catcher at the bottom of the screen.

Task 2: movement is velocity-based (accelerates and slides to a stop),
        and the basket is clamped so it never goes past either edge.
Task 4: a timed speed boost with a cooldown.
"""

import pygame

ACCELERATION = 1.0
FRICTION = 0.80

BOOST_DURATION_FRAMES = 120      # 2 seconds at 60 FPS
BOOST_COOLDOWN_FRAMES = 240      # 4 seconds at 60 FPS
BOOST_MULTIPLIER = 1.8


class Basket:
    def __init__(self, x, y, width=90, height=24, speed=5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.velocity = 0.0
        self.boosted_frames = 0
        self.boost_cooldown = 0
        self.normal_speed = speed
        self.boost_speed = speed * BOOST_MULTIPLIER

    # ---- Task 4: boost ----
    @property
    def is_boosted(self):
        return self.boosted_frames > 0

    def activate_boost(self):
        """Start a boost if one is not already running or recharging."""
        if self.boosted_frames == 0 and self.boost_cooldown == 0:
            self.boosted_frames = BOOST_DURATION_FRAMES

    def _tick_boost(self):
        if self.boosted_frames > 0:
            self.boosted_frames -= 1
            if self.boosted_frames == 0:
                self.boost_cooldown = BOOST_COOLDOWN_FRAMES
        elif self.boost_cooldown > 0:
            self.boost_cooldown -= 1
        self.speed = self.boost_speed if self.is_boosted else self.normal_speed

    # ---- Task 2: movement ----
    def update(self, direction, screen_width):
        """direction: -1 (left), 0 (none) or +1 (right)."""
        self._tick_boost()

        if direction != 0:
            self.velocity += direction * ACCELERATION
            self.velocity = max(-self.speed, min(self.speed, self.velocity))
        else:
            self.velocity *= FRICTION
            if abs(self.velocity) < 0.1:
                self.velocity = 0.0

        self.x += self.velocity

        # Clamp using the basket's own half-width so it stays fully on screen.
        half = self.width / 2
        if self.x < half:
            self.x = half
            self.velocity = 0.0
        elif self.x > screen_width - half:
            self.x = screen_width - half
            self.velocity = 0.0

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height,
        )
