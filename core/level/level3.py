import pygame
import random

from core.level.level import BaseLevel
from core.utils.spritesheet import load_image, slice_spritesheet
from ui.hud import HUD
from core.entities.ball import Ball
from core.entities.player import Player
from core.entities.bullet import Bullet
from core.render.boundaries import BoundariesRenderer
from core.physics.platforms import PLATFORM_TILES


class Level3(BaseLevel):

    def __init__(self, pantalla, ANCHO, ALTO):
        super().__init__(pantalla, ANCHO, ALTO)

        # ---------------------------------------------------------
        # CONFIGURACIÓN GENERAL
        # ---------------------------------------------------------
        self.tile_w = 16
        self.tile_h = 16
        self.time_remaining = 80

        # Límites + HUD
        self.setup_level_boundaries(hud_height=50, floor_offset=48)
        self.hud = HUD(ANCHO, self.hud_height, hud_y_start=0)

        # ---------------------------------------------------------
        # SPAWN DE BOLAS EN PIRÁMIDE INVERTIDA POR FILAS
        # ---------------------------------------------------------
        self.spawn_rows = self._create_pyramid_rows()
        self.current_row = 0
        self.row_delay = 1200  # ms entre cada FILA completa
        self.last_row_spawn = pygame.time.get_ticks()
        self.spawning_finished = False

        self.load_assets()
        self.spawn_initial_entities()

    # ---------------------------------------------------------
    def _create_pyramid_rows(self):
        """
        Pirámide invertida tipo oruga:
        - SOLO una bola central (fila 0)
        - Ninguna otra fila usa center_x
        """
        center_x = self.ANCHO // 2
        spacing = 90

        rows = [
            # Fila 0: cabeza de la oruga (UNA sola bola)
            [
                {"x": center_x, "vx": 0}
            ],

            # Fila 1: 2 bolas, sin centro
            [
                {"x": center_x - spacing, "vx": -4},
                {"x": center_x + spacing, "vx": 4}
            ],

            # Fila 2: 2 bolas más abiertas
            [
                {"x": center_x - spacing * 2, "vx": -4},
                {"x": center_x + spacing * 2, "vx": 4}
            ],

            # Fila 3: 2 bolas aún más abiertas
            [
                {"x": center_x - spacing * 3, "vx": -5},
                {"x": center_x + spacing * 3, "vx": 5}
            ]
        ]

        return rows


    # ---------------------------------------------------------
    def load_assets(self):
        self._load_tiles()
        Player.load_assets()
        Bullet.load_assets()
        self.setup_player()
        self._load_background()
        self._load_music()
        self._setup_boundaries_renderer()
        

    # ---------------------------------------------------------
    def _load_background(self):
        try:
            bg = load_image("assets/sprites/temple.png")
            game_area_height = self.ALTO - self.game_area_y_start
            bg_scaled = pygame.transform.scale(bg, (self.ANCHO, game_area_height))
            self.background = pygame.Surface((self.ANCHO, self.ALTO))
            self.background.fill((18, 18, 30))
            self.background.blit(bg_scaled, (0, self.game_area_y_start))
        except:
            self.background = None

    # ---------------------------------------------------------
    def _load_tiles(self):
        sheet = load_image("assets/blocks/block.png")
        raw_tiles = slice_spritesheet(sheet, 16, 16)

        PLATFORM_TILES.update({
            "top_left": raw_tiles[0],
            "top": raw_tiles[1],
            "top_right": raw_tiles[11],
            "left": raw_tiles[12],
            "fill": raw_tiles[24],
            "right": raw_tiles[23],
            "bottom_left": raw_tiles[96],
            "bottom": raw_tiles[97],
            "bottom_right": raw_tiles[107],
        })

    # ---------------------------------------------------------
    def _load_music(self):
        try:
            pygame.mixer.music.load("assets/sounds/BeepBox-Song.wav")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

    # ---------------------------------------------------------
    def _setup_boundaries_renderer(self):
        self.boundaries_renderer = BoundariesRenderer(self)

    # ---------------------------------------------------------
    def setup_player(self):
        sprites = Player._player_sprites
        self.player = Player(
            self.ANCHO // 2 - sprites[0].get_width() // 2,
            self.floor_y - sprites[0].get_height()
        )

    # ---------------------------------------------------------
    # SPAWN DE BOLAS POR FILAS
    # ---------------------------------------------------------
    def spawn_initial_entities(self):
        self.balls.clear()
        self.current_row = 0
        self.spawning_finished = False
        self.last_row_spawn = pygame.time.get_ticks()

    def update_ball_spawning(self):
        """Spawnea una FILA COMPLETA de bolas a la vez"""
        if self.current_row >= len(self.spawn_rows):
            self.spawning_finished = True
            return

        now = pygame.time.get_ticks()
        if now - self.last_row_spawn >= self.row_delay:
            
            # Obtener la fila actual
            current_row_data = self.spawn_rows[self.current_row]
            
            # Spawnear TODAS las bolas de esta fila
            for ball_data in current_row_data:
                x = ball_data["x"]
                vx = ball_data["vx"]
                
                # Asegurar límites
                x = max(self.playfield_left + 30, min(x, self.playfield_right - 30))
                
                ball = Ball(
                    x,
                    self.game_area_y_start + 20,
                    "small",
                    vx=vx,
                    vy=0
                )
                
                # Parámetros de rebote mejorados
                ball.bounce_factor = 0.70
                ball.MIN_VY = 10
                ball.MIN_BOUNCE_HEIGHT = 260
                ball.max_bounces_before_low = 6
                
                self.balls.append(ball)
            
            print(f"🎯 Fila {self.current_row + 1} spawneada: {len(current_row_data)} bolas")
            
            # Avanzar a la siguiente fila
            self.current_row += 1
            self.last_row_spawn = now

    # ---------------------------------------------------------
    def update(self, dt):
        super().update(dt)

        if not self.spawning_finished:
            self.level_won = False

        self.update_ball_spawning()

        if self.spawning_finished and not self.balls:
            self.level_won = True

    # ---------------------------------------------------------
    def draw(self):
        """Dibuja el nivel con orden correcto"""
        self._draw_background()
        self._draw_boundaries()
        self._draw_platforms()
        self._draw_entities()
        
        self.hud.update(
            lives=self.player.lives if self.player else 3,
            score=self.score,
            time=self.time_remaining,
            game_over=self.game_over,
            level_won=self.level_won
        )
        self.hud.draw(self.pantalla)

    # ---------------------------------------------------------
    def detener_musica(self):
        pygame.mixer.music.stop()