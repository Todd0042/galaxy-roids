import pygame
from settings import BULLET_DAMAGE, SHRAPNEL_DAMAGE, BOSS_DAMAGE


def handle_boss_collisions(player, groups, state, sfx):
    """
    Handles:
    - player bullets hitting boss
    - shrapnel hitting boss
    - gravity bombs hitting boss
    - boss laser hitting player
    - boss tail strike (Boss3)

    Returns:
        True  – boss died this frame
        False – boss still alive
    """

    boss_group = groups["boss_group"]
    if len(boss_group) == 0:
        return False

    boss = next(iter(boss_group))

    bullets = groups["bullets"]
    shrapnel = groups["shrapnel_grenades"]
    gravity = groups["gravity_bombs"]
    all_sprites = groups["all_sprites"]

    # -----------------------------
    # Player bullets → boss
    # -----------------------------
    for b in bullets.copy():
        if boss.rect.colliderect(b.rect):
            b.kill()
            bullets.remove(b)

            boss.health -= BULLET_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True

    # -----------------------------
    # Shrapnel → boss
    # -----------------------------
    for s in shrapnel.copy():
        if s.exploded:
            s.kill()
            shrapnel.remove(s)

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True

    # -----------------------------
    # Gravity bomb → boss
    # -----------------------------
    for g in gravity.copy():
        if g.exploded:
            g.kill()
            gravity.remove(g)

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True

    # -----------------------------
    # Boss laser → player
    # -----------------------------
    if boss.laser_active_timer > 0:
        laser_rect = pygame.Rect(
            boss.rect.centerx - 40,
            boss.rect.bottom,
            80,
            state["HEIGHT"]
        )

        if laser_rect.colliderect(player.rect):
            player.health -= BOSS_DAMAGE
            player.lose_powerup_level()

    # -----------------------------
    # Boss tail strike (Boss3)
    # -----------------------------
    if hasattr(boss, "tail_active_timer") and boss.tail_active_timer > 0:
        strike_rect = pygame.Rect(
            boss.tail_tip.x - 8,
            boss.tail_tip.y,
            16,
            state["HEIGHT"] - boss.tail_tip.y
        )

        if strike_rect.colliderect(player.rect):
            # Use boss.tail_damage if available, fallback to BOSS_DAMAGE
            dmg = getattr(boss, "tail_damage", BOSS_DAMAGE)
            player.health -= dmg
            player.lose_powerup_level()

    return False
