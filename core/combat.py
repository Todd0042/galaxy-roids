import pygame
import systems.audio as audio   # ⭐ REQUIRED for play_sfx
from entities.projectiles import Bullet, LaserBeam, HomingMissile
from settings import LASER_FIRE_COOLDOWN, HOMING_FIRE_COOLDOWN, RAPID_FIRE_COOLDOWN


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

    # -------------------------------------------------------
    #   SINGLE-SHOT MODE (powerups < 2)
    # -------------------------------------------------------
    if player.powerup_hits < 2:
        if not player.fire_button_held:
            return
        if state.get("single_shot_fired", False):
            return

        audio.play_sfx(sfx, "weapon_pew")
        state["single_shot_fired"] = True

        # Normal single bullet
        direction = player.direction
        b = Bullet(player.pos, 0, WIDTH, HEIGHT)
        b.vel = direction * b.vel.length()
        groups["bullets"].add(b)
        groups["all_sprites"].add(b)
        return

    # Reset single-shot flag when in rapid-fire mode
    state["single_shot_fired"] = False

    # -------------------------------------------------------
    #   RAPID-FIRE MODE (powerups >= 2)
    # -------------------------------------------------------
    if not player.fire_button_held:
        return

    now = pygame.time.get_ticks()
    last = state.get("last_pew_time")

    # First shot is instant
    if last is None:
        can_fire = True
    else:
        can_fire = (now - last) >= RAPID_FIRE_COOLDOWN

    if can_fire:
        audio.play_sfx(sfx, "weapon_pew")
        state["last_pew_time"] = now

        # Fire the bullet
        direction = player.direction
        b = Bullet(player.pos, 0, WIDTH, HEIGHT)
        b.vel = direction * b.vel.length()
        groups["bullets"].add(b)
        groups["all_sprites"].add(b)

    # -------------------------------------------------------
    #   SPREAD SHOT (powerup >= 1)
    # -------------------------------------------------------
    if player.powerup_hits >= 1:
        audio.play_sfx(sfx, "weapon_spread")

        for offset in (-15, 0, 15):
            direction = player.direction.rotate(offset)
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

        # ⭐ AUDIO: laser charge
        audio.play_sfx(sfx, "weapon_laser_charge")

        forward = player.direction
        laser = LaserBeam(player.pos + forward * 20, forward, WIDTH, HEIGHT)
        groups["bullets"].add(laser)
        groups["all_sprites"].add(laser)

        # ⭐ AUDIO: laser fire
        audio.play_sfx(sfx, "weapon_laser")

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
        audio.play_sfx(sfx, "weapon_missile")

        player.missile_cooldown = HOMING_FIRE_COOLDOWN

    # -------------------------------------------------------
    #   FINAL FIRE COOLDOWN (for bullets only)
    # -------------------------------------------------------
    if player.powerup_hits >= 2:
        base_cd = max(2, 10 - (player.powerup_hits * 2))
    else:
        base_cd = 10

    player.fire_cooldown = base_cd
