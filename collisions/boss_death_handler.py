def handle_boss_death(boss_group, score, debugger):
    """
    Handles ONLY boss death detection and cleanup.
    Does NOT handle:
    - victory popup
    - level transitions
    - difficulty scaling
    - start_level()
    """

    if len(boss_group) == 0:
        return None  # No boss active

    boss = boss_group.sprites()[0]

    # Boss still alive
    if boss.health > 0:
        return None

    # Boss is dead — clean up
    boss.kill()
    boss_group.remove(boss)
    score += 500
    debugger.add_log("Boss defeated")

    return "dead", score
