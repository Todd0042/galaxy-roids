import pygame
from settings import (
    ASTEROID_HEALTH_LARGE, ASTEROID_HEALTH_MEDIUM, ASTEROID_HEALTH_SMALL,
    POWERUP_SPAWN_CHANCE
)

# ---------------------------------------------------------
#   Circular hitbox helper
# ---------------------------------------------------------
def circle_hit(pos1, r1, pos2, r2):
    return (pos1 - pos2).length_squared() <= (r1 + r2) ** 2


def handle_misc_collisions(player, groups, state, sfx):
    all_sprites = groups["all_sprites"]
    asteroids = groups["asteroids"]
    bullets = groups["bullets"]
    shrapnel_grenades = groups["shrapnel_grenades"]
    gravity_bombs = groups["gravity_bombs"]
    powerups = groups.get("powerups", None)

    debugger = state.get("debugger", None)
    spawn_shrapnel_explosion = state["spawn_shrapnel_explosion"]

    # ---------------------------------------------------------
    #   Bullets → Asteroids
    # ---------------------------------------------------------
    for a in asteroids.copy():
        ar = getattr(a, "hitbox_radius", 20)

        for b in bullets.copy():
            br = getattr(b, "hitbox_radius", 4)

            if circle_hit(a.pos, ar, b.pos, br):
                bullets.remove(b)
                b.kill()

                a.health -= 1
                if debugger:
                    debugger.add_log("Asteroid hit by bullet")

                if a.health <= 0:
                    asteroids.remove(a)
                    a.kill()

                    if debugger:
                        debugger.add_log("Asteroid destroyed")

                    # Powerup spawn
                    import random
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        p = state["powerup_spawner"].spawn(a.pos)
                        all_sprites.add(p)
                        if debugger:
                            debugger.add_log("Powerup spawned")

                break  # Stop checking bullets for this asteroid

    # ---------------------------------------------------------
    #   Player → Powerups
    # ---------------------------------------------------------
    if powerups:
        ppos = player.hit_pos
        pr = player.hitbox_radius

        for p in powerups.copy():
            pr2 = getattr(p, "hitbox_radius", 10)

            if circle_hit(ppos, pr, p.pos, pr2):
                powerups.remove(p)
                p.kill()

                if hasattr(p, "apply"):
                    p.apply(player)

                if debugger:
                    debugger.add_log("Player picked up powerup")

    # ---------------------------------------------------------
    #   Shrapnel grenade explosion triggers
    # ---------------------------------------------------------
    for s in shrapnel_grenades.copy():
        if s.exploded:
            spawn_shrapnel_explosion(s.pos, all_sprites, bullets)
            shrapnel_grenades.remove(s)
            s.kill()

            if debugger:
                debugger.add_log("Shrapnel grenade exploded")

    return
