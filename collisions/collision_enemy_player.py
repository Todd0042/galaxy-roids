import pygame
from entities.projectiles import VenomOrb, HazardPool
from settings import (
    HAZARD_DAMAGE,
    HAZARD_DOT_INTERVAL,
    HAZARD_SLOW_MULT,
    HAZARD_LINGER_MULT,
    HAZARD_LINGER_TIME,
)


def circle_hit(a_center, a_r, b_center, b_r):
    dx = a_center.x - b_center.x
    dy = a_center.y - b_center.y
    return (dx*dx + dy*dy) < (a_r + b_r) * (a_r + b_r)


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

            if not hasattr(enemy, "hitbox_radius"):
                enemy.hitbox_radius = enemy.rect.width * 0.35
            enemy.hitbox_center = pygame.Vector2(enemy.rect.center)

            if circle_hit(player.hitbox_center, player.hitbox_radius,
                          enemy.hitbox_center, enemy.hitbox_radius):
                player.take_damage(enemy.contact_damage)

                if player.health <= 0:
                    return True

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH ASTEROIDS
    # ------------------------------------------------------------
    if asteroids:
        for rock in asteroids:

            if not hasattr(rock, "hitbox_radius"):
                rock.hitbox_radius = rock.rect.width * 0.45
            rock.hitbox_center = pygame.Vector2(rock.rect.center)

            if circle_hit(player.hitbox_center, player.hitbox_radius,
                          rock.hitbox_center, rock.hitbox_radius):
                player.take_damage(rock.contact_damage)

                if player.health <= 0:
                    return True

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH BOSS BODY
    # ------------------------------------------------------------
    if boss_group:
        for boss in boss_group:

            if not hasattr(boss, "hitbox_radius"):
                boss.hitbox_radius = boss.rect.width * 0.45
            boss.hitbox_center = pygame.Vector2(boss.rect.center)

            if circle_hit(player.hitbox_center, player.hitbox_radius,
                          boss.hitbox_center, boss.hitbox_radius):
                player.take_damage(10)

                if player.health <= 0:
                    return True

    # ------------------------------------------------------------
    #   PLAYER COLLISION WITH BOSS BULLETS
    # ------------------------------------------------------------
    if boss_bullets:
        for bullet in boss_bullets:

            if not hasattr(bullet, "hitbox_radius"):
                bullet.hitbox_radius = bullet.rect.width * 0.3
            bullet.hitbox_center = pygame.Vector2(bullet.rect.center)

            if circle_hit(player.hitbox_center, player.hitbox_radius,
                          bullet.hitbox_center, bullet.hitbox_radius):
                player.take_damage(5)
                bullet.kill()

                if player.health <= 0:
                    return True

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

                    if player.health <= 0:
                        return True

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

    # ============================================================
    #   FINAL DEATH CHECK (centralized)
    # ============================================================
    if player.health <= 0:
        return True

    return False
