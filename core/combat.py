import pygame
from entities.projectiles import Bullet, LaserBeam, HomingMissile
from settings import LASER_FIRE_COOLDOWN, HOMING_FIRE_COOLDOWN

AXIS_OFFSET = 90


def handle_autofire(player, groups, sfx, state):
    """
    Stacking weapon system:
    1 powerup  → spread shot
    2 powerups → rapid-fire spread
    3 powerups → faster rapid-fire spread
    4 powerups → laser beam + rapid-fire spread
    5 powerups → add left homing missile
    6 powerups → add right homing missile
    """

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]

    # -------------------------------------------------------
    #   FIRE BUTTON REQUIREMENTS
    # -------------------------------------------------------
    if not player.fire_button_held and player.powerup_hits < 2:
        return

    # Single-shot mode (powerups < 2)
    if player.powerup_hits < 2:
        if not player.fire_button_held:
            return
        if state.get("single_shot_fired", False):
            return
        state["single_shot_fired"] = True
    else:
        state["single_shot_fired"] = False

    # -------------------------------------------------------
    #   GLOBAL FIRE COOLDOWN (for bullets only)
    # -------------------------------------------------------
    if player.fire_cooldown > 0:
        return

    now = pygame.time.get_ticks()

    # Pew sound cooldown
    if sfx.get("pew") and now - state["last_pew_time"] > 150:
        sfx["pew"].play()
        state["last_pew_time"] = now

    # -------------------------------------------------------
    #   SPREAD SHOT (powerup >= 1)
    # -------------------------------------------------------
    if player.powerup_hits >= 1:
        for offset in (-15, 0, 15):
            b = Bullet(player.pos, player.angle + offset, WIDTH, HEIGHT)
            groups["bullets"].add(b)
            groups["all_sprites"].add(b)
    else:
        b = Bullet(player.pos, player.angle, WIDTH, HEIGHT)
        groups["bullets"].add(b)
        groups["all_sprites"].add(b)

    # -------------------------------------------------------
    #   LASER BEAM (powerup >= 4) — OWN COOLDOWN
    # -------------------------------------------------------
    if not hasattr(player, "laser_cooldown"):
        player.laser_cooldown = 0

    if player.laser_cooldown > 0:
        player.laser_cooldown -= 1

    if player.powerup_hits >= 4 and player.laser_cooldown <= 0:
        forward = pygame.Vector2(0, -1).rotate(player.angle + AXIS_OFFSET)
        laser = LaserBeam(player.pos + forward * 20, forward, WIDTH, HEIGHT)
        groups["bullets"].add(laser)
        groups["all_sprites"].add(laser)

        player.laser_cooldown = LASER_FIRE_COOLDOWN

    # -------------------------------------------------------
    #   HOMING MISSILES (powerup >= 5) — OWN COOLDOWN
    # -------------------------------------------------------
    if not hasattr(player, "missile_cooldown"):
        player.missile_cooldown = 0

    if player.missile_cooldown > 0:
        player.missile_cooldown -= 1

    if player.powerup_hits >= 5 and player.missile_cooldown <= 0:

        forward = pygame.Vector2(0, -1).rotate(player.angle + AXIS_OFFSET)
        right   = pygame.Vector2(1, 0).rotate(player.angle + AXIS_OFFSET)

        # LEFT MISSILE
        left_offset = right * -20
        left_dir = right * -1
        m1 = HomingMissile(player.pos + left_offset, left_dir, WIDTH, HEIGHT, groups)
        groups["bullets"].add(m1)
        groups["all_sprites"].add(m1)

        # RIGHT MISSILE (powerup >= 6)
        if player.powerup_hits >= 6:
            right_offset = right * 20
            right_dir = right * 1
            m2 = HomingMissile(player.pos + right_offset, right_dir, WIDTH, HEIGHT, groups)
            groups["bullets"].add(m2)
            groups["all_sprites"].add(m2)

        player.missile_cooldown = HOMING_FIRE_COOLDOWN

    # -------------------------------------------------------
    #   FINAL FIRE COOLDOWN (for bullets only)
    # -------------------------------------------------------
    if player.powerup_hits >= 2:
        base_cd = max(2, 10 - (player.powerup_hits * 2))
    else:
        base_cd = 10

    player.fire_cooldown = base_cd
