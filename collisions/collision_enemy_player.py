import pygame
from entities.projectiles import VenomOrb, HazardPool
from settings import (
    HAZARD_DAMAGE,
    HAZARD_DOT_INTERVAL,
    HAZARD_SLOW_MULT,
    HAZARD_LINGER_MULT,
    HAZARD_LINGER_TIME,
)


def handle_enemy_player_collisions(player, groups, state, sfx):
    enemies = groups.get("enemies")
    asteroids = groups.get("asteroids")
    boss_bullets = groups.get("boss_bullets")
    hazards = groups.get("hazards")
    boss_group = groups.get("boss_group")

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH REGULAR ENEMIES
    # ------------------------------------------------------------
    if enemies:
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                player.take_damage(enemy.contact_damage)

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH ASTEROIDS
    # ------------------------------------------------------------
    if asteroids:
        for rock in asteroids:
            if player.rect.colliderect(rock.rect):
                player.take_damage(rock.contact_damage)

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH BOSS BODY
    # ------------------------------------------------------------
    if boss_group:
        for boss in boss_group:
            if player.rect.colliderect(boss.rect):
                player.take_damage(10)

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH BOSS BULLETS
    # ------------------------------------------------------------
    if boss_bullets:
        for bullet in boss_bullets:
            if player.rect.colliderect(bullet.rect):
                player.take_damage(5)
                bullet.kill()

    # ============================================================
    #   HAZARD POOL LOGIC (Boss3)
    # ============================================================
    if hazards:
        player_in_pool = False

        for pool in hazards:
            if player.rect.colliderect(pool.rect):

                player_in_pool = True

                # Apply strong slow
                player.speed_multiplier = HAZARD_SLOW_MULT

                # DOT timer
                if not hasattr(player, "hazard_dot_timer"):
                    player.hazard_dot_timer = 0

                player.hazard_dot_timer -= 1
                if player.hazard_dot_timer <= 0:
                    player.take_damage(HAZARD_DAMAGE)
                    player.hazard_dot_timer = HAZARD_DOT_INTERVAL

                # Reset lingering slow timer
                player.hazard_slow_timer = HAZARD_LINGER_TIME

        # --------------------------------------------------------
        #   OUTSIDE POOL — lingering slow logic
        # --------------------------------------------------------
        if not player_in_pool:

            if hasattr(player, "hazard_slow_timer") and player.hazard_slow_timer > 0:
                player.hazard_slow_timer -= 1
                player.speed_multiplier = HAZARD_LINGER_MULT

            else:
                player.speed_multiplier = 1.0
                player.hazard_dot_timer = 0
