import pygame
import random
import math


class GlobEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, speed=1.2, level=1):
        super().__init__()

        # Animation state
        self.wobble_timer = 0
        self.wobble_speed = 120  # ms
        self.wobble_amount = 3   # pixels

        # Composite image
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        # Movement + AI
        self.pos = pygame.Vector2(pos)
        self.slot_pos = pygame.Vector2(pos)
        self.width = width
        self.height = height
        self.speed = speed
        self.level = level

        self.state = "FORMATION"
        self.target_pos = pygame.Vector2(pos)

        # Trap effect duration
        self.trap_duration = 800  # ms player is slowed

    # --------------------------
    #   DRAW GLOB BODY
    # --------------------------
    def draw_glob(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)

        # Base snot color
        base = (80, 255, 120, 180)  # translucent green

        # Main blob
        pygame.draw.ellipse(surf, base, (6, 8, 36, 32))

        # Highlights
        pygame.draw.ellipse(surf, (150, 255, 180, 200), (14, 14, 12, 10))
        pygame.draw.ellipse(surf, (150, 255, 180, 200), (24, 20, 10, 8))

        # Drips
        pygame.draw.ellipse(surf, base, (18, 32, 12, 12))
        pygame.draw.ellipse(surf, base, (26, 30, 10, 14))

        return surf

    # --------------------------
    #   WOBBLE ANIMATION
    # --------------------------
    def animate_wobble(self):
        now = pygame.time.get_ticks()
        wobble_offset = 0

        if now - self.wobble_timer > self.wobble_speed:
            self.wobble_timer = now
            wobble_offset = random.randint(-self.wobble_amount, self.wobble_amount)

        glob = self.draw_glob()

        # Composite final sprite
        self.image.fill((0, 0, 0, 0))
        self.image.blit(glob, (0, wobble_offset))

    # --------------------------
    #       UPDATE LOOP
    # --------------------------
    def update(self, **kwargs):
        player_pos = kwargs.get("player_pos")

        # Animate wobble
        self.animate_wobble()

        # ==========================
        #     FORMATION MOVEMENT
        # ==========================
        if self.state == "FORMATION":
            t = pygame.time.get_ticks() * 0.002
            offset_x = math.sin(t + self.slot_pos.y * 0.01) * 20
            offset_y = math.cos(t + self.slot_pos.x * 0.01) * 10

            target = pygame.Vector2(
                self.slot_pos.x + offset_x,
                self.slot_pos.y + offset_y
            )

            self.pos += (target - self.pos) * 0.08

            # Random dive
            if random.random() < 0.002 and player_pos is not None:
                self.state = "DIVING"
                self.target_pos = pygame.Vector2(player_pos)

        # ==========================
        #        DIVING MODE
        # ==========================
        elif self.state == "DIVING":
            if player_pos is None:
                return

            direction = (player_pos - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()

            self.pos += direction * self.speed

            # Return to formation if too far
            if self.pos.distance_to(self.slot_pos) > 500:
                self.state = "FORMATION"

        # Update rect
        self.rect.center = self.pos
