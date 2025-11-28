import pygame
from typing import List, Tuple, Optional

#Aca se hicieron muchas pruebas a prueba y error hasta que  funciono, 
# se puede optimizar esta clase por que no todo se usa

# ======================================================================
#region IMAGE LOADING
# Funciones básicas para cargar imágenes con soporte alpha
# ======================================================================

def load_image(path: str) -> pygame.Surface:
    """Carga una imagen desde disco con conversión alpha."""
    img = pygame.image.load(path).convert_alpha()
    return img

#endregion
# ======================================================================


# ======================================================================
#region BASIC SPRITESHEET SLICER
# Corta un spritesheet en tiles uniformes
# ======================================================================

def slice_spritesheet(sheet: pygame.Surface, tile_w: int, tile_h: int,
                      margin: int = 0, spacing: int = 0, 
                      start_x: int = 0, start_y: int = 0,
                      max_tiles: Optional[int] = None) -> List[pygame.Surface]:
    """
    Corta un spritesheet en tiles y retorna una lista de Surfaces.

    Parámetros:
        sheet: imagen completa
        tile_w / tile_h: tamaño del tile
        margin: margen externo del sheet
        spacing: espacio entre tiles
        start_x / start_y: offsets iniciales
        max_tiles: máximo número de tiles a extraer
    
    Retorna:
        Lista de surfaces representando cada tile.
    """
    tiles = []
    sheet_w, sheet_h = sheet.get_size()
    
    y = margin + start_y
    while y + tile_h <= sheet_h:
        x = margin + start_x
        while x + tile_w <= sheet_w:

            # Crear tile con transparencia
            tile = pygame.Surface((tile_w, tile_h), flags=pygame.SRCALPHA)
            tile.blit(sheet, (0, 0), pygame.Rect(x, y, tile_w, tile_h))
            tiles.append(tile)

            # Si se alcanzó el máximo, detener
            if max_tiles and len(tiles) >= max_tiles:
                return tiles
            
            x += tile_w + spacing
        
        y += tile_h + spacing
    
    return tiles

#endregion
# ======================================================================


# ======================================================================
#region MULTI-REGION SLICER
# Corta múltiples regiones distintas de un mismo spritesheet
# ======================================================================

def slice_spritesheet_regions(sheet: pygame.Surface, 
                               regions: List[dict]) -> List[pygame.Surface]:
    """
    Corta distintas regiones del spritesheet con configuraciones diferentes.

    Parámetros:
        regions: lista de diccionarios describiendo cada región.

    Retorna:
        Lista unificada de todos los tiles extraídos.
    """
    all_tiles = []
    
    for region in regions:
        tiles = slice_spritesheet(
            sheet,
            tile_w=region['tile_w'],
            tile_h=region['tile_h'],
            margin=region.get('margin', 0),
            spacing=region.get('spacing', 0),
            start_x=region.get('start_x', 0),
            start_y=region.get('start_y', 0),
            max_tiles=region.get('max_tiles', None)
        )
        all_tiles.extend(tiles)
    
    return all_tiles

#endregion
# ======================================================================


# ======================================================================
#region AUTO-DETECTOR (EXPERIMENTAL)
# Detección automática de grid en spritesheets (placeholder)
# ======================================================================

def auto_detect_tile_grid(sheet: pygame.Surface, 
                          sample_x: int, sample_y: int,
                          tolerance: int = 5) -> Tuple[int, int, int, int]:
    """
    Intenta detectar automáticamente tamaño y espaciado del tileset.
    NOTA: Esta función es un placeholder y no está implementada.

    Retorna:
        (tile_w, tile_h, spacing_x, spacing_y)
    """
    pass

#endregion
# ======================================================================


# ======================================================================
#region TILESET PREVIEW (DEBUG)
# Construye una vista previa de tiles en forma de rejilla
# ======================================================================

def draw_tileset_preview(tiles: List[pygame.Surface], 
                         cols: int = 10,
                         bg_color: Tuple[int,int,int,int] = (50, 50, 50, 255),
                         show_borders: bool = True) -> pygame.Surface:
    """
    Genera una Surface con miniaturas de los tiles para depuración.
    """

    if not tiles:
        return pygame.Surface((1, 1))
    
    tw, th = tiles[0].get_size()
    rows = (len(tiles) + cols - 1) // cols
    
    surf = pygame.Surface((cols * tw, rows * th), flags=pygame.SRCALPHA)
    surf.fill(bg_color)

    for i, tile in enumerate(tiles):
        cx = (i % cols) * tw
        cy = (i // cols) * th
        surf.blit(tile, (cx, cy))
        
        if show_borders:
            pygame.draw.rect(
                surf, (255, 255, 255, 100),
                pygame.Rect(cx, cy, tw, th), 
                1
            )
    
    return surf

#endregion
# ======================================================================


# ======================================================================
#region SAFE TILE GETTER
# Obtención segura de un tile por índice
# ======================================================================

def get_tile(tiles: List[pygame.Surface], index: int) -> Optional[pygame.Surface]:
    """Retorna un tile del índice dado o None si está fuera de rango."""
    if 0 <= index < len(tiles):
        return tiles[index]
    return None

#endregion
# ======================================================================


# ======================================================================
#region CUSTOM TILESET LOADER
# Carga específica para tu tileset personalizado
# ======================================================================

def load_your_tileset(path: str) -> List[pygame.Surface]:
    """
    Carga tu tileset particular con valores adecuados de slicing.
    En este caso: tiles de 16x16 sin margen ni espaciado.
    """
    sheet = load_image(path)
    
    tiles = slice_spritesheet(
        sheet=sheet,
        tile_w=16,
        tile_h=16,
        margin=0,
        spacing=0,
        start_x=0,
        start_y=0
    )
    
    return tiles

#endregion
# ======================================================================
