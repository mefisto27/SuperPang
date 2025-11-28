# core/lvl/level_manager.py
import pygame

class LevelManager:
    """Gestor que controla la progresión entre niveles"""
    
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.current_level_index = 0
        self.current_level = None
        
        # Lista de clases de niveles disponibles
        # Importar aquí para evitar imports circulares
        from core.level.level1 import Level1
        # from core.level.level2 import Level2
        # from core.level.level3 import Level3
        # from core.lvl.lvl_boss import LevelBoss  # Descomenta si creas el nivel boss
        
        self.level_classes = [
            Level1#,
            #Level2,
            #Level3,
            # LevelBoss,  # Descomenta para agregar nivel boss
        ]
    
    def load_level(self, level_index=0):
        """Carga un nivel específico"""
        if level_index < 0 or level_index >= len(self.level_classes):
            print(f"Nivel {level_index} no existe")
            return False
        
        self.current_level_index = level_index
        LevelClass = self.level_classes[level_index]
        
        self.current_level = LevelClass(self.pantalla)
        self.current_level.cargar_assets()
        self.current_level.spawn_balls()
        
        print(f"Nivel {level_index + 1} cargado: {LevelClass.__name__}")
        return True
    
    def next_level(self):
        """Carga el siguiente nivel"""
        next_index = self.current_level_index + 1
        
        if next_index >= len(self.level_classes):
            print("¡Has completado todos los niveles!")
            return False
        
        return self.load_level(next_index)
    
    def restart_current_level(self):
        """Reinicia el nivel actual"""
        if self.current_level:
            self.current_level._restart_level()
    
    def handle_events(self, events):
        """Maneja eventos del nivel actual"""
        if not self.current_level:
            return True
        
        # Agregar tecla N para siguiente nivel (solo en desarrollo/debug)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:  # N = Next Level (debug)
                    if self.next_level():
                        print("Nivel siguiente cargado (modo debug)")
                        return True
        
        return self.current_level.handle_events(events)
    
    def update(self, dt):
        """Actualiza el nivel actual"""
        if self.current_level:
            self.current_level.update(dt)
            
            # Auto-avanzar al siguiente nivel si se completa
            # (Comentado por defecto, descomenta si quieres progresión automática)
            # if self.current_level.level_complete:
            #     self.next_level()
    
    def draw(self):
        """Dibuja el nivel actual"""
        if self.current_level:
            self.current_level.draw()