import pygame
from entities.projectiles import Bullet, LaserBeam, HomingMissile
from settings import LASER_FIRE_COOLDOWN, HOMING_FIRE_COOLDOWN


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

        # ⭐ AUDIO: single-shot pew
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("weapon_pew"):
            ch.play(sfx["weapon_pew"])

        state["single_shot_fired"] = True
    else:
        state["single_shot_fired"] = False

    # --------------------------
    # AUTO-FIRE PEW (NO BUTTON)
    # --------------------------

    now = pygame.time.get_ticks()
    MIN_SPACING = 160   # minimum ms between starting a new pew

    if now - state["last_pew_time"] > MIN_SPACING:
        # ⭐ AUDIO: rapid-fire pew
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("weapon_pew"):
            ch.play(sfx["weapon_pew"])

        state["last_pew_time"] = now

    # -------------------------------------------------------
    #   SPREAD SHOT (powerup >= 1)
    # -------------------------------------------------------
    if player.powerup_hits >= 1:

        # ⭐ AUDIO: spread-shot accent (optional)
        if sfx.get("weapon_spread"):
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(sfx["weapon_spread"])

        for offset in (-15, 0, 15):
            direction = player.direction.rotate(offset)
            b = Bullet(player.pos, 0, WIDTH, HEIGHT)
            b.vel = direction * b.vel.length()
            groups["bullets"].add(b)
            groups["all_sprites"].add(b)

    else:
        direction = player.direction
        b = Bullet(player.pos, 0, WIDTH, HEIGHT)
        b.vel = direction * b.vel.length()
        groups["bullets"].add(b)
        groups["all_sprites"].add(b)

    # -------------------------------------------------------
    #   LASER BEAM (powerup >= 4)
    # -------------------------------------------------------
    if not hasattr(player, "laser_cooldown"):
        player.laser_cooldown = 0

    if player.laser_cooldown > 0:
        player.laser_cooldown -= 1

    if player.powerup_hits >= 4 and player.laser_cooldown <= 0:

        # ⭐ AUDIO: optional laser charge
        if sfx.get("weapon_laser_charge"):
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(sfx["weapon_laser_charge"])

        forward = player.direction
        laser = LaserBeam(player.pos + forward * 20, forward, WIDTH, HEIGHT)
        groups["bullets"].add(laser)
        groups["all_sprites"].add(laser)

        # ⭐ AUDIO: laser fire
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("weapon_laser"):
            ch.play(sfx["weapon_laser"])

        player.laser_cooldown = LASER_FIRE_COOLDOWN

    # -------------------------------------------------------
    #   HOMING MISSILES (powerup >= 5)
    # -------------------------------------------------------
    if not hasattr(player, "missile_cooldown"):
        player.missile_cooldown = 0

    if player.missile_cooldown > 0:
        player.missile_cooldown -= 1

    if player.powerup_hits >= 5 and player.missile_cooldown <= 0:

        forward = player.direction
        right = forward.rotate(90)

        # LEFT MISSILE
        left_offset = right * -20
        left_dir = forward.rotate(-45)
        m1 = HomingMissile(player.pos + left_offset, left_dir, WIDTH, HEIGHT, groups)
        groups["bullets"].add(m1)
        groups["all_sprites"].add(m1)

        # RIGHT MISSILE (powerup >= 6)
        if player.powerup_hits >= 6:
            right_offset = right * 20
            right_dir = forward.rotate(45)
            m2 = HomingMissile(player.pos + right_offset, right_dir, WIDTH, HEIGHT, groups)
            groups["bullets"].add(m2)
            groups["all_sprites"].add(m2)

        # ⭐ AUDIO: missile launch
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("weapon_missile"):
            ch.play(sfx["weapon_missile"])

        player.missile_cooldown = HOMING_FIRE_COOLDOWN

    # -------------------------------------------------------
    #   FINAL FIRE COOLDOWN (for bullets only)
    # -------------------------------------------------------
    if player.powerup_hits >= 2:
        base_cd = max(2, 10 - (player.powerup_hits * 2))
    else:
        base_cd = 10

    player.fire_cooldown = base_cd
