import pygame
from ui.popups import show_victory_popup
from systems.level_manager import start_level
from settings import STARTING_POWERUPS


def handle_boss_defeat(player, groups, state, sfx, screen, font):
    """
    Handles everything that happens AFTER the boss dies:
    - Shows victory popup
    - Applies difficulty choice
    - Increments level
    - Resets timers + flags
    - Calls start_level() to begin the next level

    Returns:
        "continue" – continue gameplay
        "exit"     – user chose to quit
    """

    # ==========================
    # ⭐ AUDIO: boss defeated stinger
    # ==========================
    ch = pygame.mixer.find_channel()
    if ch and sfx.get("boss_defeated"):
        ch.play(sfx["boss_defeated"])

    # Optional: tiny shake for dramatic effect
    state["screenshake"] = max(state.get("screenshake", 0), 6)

    # ==========================
    # 1. Show victory popup
    # ==========================

    # ⭐ AUDIO: popup open
    ch = pygame.mixer.find_channel()
    if ch and sfx.get("ui_popup_open"):
        ch.play(sfx["ui_popup_open"])

    result = show_victory_popup(state["score"], state["level"])

    if result == "exit":
        # ⭐ AUDIO: exit confirm
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("ui_confirm"):
            ch.play(sfx["ui_confirm"])
        return "exit"

    # ==========================
    # 2. Difficulty scaling
    # ==========================
    if result == "harder":
        state["current_enemy_speed"] += 0.4
        state["current_boss_speed"] += 0.4

        # ⭐ AUDIO: difficulty chosen
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("ui_select_harder"):
            ch.play(sfx["ui_select_harder"])
    else:
        # ⭐ AUDIO: normal difficulty confirm
        ch = pygame.mixer.find_channel()
        if ch and sfx.get("ui_confirm"):
            ch.play(sfx["ui_confirm"])

    # ==========================
    # 3. Level increment
    # ==========================
    state["level"] += 1

    # ⭐ AUDIO: level complete jingle
    ch = pygame.mixer.find_channel()
    if ch and sfx.get("level_complete"):
        ch.play(sfx["level_complete"])

    # ==========================
    # 4. Reset boss + spawn timers
    # ==========================
    state["boss_spawned"] = False
    state["last_periodic_spawn"] = 0
    state["level_start_time"] = pygame.time.get_ticks()

    # ⭐ MUSIC: reset boss fade flag for next level
    state["boss_music_started"] = False

    # ==========================
    # 5. Clear boss bullets
    # ==========================
    groups["boss_bullets"].empty()
    groups["boss_group"].empty()

    # ==========================
    # 5.5 Reduce player powerups between levels
    # ==========================

    # ⭐ AUDIO: power reset sound
    ch = pygame.mixer.find_channel()
    if ch and sfx.get("player_power_reset"):
        ch.play(sfx["player_power_reset"])

    # --- Powerup reduction rules based on level ---
    if current_level <= 4:
        # Reduce to exactly 1
        player.powerup_hits = min(player.powerup_hits, 1)

    elif 5 <= current_level <= 8:
        # Lose exactly 2 levels, but never below 1
        player.powerup_hits = max(player.powerup_hits - 2, 1)

    else:
        # Level 9+ lose nothing
        pass

    # --- Recompute weapon mode + flags ---
    player.weapon_mode = "NORMAL"
    player.has_laser = False
    player.homing_count = 0

    if player.powerup_hits >= 1:
        player.weapon_mode = "SPREAD"

    player.update_appearance()

    # ==========================
    # DEV OVERRIDE: starting powerup level
    # ==========================
    if settings.STARTING_POWERUPS > 0:
        player.powerup_hits = settings.STARTING_POWERUPS

        # Recompute weapon state
        player.weapon_mode = "NORMAL"
        player.has_laser = False
        player.homing_count = 0

        if player.powerup_hits >= 1:
            player.weapon_mode = "SPREAD"
        if player.powerup_hits >= 4:
            player.has_laser = True

        player.update_appearance()


    # ==========================
    # 6. Start next level
    # ==========================

    # ⭐ AUDIO: new level start SFX (not music)
    ch = pygame.mixer.find_channel()
    if ch and sfx.get("level_start"):
        ch.play(sfx["level_start"])

    # ⭐ MUSIC: actual level music is started inside start_level()
    start_level(
        state["level"],
        state["WIDTH"],
        state["HEIGHT"],
        groups["all_sprites"],
        groups["enemies"],
        groups["asteroids"],
        state["current_enemy_speed"],
        state["enemies_per_side"],
        debugger=None,
        state=state  # ⭐ pass state so level_manager can access sfx + flags
    )

    return "continue"
