import pygame
import math
import random
from effects.splatter import SplatterParticle



class BaseEnemy(pygame.sprite.Sprite):
    """
    Base class for all enemy types.
    Subclasses override:
        - self.type
        - movement_update()
        - attack_update()
        - collision_effect()
    """

    def __init__(self, pos, width, height, speed=2.0, level=1):
        super().__init__()

        # Shared geometry
        self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(0, 0, 48, 48)
        self.rect.center = self.pos

        self.width = width
        self.height = height
        self.speed = speed
        self.level = level

        # Subclasses will set this
        self.type = "BASE"

        # Animation
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.wing_frame = 0
        self.wing_timer = 0
        self.wing_speed = 100  # ms per flap

        # Targeting helpers
        self.target_pos = pygame.Vector2(pos)
        self.player_last_seen = pygame.Vector2(pos)

    # ============================================================
    #   SHARED DRAWING HELPERS (subclasses can override)
    # ============================================================
    def draw_body(self):
        """Default bug body — subclasses override for unique visuals."""
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (20, 120, 20), (10, 14, 28, 20))
        pygame.draw.circle(surf, (10, 80, 10), (24, 18), 10)
        pygame.draw.polygon(surf, (150, 0, 0),
                            [(24, 34), (20, 42), (28, 42)])
        return surf

    def draw_wings(self, open_state=True):
        """Default wing animation — subclasses can override or disable."""
        wings = pygame.Surface((48, 48), pygame.SRCALPHA)
        color = (180, 220, 255, 180)

        if open_state:
            pygame.draw.polygon(wings, color, [(24, 10), (6, 20), (24, 22)])
            pygame.draw.polygon(wings, color, [(24, 10), (42, 20), (24, 22)])
        else:
            pygame.draw.polygon(wings, color, [(24, 14), (12, 22), (24, 22)])
            pygame.draw.polygon(wings, color, [(24, 14), (36, 22), (24, 22)])

        return wings

    def animate_wings(self):
        now = pygame.time.get_ticks()
        if now - self.wing_timer > self.wing_speed:
            self.wing_timer = now
            self.wing_frame = 1 - self.wing_frame

        wings = self.draw_wings(open_state=(self.wing_frame == 0))
        body = self.draw_body()

        self.image.fill((0, 0, 0, 0))
        self.image.blit(wings, (0, 0))
        self.image.blit(body, (0, 0))

    # ============================================================
    #   OVERRIDABLE BEHAVIOR HOOKS
    # ============================================================
    def movement_update(self, player_pos):
        """Subclasses override with movement logic."""
        pass

    def attack_update(self, player_pos):
        """Subclasses override with shooting/dashing/etc."""
        pass

    def collision_effect(self, player):
        """Subclasses override with damage/stun/explosion/etc."""
        pass

    # ============================================================
    #   MAIN UPDATE LOOP
    # ============================================================
    def update(self, **kwargs):
        player_pos = kwargs.get("player_pos")

        # Shared animation
        self.animate_wings()

        # Subclass movement
        self.movement_update(player_pos)

        # Subclass attack logic
        self.attack_update(player_pos)

        # Update rect
        self.rect.center = self.pos

    # ============================================================
    #   UTILITY HELPERS FOR SUBCLASSES
    # ============================================================
    def move_toward(self, target, speed_mult=1.0):
        direction = (target - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed * speed_mult

    def distance_to(self, target):
        return self.pos.distance_to(target)

    def angle_to(self, target):
        direction = (target - self.pos)
        return math.degrees(math.atan2(-direction.y, direction.x))

    # Death Splatter Effect
    def spawn_splatter(self, groups, color=(255, 50, 50)):
        for _ in range(12):
            p = SplatterParticle(self.pos, color)
            groups["all_sprites"].add(p)
