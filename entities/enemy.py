import pygame
import random
import math


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, speed=2.0, level=1):
        super().__init__()

        # Animation state
        self.wing_frame = 0
        self.wing_timer = 0
        self.wing_speed = 100  # ms per flap

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

    # --------------------------
    #   DRAW BUG BODY
    # --------------------------
    def draw_body(self):
        body = pygame.Surface((48, 48), pygame.SRCALPHA)

        # Main body (dark green oval)
        pygame.draw.ellipse(body, (20, 120, 20), (10, 14, 28, 20))

        # Head (darker)
        pygame.draw.circle(body, (10, 80, 10), (24, 18), 10)

        # Stinger
        pygame.draw.polygon(body, (150, 0, 0),
                            [(24, 34), (20, 42), (28, 42)])

        return body

    # --------------------------
    #   DRAW WINGS (OPEN/CLOSED)
    # --------------------------
    def draw_wings(self, open_state=True):
        wings = pygame.Surface((48, 48), pygame.SRCALPHA)

        color = (180, 220, 255, 180)  # translucent blue

        if open_state:
            # Wide wings
            pygame.draw.polygon(wings, color,
                                [(24, 10), (6, 20), (24, 22)])
            pygame.draw.polygon(wings, color,
                                [(24, 10), (42, 20), (24, 22)])
        else:
            # Folded wings
            pygame.draw.polygon(wings, color,
                                [(24, 14), (12, 22), (24, 22)])
            pygame.draw.polygon(wings, color,
                                [(24, 14), (36, 22), (24, 22)])

        return wings

    # --------------------------
    #   WING ANIMATION
    # --------------------------
    def animate_wings(self):
        now = pygame.time.get_ticks()
        if now - self.wing_timer > self.wing_speed:
            self.wing_timer = now
            self.wing_frame = 1 - self.wing_frame  # toggle 0/1

        wings = self.draw_wings(open_state=(self.wing_frame == 0))
        body = self.draw_body()

        # Composite final sprite
        self.image.fill((0, 0, 0, 0))
        self.image.blit(wings, (0, 0))
        self.image.blit(body, (0, 0))

    # --------------------------
    #       UPDATE LOOP
    # --------------------------
    def update(self, **kwargs):
        player_pos = kwargs.get("player_pos")

        # Animate wings every frame
        self.animate_wings()

        # ==========================
        #     FORMATION MOVEMENT
        # ==========================
        if self.state == "FORMATION":
            t = pygame.time.get_ticks() * 0.002
            offset_x = math.sin(t + self.slot_pos.y * 0.01) * 30
            offset_y = math.cos(t + self.slot_pos.x * 0.01) * 15

            target = pygame.Vector2(
                self.slot_pos.x + offset_x,
                self.slot_pos.y + offset_y
            )

            self.pos += (target - self.pos) * 0.1

            # Random dive
            if random.random() < 0.003 and player_pos is not None:
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
            if self.pos.distance_to(self.slot_pos) > 550:
                self.state = "FORMATION"

        # Update rect
        self.rect.center = self.pos
