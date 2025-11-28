# =============================================================================
# ui/hud.py
# HUD (Heads-Up Display)
# Renderiza información del juego: vidas, puntuación, tiempo, estados WIN/LOSE
# =============================================================================

import pygame


# -----------------------------------------------------------------------------
#region CLASE HUD
# -----------------------------------------------------------------------------
class HUD:
    # -------------------------------------------------------------------------
    # region INIT
    # -------------------------------------------------------------------------
    def __init__(self, screen_width, hud_height, hud_y_start=0):
        """
        Inicializa el HUD.

        Args:
            screen_width (int): Ancho total de la pantalla.
            hud_height (int): Alto del área visual del HUD.
            hud_y_start (int): Posición Y donde empieza el HUD.
        """
        # Dimensiones y posición
        self.width = screen_width
        self.height = hud_height
        self.screen_height = 650
        self.y_start = hud_y_start

        # Datos del juego
        self.lives = 3
        self.score = 0
        self.time = 99
        self.game_over = False
        self.level_won = False

        # Estética
        self.bg_color = (20, 20, 30)
        self.text_color = (255, 255, 255)
        self.heart_color = (220, 40, 40)

        # Ruta de fuente
        font_path = "assets/fonts/ARCADECLASSIC.TTF"

        # Cargar fuentes con fallback
        try:
            self.font = pygame.font.Font(font_path, 28)
            self.font_large = pygame.font.Font(font_path, 36)
            self.font_game_over = pygame.font.Font(font_path, 64)
            self.font_instructions = pygame.font.Font(font_path, 24)
        except Exception:
            self.font = pygame.font.SysFont('Arial', 24)
            self.font_large = pygame.font.SysFont('Arial', 32)
            self.font_game_over = pygame.font.SysFont('Arial', 48)
            self.font_instructions = pygame.font.SysFont('Arial', 18)

        # Padding
        self.padding = 15

        # Tamaño de ícono de vida (si usas heart.png)
        self.heart_size = 36
        self.heart_spacing = 20

        # Cargar ícono de corazón si existe
        try:
            heart_img = pygame.image.load("assets/sprites/heart.png").convert_alpha()
            self.heart_icon = pygame.transform.scale(heart_img, (self.heart_size, self.heart_size))
        except Exception:
            self.heart_icon = None  # fallback a dibujo geométrico
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region UPDATE
    # -------------------------------------------------------------------------
    def update(self, lives=None, score=None, time=None, game_over=None, level_won=None):
        """Actualiza el estado del HUD."""
        if lives is not None:
            self.lives = lives
        if score is not None:
            self.score = score
        if time is not None:
            self.time = time
        if game_over is not None:
            self.game_over = game_over
        if level_won is not None:
            self.level_won = level_won
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region SCORE MANAGEMENT
    # -------------------------------------------------------------------------
    def add_score(self, points):
        """Agrega puntos al marcador."""
        self.score += points
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region DRAW ENTRYPOINT
    # -------------------------------------------------------------------------
    def draw(self, screen):
        """Entry point de dibujo del HUD."""
        if self.game_over:
            self._draw_game_over(screen)
        elif self.level_won:
            self._draw_win(screen)
        else:
            self._draw_normal_hud(screen)
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region NORMAL HUD
    # -------------------------------------------------------------------------
    def _draw_normal_hud(self, screen):
        """HUD del juego en ejecución."""
        self._draw_lives(screen)
        self._draw_score(screen)
        self._draw_time(screen)
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region GAME OVER
    # -------------------------------------------------------------------------
    def _draw_game_over(self, screen):
        """Pantalla completa de Game Over."""
        overlay = pygame.Surface((self.width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        center_y = self.screen_height // 2

        # Título
        game_over_text = self.font_game_over.render("GAME OVER", True, (255, 50, 50))
        screen.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, center_y - 80))

        # Score final
        score_text = f"FINAL SCORE {self.score:06d}"
        score_surf = self.font_large.render(score_text, True, (255, 255, 255))
        screen.blit(score_surf, (self.width//2 - score_surf.get_width()//2, center_y - 20))

        # Instrucciones
        restart_text = self.font.render("Press   R   to Restart", True, (100, 255, 100))
        screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, center_y + 30))

        exit_text = self.font.render("Press   ESC   to Exit", True, (255, 100, 100))
        screen.blit(exit_text, (self.width//2 - exit_text.get_width()//2, center_y + 70))
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region WIN SCREEN
    # -------------------------------------------------------------------------
    def _draw_win(self, screen):
        """Dibuja la pantalla de victoria."""
        overlay = pygame.Surface((self.width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        win_text = self.font_game_over.render("YOU WIN!", True, (50, 255, 50))
        screen.blit(win_text, (self.width//2 - win_text.get_width()//2, self.screen_height//2 - 80))

        score_surf = self.font_large.render(f"FINAL SCORE {self.score:06d}", True, (255, 255, 255))
        screen.blit(score_surf, (self.width//2 - score_surf.get_width()//2, self.screen_height//2 - 20))

        restart_text = self.font.render("Press  R  to Restart", True, (100, 255, 100))
        screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, self.screen_height//2 + 30))
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region LIVES
    # -------------------------------------------------------------------------
    def _draw_lives(self, screen):
        """Dibuja las vidas usando heart.png si está disponible."""
        x_start = self.padding
        y = self.y_start + self.height // 2

        # Texto "Vidas"
        label = self.font.render("Vidas", True, self.text_color)
        screen.blit(label, (x_start, y - label.get_height() // 2))

        # Coordenada inicial para íconos
        heart_x = x_start + label.get_width() + 10

        for i in range(self.lives):
            cx = heart_x + i * self.heart_spacing

            if self.heart_icon:
                # Dibujar heart.png centrado verticalmente
                screen.blit(
                    self.heart_icon,
                    (cx - self.heart_size // 2, y - self.heart_size // 2)
                )
            else:
                # Fallback: corazón geométrico
                pygame.draw.circle(screen, self.heart_color, 
                                   (cx - 4, y - 2), self.heart_size // 2)
                pygame.draw.circle(screen, self.heart_color, 
                                   (cx + 4, y - 2), self.heart_size // 2)
                pygame.draw.polygon(screen, self.heart_color, [
                    (cx - 8, y),
                    (cx + 8, y),
                    (cx, y + 10)
                ])
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region SCORE
    # -------------------------------------------------------------------------
    def _draw_score(self, screen):
        """Dibuja el marcador en el centro del HUD."""
        text = f"Score {self.score:06d}"
        surf = self.font_large.render(text, True, self.text_color)
        x = self.width//2 - surf.get_width()//2
        y = self.y_start + self.height//2 - surf.get_height()//2
        screen.blit(surf, (x, y))
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region TIME
    # -------------------------------------------------------------------------
    def _draw_time(self, screen):
        """Dibuja el temporizador a la derecha."""
        text = f"Time {self.time:02d}"
        surf = self.font.render(text, True, self.text_color)

        x = self.width - surf.get_width() - self.padding
        y = self.y_start + self.height//2 - surf.get_height()//2
        screen.blit(surf, (x, y))

        # Parpadeo si queda poco tiempo
        if self.time <= 10:
            if pygame.time.get_ticks() % 1000 < 500:
                surf2 = self.font.render(text, True, (255, 50, 50))
                screen.blit(surf2, (x, y))
    # endregion
    # -------------------------------------------------------------------------

# endregion
# -----------------------------------------------------------------------------
