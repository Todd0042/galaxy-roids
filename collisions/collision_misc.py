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

    # -------------------------------------------------
    # Bullets hitting asteroids
    # -------------------------------------------------
    for a in asteroids:
        if debugger:
            debugger.add_log(f"[CHECK] Asteroid {id(a)} starting health {a.health}")

        for b in bullets:
            if a.rect.colliderect(b.rect):
                bullets.remove(b)
                b.kill()

                # Reduce asteroid health
                a.health -= 1
                if debugger:
                    debugger.add_log(f"[HIT] Asteroid {id(a)} health now {a.health}")

                # Let Asteroid.update() handle splitting + kill
                if a.health <= 0 and debugger:
                    debugger.add_log(f"[PENDING SPLIT] Asteroid {id(a)} reached 0 HP")

                    # Spawn powerup randomly
                    import random
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        p = state["powerup_spawner"].spawn(a.rect.center)
                        all_sprites.add(p)
                        debugger.add_log("Powerup spawned")

                break  # stop checking more bullets for this asteroid

    # -------------------------------------------------
    # Shrapnel grenades impacting asteroids
    # (grenade itself should not ghost through)
    # -------------------------------------------------
    for s in shrapnel_grenades.copy():
        for a in asteroids:
            if s.rect.colliderect(a.rect):
                # Mark grenade as exploded on impact
                s.exploded = True
                if debugger:
                    debugger.add_log("Shrapnel grenade impacted asteroid (will explode)")
                break

    # -------------------------------------------------
    # Player picking up powerups
    # -------------------------------------------------
    if powerups is not None:
        for p in powerups.copy():
            if player.rect.colliderect(p.rect):
                powerups.remove(p)
                p.kill()

                # Apply powerup effect
                if hasattr(p, "apply"):
                    p.apply(player)

                if debugger:
                    debugger.add_log("Player picked up powerup")

    # -------------------------------------------------
    # Shrapnel grenade explosion triggers
    # -------------------------------------------------
    for s in shrapnel_grenades.copy():
        if getattr(s, "exploded", False):
            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
            shrapnel_grenades.remove(s)
            s.kill()
            if debugger:
                debugger.add_log("Shrapnel grenade exploded")

    return
