import pygame
import traceback


class DebuggerOverlay:
    def __init__(self, font):
        self.font = font
        self.active = False
        self.traceback_text = []
        self.log = []
        self.max_log = 50
        self.last_sprite = None
        self.fps_history = []

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

    def draw(self, screen, width, height):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        y = 20
        title = self.font.render("DEBUGGER — GAME PAUSED DUE TO EXCEPTION", True, (255, 200, 0))
        screen.blit(title, (20, y))
        y += 40

        screen.blit(self.font.render("Traceback:", True, (255, 255, 255)), (20, y))
        y += 30
        for line in self.traceback_text[-12:]:
            if line.strip():
                screen.blit(self.font.render(line, True, (255, 180, 180)), (40, y))
                y += 22

        y += 10
        last_sprite_text = f"Last Sprite Updated: {self.last_sprite}"
        screen.blit(self.font.render(last_sprite_text, True, (180, 255, 180)), (20, y))
        y += 30

        screen.blit(self.font.render("Recent Events:", True, (255, 255, 255)), (20, y))
        y += 30
        for entry in self.log[-10:]:
            screen.blit(self.font.render(entry, True, (200, 200, 255)), (40, y))
            y += 22

        y += 20
        screen.blit(self.font.render("FPS (last 120 frames):", True, (255, 255, 255)), (20, y))
        y += 30
        if self.fps_history:
            max_fps = max(self.fps_history) or 1
            for i, f in enumerate(self.fps_history[-100:]):
                h = int((f / max_fps) * 50)
                pygame.draw.rect(screen, (255, 255, 0), (20 + i * 3, y + 50 - h, 2, h))

        y = height - 80
        controls = "[R] Resume   [Q] Quit"
        screen.blit(self.font.render(controls, True, (255, 255, 255)), (20, y))
