import pygame
from ui.popups import show_victory_popup
from systems.level_manager import start_level


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
    # 1. Show victory popup
    # ==========================
    result = show_victory_popup(state["score"], state["level"])

    if result == "exit":
        return "exit"

    # ==========================
    # 2. Difficulty scaling
    # ==========================
    if result == "harder":
        state["current_enemy_speed"] += 0.4
        state["current_boss_speed"] += 0.4

    # ==========================
    # 3. Level increment
    # ==========================
    state["level"] += 1

    # ==========================
    # 4. Reset boss + spawn timers
    # ==========================
    state["boss_spawned"] = False
    state["last_periodic_spawn"] = 0
    state["level_start_time"] = pygame.time.get_ticks()

    # ==========================
    # 5. Clear boss bullets
    # ==========================
    groups["boss_bullets"].empty()
    groups["boss_group"].empty()

    # ==========================
    # 5.5 Reduce player powerups between levels
    # ==========================
    player.powerup_hits = min(player.powerup_hits, 1)

    player.weapon_mode = "NORMAL"
    player.has_laser = False
    player.homing_count = 0

    if player.powerup_hits == 1:
        player.weapon_mode = "SPREAD"

    player.update_appearance()

    # ==========================
    # 6. Start next level
    # ==========================
    start_level(
        state["level"],
        state["WIDTH"],
        state["HEIGHT"],
        groups["all_sprites"],
        groups["enemies"],
        groups["asteroids"],
        state["current_enemy_speed"],
        state["enemies_per_side"],
        debugger=None
    )

    return "continue"
