import pygame
import os

_FONT_CACHE = {}

def get_arcade_font(size: int) -> pygame.font.Font:
    global _FONT_CACHE

    # Return cached font if already loaded
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]

    # Path to your arcade font
    font_path = os.path.join("assets", "fonts", "retro.ttf")

    try:
        font = pygame.font.Font(font_path, size)
    except Exception:
        # Safe fallback — never crashes
        font = pygame.font.Font(None, size)

    _FONT_CACHE[size] = font
    return font





# ============================================================
#   DRAW HELPERS
# ============================================================

def _draw_bar(surface, x, y, w, h, frac, back_color, fill_color, border_color):
    frac = max(0.0, min(1.0, frac))

    back_rect = pygame.Rect(x, y, w, h)
    fill_rect = pygame.Rect(x, y, int(w * frac), h)

    pygame.draw.rect(surface, back_color, back_rect)
    if fill_rect.width > 0:
        pygame.draw.rect(surface, fill_color, fill_rect)
    pygame.draw.rect(surface, border_color, back_rect, 2)


def _draw_text(surface, text, x, y, size=18, color=(255, 255, 255), align="topleft"):
    font = get_arcade_font(size)
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    setattr(rect, align, (x, y))
    surface.blit(surf, rect)
    return rect


# ============================================================
#   PLAYER HUD (Top‑Left)
# ============================================================

def draw_player_health(surface, player, state):
    w = state["WIDTH"]
    x = 20
    y = 20
    bar_w = int(w * 0.25)
    bar_h = 16

    max_hp = getattr(player, "max_health", getattr(player, "health", 1))
    hp = getattr(player, "health", max_hp)
    frac = hp / max_hp if max_hp > 0 else 0

    _draw_text(surface, "HP", x, y - 2, size=16, color=(180, 220, 255))
    _draw_bar(
        surface,
        x + 30,
        y,
        bar_w,
        bar_h,
        frac,
        back_color=(25, 35, 45),
        fill_color=(60, 200, 220),
        border_color=(180, 220, 255),
    )


def draw_shrapnel_cooldown(surface, player, state):
    if not hasattr(player, "shrapnel_cooldown"):
        return

    w = state["WIDTH"]
    x = 20
    y = 44
    bar_w = int(w * 0.25)
    bar_h = 10

    cd = max(0, getattr(player, "shrapnel_cooldown", 0))
    cd_max = max(1, getattr(player, "shrapnel_cooldown_max", 1))
    frac = 1.0 - (cd / cd_max)

    _draw_text(surface, "SHOT", x, y - 2, size=14, color=(180, 220, 255))
    _draw_bar(
        surface,
        x + 50,
        y,
        bar_w,
        bar_h,
        frac,
        back_color=(25, 35, 45),
        fill_color=(255, 190, 90),
        border_color=(180, 220, 255),
    )


def draw_player_meta(surface, player, state):
    x = 20
    y = 64

    # ⭐ Correct source of truth for lives
    lives = state.get("lives", 0)

    score = state.get("score", 0)
    difficulty = state.get("difficulty", "NORMAL")

    _draw_text(surface, f"LIVES: {lives}   SCORE: {score}",
               x, y, size=16, color=(200, 220, 240))

    _draw_text(surface, f"DIFFICULTY: {difficulty}",
               x, y + 20, size=14, color=(150, 200, 220))



# ============================================================
#   BOSS HUD (Top‑Right)
# ============================================================

def draw_boss_health(surface, groups, state):
    boss_group = groups.get("boss_group")
    if not boss_group:
        return

    boss = next(iter(boss_group), None)
    if boss is None:
        return

    w = state["WIDTH"]
    x = w - int(w * 0.25) - 20
    y = 20
    bar_w = int(w * 0.25)
    bar_h = 16

    max_hp = getattr(boss, "max_health", getattr(boss, "health", 1))
    hp = getattr(boss, "health", max_hp)
    frac = hp / max_hp if max_hp > 0 else 0

    _draw_text(surface, "BOSS", x + bar_w // 2, y - 2,
               size=16, color=(255, 180, 180), align="midtop")

    _draw_bar(
        surface,
        x,
        y,
        bar_w,
        bar_h,
        frac,
        back_color=(40, 20, 20),
        fill_color=(220, 80, 80),
        border_color=(255, 200, 200),
    )

    phase = getattr(boss, "phase", None)
    if phase is not None:
        _draw_text(surface, f"PHASE: {phase}",
                   x + bar_w // 2, y + bar_h + 4,
                   size=14, color=(255, 200, 200), align="midtop")


# ============================================================
#   WEAPON + POWERUPS (Bottom‑Center)
# ============================================================

def draw_weapon_mode(surface, player, state):
    w = state["WIDTH"]
    h = state["HEIGHT"]

    weapon_mode = getattr(player, "weapon_mode", "NORMAL")
    _draw_text(surface, f"WEAPON: {weapon_mode}",
               w // 2, h - 60, size=18,
               color=(180, 230, 255), align="midtop")


def draw_powerup_meter(surface, player, state, max_segments=6):
    w = state["WIDTH"]
    h = state["HEIGHT"]

    level = int(getattr(player, "powerup_level", 0))
    level = max(0, min(max_segments, level))

    label_rect = _draw_text(surface, "POWERUPS:",
                            w // 2, h - 36, size=14,
                            color=(200, 220, 240), align="midtop")

    seg_w = 14
    seg_h = 10
    padding = 4
    total_w = max_segments * seg_w + (max_segments - 1) * padding

    start_x = label_rect.centerx - total_w // 2
    y = label_rect.bottom + 4

    for i in range(max_segments):
        x = start_x + i * (seg_w + padding)
        rect = pygame.Rect(x, y, seg_w, seg_h)

        filled = i < level
        color = (70, 90, 110) if not filled else (90, 200, 160)

        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (200, 220, 240), rect, 1)


# ============================================================
#   FPS (Bottom‑Right)
# ============================================================

def draw_fps(surface, state, clock=None):
    if clock is None:
        return

    w = state["WIDTH"]
    h = state["HEIGHT"]

    fps = int(clock.get_fps())
    _draw_text(surface, f"FPS: {fps}",
               w - 20, h - 24, size=14,
               color=(180, 200, 220), align="topright")


# ============================================================
#   PUBLIC ENTRY POINT
# ============================================================

def draw(surface, player, state, groups, clock=None):
    draw_player_health(surface, player, state)
    draw_shrapnel_cooldown(surface, player, state)
    draw_player_meta(surface, player, state)

    draw_boss_health(surface, groups, state)

    draw_weapon_mode(surface, player, state)
    draw_powerup_meter(surface, player, state)

    draw_fps(surface, state, clock)
