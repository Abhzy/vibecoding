"""
GameEngine: owns the basket and all falling objects.

Task 1: catch detection fixed (collision.py + safe list handling).
Task 2: basket movement/boundaries handled in Basket.update().
Task 3: varied spawn position, speed and timing, with an on-screen cap.
Task 4: speed boost (Space) with an on-screen indicator.
"""

import random
import pygame

from game.basket import (
    Basket,
    BOOST_DURATION_FRAMES,
    BOOST_COOLDOWN_FRAMES,
)
from game.falling_object import FallingObject
from game.collision import is_caught
from game.renderer import WIDTH, HEIGHT

MAX_MISSES = 5

# Task 3: spawning
MIN_SPAWN_INTERVAL = 25
MAX_SPAWN_INTERVAL = 70
MIN_OBJECT_SPEED = 2.0
MAX_OBJECT_SPEED = 5.0
MAX_OBJECTS_ON_SCREEN = 6
MIN_SPAWN_X_GAP = 60            # avoid spawning right on top of the previous one
SPAWN_RETRY_FRAMES = 10         # when the cap is hit, check again soon


class GameEngine:
    def __init__(self):
        self.basket = Basket(x=WIDTH / 2, y=HEIGHT - 30)
        self.objects = []
        self.frames_until_spawn = 0
        self.last_spawn_x = None
        self.score = 0
        self.misses = 0
        self.game_over = False

    # ---- Task 3: spawning ----
    def _pick_spawn_x(self):
        x = random.randint(20, WIDTH - 20)
        for _ in range(10):
            if self.last_spawn_x is None or abs(x - self.last_spawn_x) >= MIN_SPAWN_X_GAP:
                break
            x = random.randint(20, WIDTH - 20)
        return x

    def _spawn_object(self):
        x = self._pick_spawn_x()
        speed = random.uniform(MIN_OBJECT_SPEED, MAX_OBJECT_SPEED)
        self.objects.append(FallingObject(x=x, y=-14, speed=speed))
        self.last_spawn_x = x

    # ---- input ----
    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        direction = 0
        if keys_pressed[pygame.K_LEFT]:
            direction -= 1
        if keys_pressed[pygame.K_RIGHT]:
            direction += 1
        self.basket.update(direction, WIDTH)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.__init__()
        elif not self.game_over and key == pygame.K_SPACE:
            self.basket.activate_boost()

    # ---- game loop ----
    def update(self):
        if self.game_over:
            return

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            if len(self.objects) < MAX_OBJECTS_ON_SCREEN:
                self._spawn_object()
                self.frames_until_spawn = random.randint(
                    MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL
                )
            else:
                self.frames_until_spawn = SPAWN_RETRY_FRAMES

        for obj in self.objects:
            obj.update()

        basket_rect = self.basket.get_rect()

        # Task 1: split into caught/remaining instead of removing while iterating.
        remaining = []
        for obj in self.objects:
            if is_caught(basket_rect, obj):
                self.score += 1
            else:
                remaining.append(obj)
        self.objects = remaining

        missed = [o for o in self.objects if o.is_past_bottom(HEIGHT)]
        if missed:
            self.objects = [o for o in self.objects if not o.is_past_bottom(HEIGHT)]
            self.misses += len(missed)
            if self.misses >= MAX_MISSES:
                self.game_over = True

    # ---- drawing ----
    def _draw_boost_indicator(self, surface, font):
        from game import renderer
        b = self.basket
        bar_x, bar_y, bar_w, bar_h = 10, 90, 140, 12

        if b.is_boosted:
            label = "BOOST ACTIVE!"
            fraction = b.boosted_frames / BOOST_DURATION_FRAMES
            color = (255, 200, 0)
            # Gold outline around the basket while boosted.
            pygame.draw.rect(surface, color, b.get_rect().inflate(6, 6), 3)
        elif b.boost_cooldown > 0:
            label = "Boost recharging..."
            fraction = 1 - b.boost_cooldown / BOOST_COOLDOWN_FRAMES
            color = (150, 150, 150)
        else:
            label = "Boost READY (Space)"
            fraction = 1.0
            color = (80, 220, 120)

        renderer.draw_text(surface, font, label, (10, 62), color)
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_w * fraction), bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.basket, self.objects)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Misses: {self.misses}/{MAX_MISSES}", (10, 36))
        self._draw_boost_indicator(surface, font)

        if self.game_over:
            renderer.draw_banner(surface, font, f"Game Over! Final score: {self.score}. Press R to restart.")
