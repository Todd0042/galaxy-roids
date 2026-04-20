import pygame
from settings import (
    HAZARD_DAMAGE, BLOB_DAMAGE, BOMBER_DAMAGE, BOSS_DAMAGE,
    BLOB_STUN_TIME
)

# ---------------------------------------------------------
#   Circular hitbox helper
# ---------------------------------------------------------
def circle_hit(pos1, r1, pos2, r2):
    return (pos1 - pos2).length_squared() <= (r1 + r2) ** 2


def handle_enemy_player_collisions(player, groups, state, sfx):
    """
    Handles:
    - enemies colliding with player
    - blob traps
    - bomber explosions
    - boss contact damage
    - enemy bullets hitting player
    - asteroid collisions
    """

    enemies = groups["enemies"]
    enemy_bullets = groups["boss_bullets"]
    asteroids = groups["asteroids"]
    debugger = state.get("debugger", None)
    current_time = pygame.time.get_ticks()

    ppos = player.hit_pos
    pr = player.hitbox_radius

    # ---------------------------------------------------------
    #   Enemy bullets → Player
    # ---------------------------------------------------------
    for b in enemy_bullets.copy():
        br = getattr(b, "hitbox_radius", 4)

        if circle_hit(ppos, pr, b.pos, br):
            enemy_bullets.remove(b)
            b.kill()

            if player.invulnerable_timer == 0:
                player.health -= HAZARD_DAMAGE
                player.lose_powerup_level()
                player.invulnerable_timer = 60

                if debugger:
                    debugger.add_log("Player hit by enemy bullet")

    # ---------------------------------------------------------
    #   Enemies → Player
    # ---------------------------------------------------------
    for e in enemies.copy():
        er = getattr(e, "hitbox_radius", 12)

        if not circle_hit(ppos, pr, e.pos, er):
            continue

        etype = getattr(e, "enemy_type", "")

        # Blob trap
        if etype == "BLOB":
            if player.invulnerable_timer == 0:
                player.apply_trap(BLOB_STUN_TIME * 16, BLOB_DAMAGE)
                if debugger:
                    debugger.add_log("Player trapped by blob")
            continue

        # Bomber explosion
        if etype == "BOMBER":
            if hasattr(e, "explode"):
                e.explode()
            if player.invulnerable_timer == 0:
                player.health -= BOMBER_DAMAGE
                player.lose_powerup_level()
                player.invulnerable_timer = 60

                if debugger:
                    debugger.add_log("Player hit by bomber explosion")
            continue

        # Boss contact
        if etype == "BOSS":
            if player.invulnerable_timer == 0:
                player.health -= BOSS_DAMAGE
                player.lose_powerup_level()
                player.invulnerable_timer = 60

                if debugger:
                    debugger.add_log("Player hit by boss")
            continue

        # Normal enemy collision
        if player.invulnerable_timer == 0:
            player.health -= HAZARD_DAMAGE
            player.lose_powerup_level()
            player.invulnerable_timer = 60

            if debugger:
                debugger.add_log("Player hit by enemy")

    # ---------------------------------------------------------
    #   Asteroids → Player
    # ---------------------------------------------------------
    for a in asteroids.copy():
        ar = getattr(a, "hitbox_radius", 20)

        if not circle_hit(ppos, pr, a.pos, ar):
            continue

        if current_time - player.last_asteroid_hit > player.asteroid_hit_cooldown:
            player.last_asteroid_hit = current_time

            if player.invulnerable_timer == 0:
                player.health -= HAZARD_DAMAGE
                player.lose_powerup_level()
                player.invulnerable_timer = 60

                if debugger:
                    debugger.add_log("Player hit by asteroid")

    return player.health <= 0
