import pygame


def update_all_sprites(player, joysticks, groups, debugger, state):
    """
    Updates all sprites in the game, including trails.
    Mirrors the original main.py update block exactly.

    Parameters:
        player      – Player instance
        joysticks   – list of joystick objects
        groups      – dict of sprite groups
        debugger    – DebuggerOverlay instance
        state       – dynamic game state (WIDTH, HEIGHT, etc.)
    """

    all_sprites = groups["all_sprites"]
    trail_group = groups["trail_group"]
    boss_bullets = groups["boss_bullets"]

    try:
        for sprite in all_sprites:
            debugger.last_sprite = sprite.__class__.__name__

            sprite.update(
                player_pos=player.pos,
                joysticks=joysticks,
                trail_group=trail_group,
                boss_bullets=boss_bullets,
                all_sprites=all_sprites,
                groups=groups,        # ⭐ CRITICAL LINE
                state=state
            )


            debugger.add_log(f"Updated: {sprite.__class__.__name__}")

        # Trails update separately
        trail_group.update(state=state)

    except Exception as e:
        debugger.capture_exception(e, debugger.last_sprite)
        return False

    return True
