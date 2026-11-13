"""Main game entry point with scene management."""
import pygame
from core.scene import SceneManager
from scenes import MainMenuScene, WorldScene, SurvivalScene
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    CAMERA_ENABLED, CAMERA_HOLD_TIME, CAMERA_CONFIDENCE, CAMERA_SHOW_PREVIEW
)
from core.sound_manager import sound_manager


class Game:
    """Main game class managing the game loop and scenes."""
    
    def __init__(self):
        pygame.init()
        
        # Display setup
        # Scenes always draw onto a fixed 1920x1080 canvas. Each frame the
        # canvas is scaled (letterboxed) into the real window, so the game
        # fits any screen / window size without cropping.
        self._fullscreen = False
        pygame.display.set_mode(self._initial_window_size(), pygame.RESIZABLE)
        pygame.display.set_caption("Cosmos Academy")
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
        self.screen = self.canvas  # what scenes draw on
        self._update_viewport()

        self.clock = pygame.time.Clock()
        self.running = True
        
        # Shared camera input (persists across scenes)
        self.camera_input = None
        self._camera_initialized = False
        
        # Scene manager
        self.scene_manager = SceneManager()
        self._register_scenes()
        
        # Start theme music
        sound_manager.play_theme()

        # Start at main menu
        self.scene_manager.change_scene('menu', self)
    
    def _initial_window_size(self, fill: float = 0.85):
        """Largest 16:9 window that fits comfortably on the current display."""
        try:
            desk_w, desk_h = pygame.display.get_desktop_sizes()[0]
        except (pygame.error, IndexError):
            return SCREEN_WIDTH, SCREEN_HEIGHT
        scale = min(1.0, fill * desk_w / SCREEN_WIDTH, fill * desk_h / SCREEN_HEIGHT)
        return int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)

    def _update_viewport(self):
        """Recompute where the scaled canvas sits inside the window."""
        self.window = pygame.display.get_surface()
        win_w, win_h = self.window.get_size()
        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        w = max(1, round(SCREEN_WIDTH * scale))
        h = max(1, round(SCREEN_HEIGHT * scale))
        self._view_scale = scale
        self._view_rect = pygame.Rect((win_w - w) // 2, (win_h - h) // 2, w, h)

    def _toggle_fullscreen(self):
        """F11: switch between fullscreen and a fitted window."""
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(self._initial_window_size(), pygame.RESIZABLE)
        self._update_viewport()

    def _translate_event(self, event):
        """Remap mouse coordinates from window space to 1920x1080 canvas space."""
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            attrs = dict(event.dict)
            attrs['pos'] = (int((event.pos[0] - self._view_rect.x) / self._view_scale),
                            int((event.pos[1] - self._view_rect.y) / self._view_scale))
            if 'rel' in attrs:
                attrs['rel'] = (int(event.rel[0] / self._view_scale),
                                int(event.rel[1] / self._view_scale))
            return pygame.event.Event(event.type, attrs)
        return event

    def _present(self):
        """Scale the canvas into the window (letterboxed) and flip."""
        self.window.fill((0, 0, 0))
        if self._view_rect.size == (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.window.blit(self.canvas, self._view_rect)
        else:
            scaled = pygame.transform.smoothscale(self.canvas, self._view_rect.size)
            self.window.blit(scaled, self._view_rect)
        pygame.display.flip()

    def get_camera_input(self):
        """Get or initialize the shared camera input."""
        if not CAMERA_ENABLED:
            return None
        
        if not self._camera_initialized:
            self._camera_initialized = True
            try:
                from vision.camera_input import CameraInput
                self.camera_input = CameraInput(
                    hold_time=CAMERA_HOLD_TIME,
                    confidence_threshold=CAMERA_CONFIDENCE,
                    show_preview=CAMERA_SHOW_PREVIEW
                )
                self.camera_input.start()
            except Exception as e:
                print(f"Camera input not available: {e}")
                self.camera_input = None
        
        return self.camera_input
    
    def _register_scenes(self):
        """Register all game scenes."""
        self.scene_manager.register_scene('menu', MainMenuScene)
        self.scene_manager.register_scene('world', WorldScene)
        self.scene_manager.register_scene('survival', SurvivalScene)
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000  # Delta time in seconds
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type in (pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED):
                    self._update_viewport()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                else:
                    self.scene_manager.handle_event(self._translate_event(event))
            
            # Update
            self.scene_manager.update(dt)
            
            # Draw
            self.scene_manager.draw(self.canvas)
            self._present()
        
        # Cleanup camera on exit
        if self.camera_input is not None:
            self.camera_input.stop()
        
        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
