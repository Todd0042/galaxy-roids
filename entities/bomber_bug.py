import pygame
import random
import math


class BomberBug(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, speed=3.2, level=1):
        super().__init__()

        # Animation state
        self.wing_frame = 0
        self.wing_timer = 0
        self.wing_speed = 60  # very fast flap

        # Charge telegraph
        self.charge_timer = 0
        self.charge_flash = False

        # Composite image
        self.image = pygame.Surface((56, 56), pygame.SRCALPHA)
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
    #   DRAW BODY (Hornet)
    # --------------------------
    def draw_body(self):
        surf = pygame.Surface((56, 56), pygame.SRCALPHA)

        # Main body (yellow/black hornet stripes)
        pygame.draw.ellipse(surf, (240, 200, 0), (12, 16, 32, 24))
        pygame.draw.rect(surf, (0, 0, 0), (20, 24, 16, 4))
        pygame.draw.rect(surf, (0, 0, 0), (20, 30, 16, 4))

        # Head
        pygame.draw.circle(surf, (80, 60, 0), (28, 20), 10)

        # Stinger (glows when charging)
        stinger_color = (255, 50, 50) if self.charge_flash else (120, 0, 0)
        pygame.draw.polygon(surf, stinger_color,
                            [(28, 40), (24, 50), (32, 50)])

        return surf

    # --------------------------
    #   DRAW WINGS
    # --------------------------
    def draw_wings(self, open_state=True):
        wings = pygame.Surface((56, 56), pygame.SRCALPHA)
        color = (200, 230, 255, 180)

        if open_state:
            pygame.draw.polygon(wings, color,
                                [(28, 10), (8, 22), (28, 24)])
            pygame.draw.polygon(wings, color,
                                [(28, 10), (48, 22), (28, 24)])
        else:
            pygame.draw.polygon(wings, color,
                                [(28, 14), (16, 24), (28, 24)])
            pygame.draw.polygon(wings, color,
                                [(28, 14), (40, 24), (28, 24)])

        return wings

    # --------------------------
    #   WING ANIMATION
    # --------------------------
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

    # --------------------------
    #       UPDATE LOOP
    # --------------------------
    def update(self, **kwargs):
        player_pos = kwargs.get("player_pos")

        # Animate wings
        self.animate_wings()

        # ==========================
        #     FORMATION MOVEMENT
        # ==========================
        if self.state == "FORMATION":
            t = pygame.time.get_ticks() * 0.003
            offset_x = math.sin(t + self.slot_pos.y * 0.02) * 40
            offset_y = math.cos(t + self.slot_pos.x * 0.02) * 18

            target = pygame.Vector2(
                self.slot_pos.x + offset_x,
                self.slot_pos.y + offset_y
            )

            self.pos += (target - self.pos) * 0.12

            # Random chance to enter CHARGE mode
            if random.random() < 0.002 and player_pos is not None:
                self.state = "CHARGING"
                self.charge_timer = pygame.time.get_ticks()

        # ==========================
        #       CHARGING MODE
        # ==========================
        elif self.state == "CHARGING":
            now = pygame.time.get_ticks()

            # Flash stinger red
            self.charge_flash = (now // 100) % 2 == 0

            # After 600ms, dive at player
            if now - self.charge_timer > 600:
                self.state = "DIVING"

        # ==========================
        #        DIVING MODE
        # ==========================
        elif self.state == "DIVING":
            self.charge_flash = False

            if player_pos is None:
                return

            direction = (player_pos - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()

            # Bomber bug dives FAST
            self.pos += direction * (self.speed * 1.8)

            # Return to formation if too far
            if self.pos.distance_to(self.slot_pos) > 650:
                self.state = "FORMATION"

        # Update rect
        self.rect.center = self.pos
