import pygame
from settings import (
    HAZARD_DAMAGE, BLOB_DAMAGE, BOMBER_DAMAGE, BOSS_DAMAGE,
    BLOB_STUN_TIME
)

def handle_enemies_hit_player(
    player, enemies, enemy_bullets, asteroids,
    debugger, current_time
):
    """
    Handles:
    - enemies colliding with player
    - blob traps
    - bomber explosions
    - boss contact damage
    - enemy bullets hitting player
    - asteroid collisions
    """

    # --- Enemy bullets hitting player ---
    for b in enemy_bullets.copy():
        if player.rect.colliderect(b.rect):
            enemy_bullets.remove(b)
            b.kill()

            if player.invulnerable_timer == 0:
                player.health -= HAZARD_DAMAGE
                player.invulnerable_timer = 60  # 1 second of i-frames
                debugger.add_log("Player hit by enemy bullet")

    # --- Enemies colliding with player ---
    for e in enemies.copy():
        if player.rect.colliderect(e.rect):

            # Blob trap
            if getattr(e, "enemy_type", "") == "BLOB":
                if player.invulnerable_timer == 0:
                    player.apply_trap(BLOB_STUN_TIME * 16, BLOB_DAMAGE)
                    debugger.add_log("Player trapped by blob")
                continue

            # Bomber explosion
            if getattr(e, "enemy_type", "") == "BOMBER":
                if hasattr(e, "explode"):
                    e.explode()
                if player.invulnerable_timer == 0:
                    player.health -= BOMBER_DAMAGE
                    player.invulnerable_timer = 60
                    debugger.add_log("Player hit by bomber explosion")
                continue

            # Boss contact damage
            if getattr(e, "enemy_type", "") == "BOSS":
                if player.invulnerable_timer == 0:
                    player.health -= BOSS_DAMAGE
                    player.invulnerable_timer = 60
                    debugger.add_log("Player hit by boss")
                continue

            # Normal enemy collision
            if player.invulnerable_timer == 0:
                player.health -= HAZARD_DAMAGE
                player.invulnerable_timer = 60
                debugger.add_log("Player hit by enemy")

    # --- Asteroids hitting player ---
    for a in asteroids.copy():
        if player.rect.colliderect(a.rect):

            # Prevent repeated asteroid hits
            if current_time - player.last_asteroid_hit > player.asteroid_hit_cooldown:
                player.last_asteroid_hit = current_time

                if player.invulnerable_timer == 0:
                    player.health -= HAZARD_DAMAGE
                    player.invulnerable_timer = 60
                    debugger.add_log("Player hit by asteroid")

    return player.health
