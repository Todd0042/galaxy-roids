import pygame
from settings import (
    ASTEROID_HEALTH_LARGE, ASTEROID_HEALTH_MEDIUM, ASTEROID_HEALTH_SMALL,
    POWERUP_SPAWN_CHANCE
)

def handle_misc_collisions(player, groups, state, sfx):
    all_sprites = groups["all_sprites"]
    asteroids = groups["asteroids"]
    bullets = groups["bullets"]
    shrapnel_grenades = groups["shrapnel_grenades"]
    gravity_bombs = groups["gravity_bombs"]
    powerups = groups.get("powerups", None)

    debugger = state.get("debugger", None)
    spawn_shrapnel_explosion = state["spawn_shrapnel_explosion"]


    # --- Bullets hitting asteroids ---
    for a in asteroids.copy():
        for b in bullets.copy():
            if a.rect.colliderect(b.rect):
                bullets.remove(b)
                b.kill()

                # Reduce asteroid health
                a.health -= 1
                debugger.add_log("Asteroid hit by bullet")

                # Destroy asteroid if health reaches zero
                if a.health <= 0:
                    asteroids.remove(a)
                    a.kill()
                    debugger.add_log("Asteroid destroyed")

                    # Spawn powerup randomly
                    import random
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        p = state["powerup_spawner"].spawn(a.rect.center)
                        all_sprites.add(p)
                        debugger.add_log("Powerup spawned")

                break  # Stop checking bullets for this asteroid

    # --- Player picking up powerups ---
    # FIXED: powerups is already a Group, so use powerups.copy()
    for p in powerups.copy():
        if player.rect.colliderect(p.rect):
            powerups.remove(p)
            p.kill()

            # Apply powerup effect
            if hasattr(p, "apply"):
                p.apply(player)

            debugger.add_log("Player picked up powerup")

    # --- Shrapnel grenade explosion triggers ---
    for s in shrapnel_grenades.copy():
        if s.exploded:
            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
            shrapnel_grenades.remove(s)
            s.kill()
            debugger.add_log("Shrapnel grenade exploded")

    return
