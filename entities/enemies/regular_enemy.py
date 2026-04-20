import pygame
import random
import math
from .base_enemy import BaseEnemy
from settings import BULLET_SPEED, BULLET_DAMAGE, PLAYER_SIZE


class RegularEnemy(BaseEnemy):
    def __init__(self, pos, width, height, speed=2.0, level=1):
        super().__init__(pos, width, height, speed, level)
        self.type = "REGULAR"

        # Circular hitbox (shmup-style)
        self.hitbox_radius = width * 0.35

        # Shooting parameters (unlocked at level 13)
        self.can_shoot = (level >= 13)
        self.shoot_cooldown = 90
        self.shoot_timer = random.randint(0, self.shoot_cooldown)

    def movement_update(self, player_pos):
        if player_pos is None:
            return

        t = pygame.time.get_ticks() * 0.002
        weave_x = math.sin(t + self.pos.y * 0.01) * 1.5
        weave_y = math.cos(t + self.pos.x * 0.01) * 1.0

        direction = (player_pos - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed
        self.pos.x += weave_x
        self.pos.y += weave_y

    def attack_update(self, player_pos):
        if not self.can_shoot or player_pos is None:
            return

        self.shoot_timer -= 1
        if self.shoot_timer > 0:
            return

        self.shoot_timer = self.shoot_cooldown
        self.fire_bullet(player_pos)

    def fire_bullet(self, player_pos):
        direction = (player_pos - self.pos)
        if direction.length() == 0:
            return

        direction = direction.normalize()

        bullet = {
            "pos": pygame.Vector2(self.pos),
            "vel": direction * BULLET_SPEED,
            "damage": BULLET_DAMAGE,
            "owner": "enemy"
        }

        self.spawned_bullet = bullet

    def collision_effect(self, player):
        pass
