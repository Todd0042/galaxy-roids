import pygame

def handle_player_enemy_collisions(
    player, groups, state, sfx
):
    """
    Handles:
    - bullets hitting enemies
    - shrapnel grenades hitting enemies
    - bomber fragments hitting enemies
    - remove_on_collision logic
    """

    enemies = groups["enemies"]
    bullets = groups["bullets"]
    shrapnel_grenades = groups["shrapnel_grenades"]
    all_sprites = groups["all_sprites"]
    debugger = state.get("debugger", None)
    score = state["score"]

    spawn_shrapnel_explosion = state["spawn_shrapnel_explosion"]

    for e in enemies.copy():
        enemy_removed = False

        # -------------------------------------------------------
        #   NORMAL BULLETS
        # -------------------------------------------------------
        for b in bullets.copy():
            if e.rect.colliderect(b.rect):
                bullets.remove(b)
                b.kill()

                # ⭐ FIX: Blobs should NOT trap the player when shot
                if hasattr(e, "collision_effect") and getattr(e, "type", "") != "BLOB":
                    e.collision_effect(player)

                # ⭐ NEW: spawn splatter before removing enemy
                if getattr(e, "remove_on_collision", True):
                    if hasattr(e, "spawn_splatter"):
                        e.spawn_splatter(groups)

                    # ⭐ AUDIO: enemy death sound
                    ch = pygame.mixer.find_channel()
                    if ch:
                        etype = getattr(e, "type", "")
                        if etype == "SMALL_BUG":
                            ch.play(sfx.get("bug_small_death"))
                        elif etype == "BIG_BUG":
                            ch.play(sfx.get("bug_big_death"))
                        else:
                            if sfx.get("explosion_small"):
                                ch.play(sfx["explosion_small"])

                    enemies.remove(e)
                    e.kill()

                score += 10
                if debugger:
                    debugger.add_log("Enemy destroyed by bullet")
                enemy_removed = True
                break
        if enemy_removed:
            continue

        # -------------------------------------------------------
        #   SHRAPNEL GRENADES
        # -------------------------------------------------------
        for s in shrapnel_grenades.copy():
            if s.exploded:
                spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                shrapnel_grenades.remove(s)
                s.kill()
                if debugger:
                    debugger.add_log("Shrapnel grenade exploded")
                continue

            if e.rect.colliderect(s.rect):
                spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                shrapnel_grenades.remove(s)
                s.kill()

                # ⭐ FIX: Blobs should NOT trap the player when shot
                if hasattr(e, "collision_effect") and getattr(e, "type", "") != "BLOB":
                    e.collision_effect(player)

                # ⭐ NEW: spawn splatter before removing enemy
                if getattr(e, "remove_on_collision", True):
                    if hasattr(e, "spawn_splatter"):
                        e.spawn_splatter(groups)

                    # ⭐ AUDIO: enemy death sound
                    ch = pygame.mixer.find_channel()
                    if ch:
                        etype = getattr(e, "type", "")
                        if etype == "SMALL_BUG":
                            ch.play(sfx.get("bug_small_death"))
                        elif etype == "BIG_BUG":
                            ch.play(sfx.get("bug_big_death"))
                        else:
                            if sfx.get("explosion_small"):
                                ch.play(sfx["explosion_small"])

                    enemies.remove(e)
                    e.kill()

                score += 10
                if debugger:
                    debugger.add_log("Enemy destroyed by shrapnel")
                enemy_removed = True
                break
        if enemy_removed:
            continue

        # -------------------------------------------------------
        #   BOMBER FRAGMENTS
        # -------------------------------------------------------
        for b in bullets.copy():
            if getattr(b, "is_bomber_fragment", False):
                if e.rect.colliderect(b.rect):
                    bullets.remove(b)
                    b.kill()

                    # ⭐ FIX: Blobs should NOT trap the player when shot
                    if hasattr(e, "collision_effect") and getattr(e, "type", "") != "BLOB":
                        e.collision_effect(player)

                    # ⭐ NEW: spawn splatter before removing enemy
                    if getattr(e, "remove_on_collision", True):
                        if hasattr(e, "spawn_splatter"):
                            e.spawn_splatter(groups)

                        # ⭐ AUDIO: enemy death sound
                        ch = pygame.mixer.find_channel()
                        if ch:
                            etype = getattr(e, "type", "")
                            if etype == "SMALL_BUG":
                                ch.play(sfx.get("bug_small_death"))
                            elif etype == "BIG_BUG":
                                ch.play(sfx.get("bug_big_death"))
                            else:
                                if sfx.get("explosion_small"):
                                    ch.play(sfx["explosion_small"])

                        enemies.remove(e)
                        e.kill()

                    score += 10
                    if debugger:
                        debugger.add_log("Enemy destroyed by fragment")
                    enemy_removed = True
                    break
        if enemy_removed:
            continue

    state["score"] = score
    return score
