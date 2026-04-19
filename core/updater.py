import pygame


def update_all_sprites(player, joysticks, groups, debugger):
    """
    Updates all sprites in the game, including trails.
    Mirrors the original main.py update block exactly.

    Parameters:
        player      – Player instance
        joysticks   – list of joystick objects
        groups      – dict of sprite groups
        debugger    – DebuggerOverlay instance
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
                all_sprites=all_sprites
            )

            debugger.add_log(f"Updated: {sprite.__class__.__name__}")

        # Trails update separately
        trail_group.update()

    except Exception as e:
        debugger.capture_exception(e, debugger.last_sprite)
        # Skip the rest of the frame, just like original behavior
        return False

    return True
