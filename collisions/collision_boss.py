import pygame
from settings import BULLET_DAMAGE, SHRAPNEL_DAMAGE, BOSS_DAMAGE

def handle_boss_collisions(
    player, bullets, shrapnel_grenades, gravity_bombs,
    boss_group, all_sprites, debugger,
    spawn_shrapnel_explosion, spawn_gravity_explosion
):
    """
    Handles:
    - player bullets hitting boss
    - shrapnel hitting boss
    - gravity bombs hitting boss
    - boss laser hitting player

    Does NOT handle:
    - boss death
    - level transitions
    - victory popup
    """

    if len(boss_group) == 0:
        return None  # No boss active

    boss = boss_group.sprites()[0]

    # -----------------------------
    #   Player bullets hit boss
    # -----------------------------
    for b in bullets.copy():
        if boss.rect.colliderect(b.rect):
            bullets.remove(b)
            b.kill()

            boss.health -= BULLET_DAMAGE
            boss.hit_flash = 5
            debugger.add_log("Boss hit by bullet")

            return boss  # Return boss so caller can check for death

    # -----------------------------
    #   Shrapnel hits boss
    # -----------------------------
    for s in shrapnel_grenades.copy():
        if s.exploded:
            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
            shrapnel_grenades.remove(s)
            s.kill()

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5
            debugger.add_log("Boss hit by shrapnel")

            return boss

    # -----------------------------
    #   Gravity bomb hits boss
    # -----------------------------
    for g in gravity_bombs.copy():
        if g.exploded:
            spawn_gravity_explosion(g.rect.center, all_sprites, bullets)
            gravity_bombs.remove(g)
            g.kill()

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5
            debugger.add_log("Boss hit by gravity explosion")

            return boss

    # -----------------------------
    #   Boss laser hits player
    # -----------------------------
    if boss.laser_active_timer > 0:
        laser_rect = pygame.Rect(
            boss.rect.centerx - 40,
            boss.rect.bottom,
            80,
            player.screen_h
        )
        if laser_rect.colliderect(player.rect):
            player.health -= BOSS_DAMAGE
            debugger.add_log("Player hit by boss laser")

            return boss

    return boss
