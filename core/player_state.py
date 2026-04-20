import pygame
from settings import PLAYER_MAX_HEALTH


def handle_player_death(player, state):
    """
    Handles player death exactly like the original main.py:

    - Decrements lives
    - Ends game if lives <= 0
    - Respawns player at center (dynamic window size)
    - Resets velocity
    - Restores health
    - Applies invulnerability timer

    Returns:
        True  – player respawned, continue game
        False – no lives left, game over
    """

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

    # Temporary invulnerability (matches original 120 frames)
    player.invulnerable_timer = 120

    return True
