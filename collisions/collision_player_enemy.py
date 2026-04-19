import pygame

def handle_player_hits_enemies(
    player, enemies, bullets, shrapnel_grenades,
    all_sprites, debugger, score, spawn_shrapnel_explosion
):
    """
    Handles:
    - bullets hitting enemies
    - shrapnel grenades hitting enemies
    - bomber fragments hitting enemies
    - remove_on_collision logic
    """

    for e in enemies.copy():
        enemy_removed = False

        # Normal bullets
        for b in bullets.copy():
            if e.rect.colliderect(b.rect):
                bullets.remove(b)
                b.kill()

                if hasattr(e, "collision_effect"):
                    e.collision_effect(player)

                if getattr(e, "remove_on_collision", True):
                    enemies.remove(e)
                    e.kill()

                score += 10
                debugger.add_log("Enemy destroyed by bullet")
                enemy_removed = True
                break
        if enemy_removed:
            continue

        # Shrapnel grenades
        for s in shrapnel_grenades.copy():
            if s.exploded:
                spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                shrapnel_grenades.remove(s)
                s.kill()
                debugger.add_log("Shrapnel grenade exploded")
                continue

            if e.rect.colliderect(s.rect):
                spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                shrapnel_grenades.remove(s)
                s.kill()

                if hasattr(e, "collision_effect"):
                    e.collision_effect(player)

                if getattr(e, "remove_on_collision", True):
                    enemies.remove(e)
                    e.kill()

                score += 10
                debugger.add_log("Enemy destroyed by shrapnel")
                enemy_removed = True
                break
        if enemy_removed:
            continue

        # Bomber radial fragments
        for b in bullets.copy():
            if getattr(b, "is_bomber_fragment", False):
                if e.rect.colliderect(b.rect):
                    bullets.remove(b)
                    b.kill()

                    if hasattr(e, "collision_effect"):
                        e.collision_effect(player)

                    if getattr(e, "remove_on_collision", True):
                        enemies.remove(e)
                        e.kill()

                    score += 10
                    debugger.add_log("Enemy destroyed by fragment")
                    enemy_removed = True
                    break
        if enemy_removed:
            continue

    return score
