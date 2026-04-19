import pygame

from collisions.collision_player_enemy import handle_player_enemy_collisions
from collisions.collision_enemy_player import handle_enemy_player_collisions
from collisions.collision_misc import handle_misc_collisions
from collisions.collision_boss import handle_boss_collisions

from core.player_state import handle_player_death


def process_collisions(player, groups, state, sfx):
    """
    Orchestrates ALL collision handling in the correct order.

    Returns:
        "continue"      – normal gameplay continues
        "player_dead"   – player died and has no lives left
        "boss_dead"     – boss was killed this frame
    """

    # ==========================
    # 1. Player bullets → enemies
    # ==========================
    handle_player_enemy_collisions(player, groups, state, sfx)

    # ==========================
    # 2. Enemies / hazards → player
    # ==========================
    player_died = handle_enemy_player_collisions(player, groups, state, sfx)

    if player_died:
        # Attempt respawn
        if not handle_player_death(player, state):
            return "player_dead"

    # ==========================
    # 3. Misc collisions
    #    (asteroids, powerups, shrapnel, gravity bombs)
    # ==========================
    handle_misc_collisions(player, groups, state, sfx)

    # ==========================
    # 4. Boss collisions
    #    (player bullets, shrapnel, gravity bombs, boss laser)
    # ==========================
    boss_killed = handle_boss_collisions(player, groups, state, sfx)

    if boss_killed:
        return "boss_dead"

    return "continue"
