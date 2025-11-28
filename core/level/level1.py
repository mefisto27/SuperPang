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

class Level1(BaseLevel):
    def __init__(self, pantalla, ANCHO, ALTO):
        super().__init__(pantalla, ANCHO, ALTO)
        
        # Configuración específica del nivel 1
        self.setup_level_boundaries(hud_height=50, floor_offset=48)
        
        # HUD específico
        self.hud = HUD(ANCHO, self.hud_height, hud_y_start=0)
        
        # Configuración de tiles
        self.tile_w = 16
        self.tile_h = 16
        self.margin = 0
        self.spacing = 0
        self.floor_tile_idx = 0
        self.wall_tile_idx = 1
        self.ceiling_tile_idx = 1
        
        # Música
        self.music_loaded = False

        # Guardaremos las plataformas para saber sus posiciones
        self.central_platform = None
        self.left_platform = None
        self.right_platform = None

    def setup_platforms(self):
        """Configura las plataformas específicas de este nivel"""
        # Plataforma grande en el centro
        self.central_platform = self.add_centered_platform(
            self.ANCHO // 2, 
            int(self.ALTO * 0.65), 
            200, 30
        )
        
        # Plataformas más pequeñas en los costados
        y = int(self.ALTO * 0.65)

        self.left_platform = self.add_platform(100, y, 80, 20)
        self.right_platform = self.add_platform(self.ANCHO - 180, y, 80, 20)

        # Plataforma cerca del techo
        self.top_platform = self.add_centered_platform(
            self.ANCHO // 2,
            int(self.ALTO * 0.35),
            150, 25
        )
    
    def load_assets(self):
        """Carga assets específicos del nivel 1"""
        self._load_background()
        self._load_tiles()
        self._load_player_assets()
        self._load_music()
        self._setup_boundaries_renderer()
        self.setup_platforms()
        self.spawn_initial_entities()    # ← ahora sí podemos crear bolas

    def _load_background(self):
        try:
            bg = load_image("assets/woodedmountain.png")
            game_area_height = self.ALTO - self.game_area_y_start
            bg_scaled = pygame.transform.scale(bg, (self.ANCHO, game_area_height))
            self.background = pygame.Surface((self.ANCHO, self.ALTO))
            self.background.fill((18, 18, 30))
            self.background.blit(bg_scaled, (0, self.game_area_y_start))
        except Exception:
            self.background = None

    def _load_tiles(self):
        try:
            sheet = load_image("assets/blocks/block.png")
            raw_tiles = slice_spritesheet(sheet, self.tile_w, self.tile_h,
                                        margin=self.margin, spacing=self.spacing)

            self.tiles = raw_tiles  # si el nivel necesita los tiles originales

            # Tiles para plataformas
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

        except Exception as e:
            print("Error cargando tiles:", e)
            self.tiles = []

    def _load_player_assets(self):
        Player.load_assets()
        Bullet.load_assets()
        self.setup_player()

    def _load_music(self):
        try:
            pygame.mixer.music.load("assets/sounds/loop.ogg")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.music_loaded = True
        except Exception as e:
            print("Error cargando música: ", e)

    def _setup_boundaries_renderer(self):
        self.boundaries_renderer = BoundariesRenderer(self)

    def setup_player(self):
        """Configura el jugador"""
        player_sprites = Player._player_sprites
        player_x = self.ANCHO // 2 - player_sprites[0].get_width() // 2
        player_y = self.floor_y - player_sprites[0].get_height()
        self.player = Player(player_x, player_y)

    # ==========================================================================
    #  BOLAS INICIALES
    # ==========================================================================
    def spawn_initial_entities(self):
        """Genera:
        - 1 bola grande en plataforma superior
        - 2 bolas medianas en plataformas laterales
        """

        self.balls = []  # limpiar lista

        # Radios
        r_big = 40
        r_med = 25

        # ======================================================
        #  BOLA GRANDE ROJA (en plataforma superior)
        # ======================================================
        cx = self.top_platform.rect.centerx
        cy = self.top_platform.rect.top - r_big
        self.balls.append(Ball(cx, cy, "big", vx=3, vy=-8))

        # ======================================================
        #  BOLA MEDIANA IZQUIERDA
        # ======================================================
        lx = self.left_platform.rect.centerx
        ly = self.left_platform.rect.top - r_med
        self.balls.append(Ball(lx, ly, "medium", vx=3, vy=-8))

        # ======================================================
        #  BOLA MEDIANA DERECHA
        # ======================================================
        rx = self.right_platform.rect.centerx
        ry = self.right_platform.rect.top - r_med
        self.balls.append(Ball(rx, ry, "medium", vx=-3, vy=-8))


    def draw(self):
        super().draw()
        player_lives = self.player.lives if self.player else 3
        self.hud.update(
            lives=player_lives,
            score=self.score,
            time=self.time_remaining,
            game_over=self.game_over,
            level_won=self.level_won
        )
        self.hud.draw(self.pantalla)

    def detener_musica(self):
        pygame.mixer.music.stop()
