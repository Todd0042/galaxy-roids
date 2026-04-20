import pygame
from settings import BULLET_DAMAGE, SHRAPNEL_DAMAGE, BOSS_DAMAGE

# ---------------------------------------------------------
#   Circular hitbox helper
# ---------------------------------------------------------
def circle_hit(pos1, r1, pos2, r2):
    return (pos1 - pos2).length_squared() <= (r1 + r2) ** 2


def handle_boss_collisions(player, groups, state, sfx):
    """
    Handles:
    - player bullets → boss
    - shrapnel → boss
    - gravity bombs → boss
    - boss laser → player

    Returns:
        True  – boss died this frame
        False – boss still alive
    """

    boss_group = groups["boss_group"]
    if len(boss_group) == 0:
        return False

    boss = next(iter(boss_group))

    # Boss hitbox radius (fallback if not defined)
    br = getattr(boss, "hitbox_radius", 40)

    bullets = groups["bullets"]
    shrapnel = groups["shrapnel_grenades"]
    gravity = groups["gravity_bombs"]

    # ---------------------------------------------------------
    #   Player bullets → Boss
    # ---------------------------------------------------------
    for b in bullets.copy():
        br2 = getattr(b, "hitbox_radius", 4)

        if circle_hit(boss.pos, br, b.pos, br2):
            bullets.remove(b)
            b.kill()

            boss.health -= BULLET_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True

    # ---------------------------------------------------------
    #   Shrapnel → Boss
    # ---------------------------------------------------------
    for s in shrapnel.copy():
        sr = getattr(s, "hitbox_radius", 6)

        if s.exploded:
            shrapnel.remove(s)
            s.kill()

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True
            continue

        if circle_hit(boss.pos, br, s.pos, sr):
            shrapnel.remove(s)
            s.kill()

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True

    # ---------------------------------------------------------
    #   Gravity Bomb → Boss
    # ---------------------------------------------------------
    for g in gravity.copy():
        gr = getattr(g, "hitbox_radius", 14)

        if g.exploded:
            gravity.remove(g)
            g.kill()

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True
            continue

        if circle_hit(boss.pos, br, g.pos, gr):
            gravity.remove(g)
            g.kill()

            boss.health -= SHRAPNEL_DAMAGE
            boss.hit_flash = 5

            if boss.health <= 0:
                boss.kill()
                boss_group.remove(boss)
                return True

    # ---------------------------------------------------------
    #   Boss Laser → Player
    # ---------------------------------------------------------
    if boss.laser_active_timer > 0:
        # Laser is a vertical beam under the boss
        laser_x = boss.pos.x
        laser_top = boss.pos.y
        laser_bottom = state["HEIGHT"]

        # Player hitbox
        ppos = player.hit_pos
        pr = player.hitbox_radius

        # Horizontal distance from beam center
        dx = abs(ppos.x - laser_x)

        # Beam half-width (80px wide → 40px half)
        beam_half_width = 40

        # Vertical check: player must be below boss
        if ppos.y > laser_top:
            # Horizontal check: within beam width + player radius
            if dx <= beam_half_width + pr:
                if player.invulnerable_timer == 0:
                    player.health -= BOSS_DAMAGE
                    player.lose_powerup_level()
                    player.invulnerable_timer = 60

    return False
