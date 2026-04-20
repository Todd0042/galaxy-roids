import pygame
from settings import (
    PLAYER_MAX_HEALTH,
    PLAYER_INVULN_TIME,
    PLAYER_STUN_TIME,
)


def handle_player_death(player, state):
    """
    Handles player death using settings-driven values:

    - Decrements lives
    - Ends game if lives <= 0
    - Respawns player at dynamic center
    - Resets velocity
    - Restores health
    - Applies invulnerability timer (from settings)
    - Applies stun timer (from settings)
    """

    # Lose a life
    state["lives"] -= 1

    # No lives left → game over
    if state["lives"] <= 0:
        return False

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]

    # Respawn player at the dynamic center
    player.health = PLAYER_MAX_HEALTH
    player.pos = pygame.Vector2(WIDTH * 0.5, HEIGHT * 0.5)
    player.vel = pygame.Vector2(0, 0)

    # Sync rect to new position
    if hasattr(player, "rect"):
        player.rect.center = (int(player.pos.x), int(player.pos.y))

    # Apply invulnerability and stun from settings
    player.invulnerable_timer = PLAYER_INVULN_TIME
    player.stun_timer = PLAYER_STUN_TIME

    return True
