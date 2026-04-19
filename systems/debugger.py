import pygame
import traceback
import pygame.scrap  # clipboard support

class DebuggerOverlay:
    def __init__(self, font):
        self.font = font
        self.active = False
        self.traceback_text = []
        self.log = []
        self.max_log = 50
        self.last_sprite = None
        self.fps_history = []

        # Selection state
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.text_lines = []  # (y_position, text)

        pygame.scrap.init()

    def add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > self.max_log:
            self.log.pop(0)

    def record_fps(self, fps):
        self.fps_history.append(fps)
        if len(self.fps_history) > 120:
            self.fps_history.pop(0)

    def capture_exception(self, exc: Exception, last_sprite):
        self.active = True
        self.traceback_text = traceback.format_exc().split("\n")
        self.last_sprite = last_sprite
        self.add_log("Exception captured — debugger activated")

    # --------------------------
    #   EVENT HANDLING
    # --------------------------
    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.selecting = True
            self.selection_start = pygame.mouse.get_pos()
            self.selection_end = self.selection_start

        elif event.type == pygame.MOUSEMOTION and self.selecting:
            self.selection_end = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.selecting = False

        elif event.type == pygame.KEYDOWN:
            # Ctrl+C to copy
            if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.copy_selection()

    # --------------------------
    #   COPY SELECTED TEXT
    # --------------------------
    def copy_selection(self):
        if not self.selection_start or not self.selection_end:
            return

        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        top = min(y1, y2)
        bottom = max(y1, y2)

        selected_lines = []
        for (line_y, text) in self.text_lines:
            if top <= line_y <= bottom:
                selected_lines.append(text)

        if selected_lines:
            joined = "\n".join(selected_lines)
            pygame.scrap.put(pygame.SCRAP_TEXT, joined.encode("utf-8"))

    # --------------------------
    #   DRAW OVERLAY
    # --------------------------
    def draw(self, screen, width, height):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        y = 20
        self.text_lines = []

        def draw_line(text, color, indent=20):
            nonlocal y
            surf = self.font.render(text, True, color)
            screen.blit(surf, (indent, y))
            self.text_lines.append((y, text))
            y += 22

        draw_line("DEBUGGER — GAME PAUSED DUE TO EXCEPTION", (255, 200, 0))
        y += 20

        draw_line("Traceback:", (255, 255, 255))
        for line in self.traceback_text[-12:]:
            if line.strip():
                draw_line(line, (255, 180, 180), indent=40)

        y += 10
        draw_line(f"Last Sprite Updated: {self.last_sprite}", (180, 255, 180))

        y += 20
        draw_line("Recent Events:", (255, 255, 255))
        for entry in self.log[-10:]:
            draw_line(entry, (200, 200, 255), indent=40)

        # Draw selection rectangle
        if self.selection_start and self.selection_end:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            rect = pygame.Rect(min(x1, x2), min(y1, y2),
                               abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(screen, (255, 255, 255, 80), rect, 1)

        # Controls
        y = height - 80
        draw_line("[R] Resume   [Q] Quit   Ctrl+C to Copy Selection", (255, 255, 255))
