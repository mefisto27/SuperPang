import pygame
import math

# ================================================================
#region COLLISION SYSTEM (MAIN CLASS)
# Sistema general que agrupa todas las funciones de colisión
# ================================================================
class CollisionSystem:

    # ============================================================
    #region BULLET vs BALL
    # Colisión entre bala y bola (circular vs punto)
    # ============================================================
    @staticmethod
    def check_bullet_ball(bullet, ball):
        """Detecta colisión bala-bola (distancia centro a centro)."""
        bullet_center_x = bullet.x + bullet.width / 2
        bullet_center_y = bullet.y + bullet.height / 2
        
        dx = bullet_center_x - ball.x
        dy = bullet_center_y - ball.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < ball.radius_by_size[ball.size]
    #endregion
    # ============================================================


    # ============================================================
    #region BULLET vs PLATFORM
    # Detección simple rect-rect
    # ============================================================
    @staticmethod
    def check_bullet_platform(bullet, platform):
        """Detecta colisión bala-plataforma"""
        bullet_rect = bullet.get_hitbox()
        return bullet_rect.colliderect(platform.rect)
    #endregion
    # ============================================================


    # ============================================================
    #region BULLET vs LEVEL LIMITS
    # Detecta colisión de bala contra paredes y techo
    # ============================================================
    @staticmethod
    def check_bullet_walls(bullet, level):
        """Detecta si bala chocó con límites del nivel."""

        # TECHO (evita que pase el HUD)
        if bullet.y < level.ceiling_y + level.tile_h:
            return True

        return False


    @staticmethod
    def _check_bullet_boundary_tiles(bullet, level):
        """Verifica colisión con tiles del borde (piso, paredes, techo)."""
        bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
        
        # Techo
        ceiling_rect = pygame.Rect(level.left_wall, level.ceiling_y, 
                                   level.right_wall - level.left_wall, level.tile_h)
        if bullet_rect.colliderect(ceiling_rect):
            return True
        
        # Suelo
        floor_rect = pygame.Rect(level.left_wall, level.floor_y, 
                                 level.right_wall - level.left_wall, level.ALTO - level.floor_y)
        if bullet_rect.colliderect(floor_rect):
            return True
        
        # Pared izquierda
        left_wall_rect = pygame.Rect(level.left_wall, level.ceiling_y + level.tile_h,
                                     level.tile_w, level.floor_y - level.ceiling_y - level.tile_h)
        if bullet_rect.colliderect(left_wall_rect):
            return True
        
        # Pared derecha
        right_wall_rect = pygame.Rect(level.right_wall - level.tile_w, level.ceiling_y + level.tile_h,
                                      level.tile_w, level.floor_y - level.ceiling_y - level.tile_h)
        if bullet_rect.colliderect(right_wall_rect):
            return True
        
        return False
    #endregion
    # ============================================================


    # ============================================================
    #region PLAYER vs BALL
    # Detección de colisión entre jugador y bolas
    # ============================================================
    @staticmethod
    def check_player_ball(player, ball):
        """Detecta colisión jugador-bola con hitboxes ajustadas."""

        # Hitbox del jugador reducida
        player_padding_x = player.width * 0.2
        player_padding_y = player.height * 0.3
        
        player_hitbox_x = player.x + player_padding_x
        player_hitbox_y = player.y + player_padding_y
        player_hitbox_width = player.width - (player_padding_x * 2)
        player_hitbox_height = player.height - player_padding_y
        
        # Hitbox de la bola reducida
        ball_radius = ball.radius_by_size[ball.size] * 0.8
    
        # Colisión círculo vs rect reducido
        closest_x = max(player_hitbox_x, min(ball.x, player_hitbox_x + player_hitbox_width))
        closest_y = max(player_hitbox_y, min(ball.y, player_hitbox_y + player_hitbox_height))
        
        dx = ball.x - closest_x
        dy = ball.y - closest_y
        return (dx*dx + dy*dy) <= (ball_radius * ball_radius)
    #endregion
    # ============================================================


    # ============================================================
    #region PROCESSOR (MAIN LOGIC)
    # Motor principal que combina todas las detecciones
    # ============================================================
    def process_collisions(self, level):
        """Procesa todas las colisiones del nivel."""
        bullets_to_remove = []
        
        for bullet in level.bullets[:]:
            bullet_hit_something = False
            
            # 1. Bala vs Bolas
            for ball in level.balls[:]:
                if self.check_bullet_ball(bullet, ball):
                    self._handle_bullet_hit_ball(level, bullet, ball)
                    bullet_hit_something = True
                    break
            
            # 2. Bala vs Plataforma
            if not bullet_hit_something and hasattr(level, 'platform_system'):
                for platform in level.platform_system.platforms[:]:
                    if self.check_bullet_platform(bullet, platform):
                        bullets_to_remove.append(bullet)
                        bullet_hit_something = True

                        # Si es rompediza, se elimina
                        if platform.type == "breakable":
                            level.platform_system.platforms.remove(platform)
                        break
            
            # 3. Bala vs Límites del nivel
            if not bullet_hit_something and self.check_bullet_walls(bullet, level):
                bullets_to_remove.append(bullet)
        
        # Eliminar balas impactadas
        for bullet in bullets_to_remove:
            if bullet in level.bullets:
                level.bullets.remove(bullet)

        # 4. Bola vs Jugador
        if level.player and level.player.is_alive():
            for ball in level.balls[:]:
                if self.check_player_ball(level.player, ball):
                    level.player.take_damage()
                    break

        # 5. Jugador vs Paredes del nivel
        if level.player and level.player.is_alive():
            self.check_player_walls(level.player, level)
            self.check_player_ceiling(level.player, level)
            self.check_player_floor(level.player, level)
    #endregion
    # ============================================================


    # ============================================================
    #region INTERNAL HANDLERS
    # Handlers internos: cuando la bala golpea una bola
    # ============================================================
    def _handle_bullet_hit_ball(self, level, bullet, ball):
        """Maneja cuando una bala golpea una bola."""
        if bullet in level.bullets:
            level.bullets.remove(bullet)

        if ball in level.balls:
            level.balls.remove(ball)
            new_balls = ball.split()
            level.balls.extend(new_balls)
            level.score += 100
    #endregion
    # ============================================================


    # ============================================================
    #region PLAYER vs LEVEL WALLS
    # Límites del área jugable para el jugador
    # ============================================================
    @staticmethod
    def check_player_walls(player, level):
        """Evita que el jugador atraviese paredes laterales."""
        if player.x < level.playfield_left:
            player.x = level.playfield_left
            return True
        
        if player.x + player.width > level.playfield_right:
            player.x = level.playfield_right - player.width
            return True
        
        return False

    @staticmethod
    def check_player_ceiling(player, level):
        """Impide que el jugador suba más allá del HUD."""
        if player.y < level.game_area_y_start:
            player.y = level.game_area_y_start
            return True
        return False

    @staticmethod
    def check_player_floor(player, level):
        """Impide que el jugador atraviese el suelo."""
        if player.y + player.height > level.floor_y:
            player.y = level.floor_y - player.height
            return True
        return False
    #endregion
    # ================================================================

#endregion
# FIN DE CollisionSystem
