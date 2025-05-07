import pygame as pg
import sys
import random

# CATSDK Game Configuration ~nya!

# Screen Constants
SCREEN_WIDTH = 512  # 256 * 2, SNES-like resolution
SCREEN_HEIGHT = 448 # 224 * 2
FPS = 60

# Physics Constants
GRAVITY = 0.7
JUMP_POWER = 13
PLAYER_MOVE_SPEED = 4
MAX_FALL_SPEED = 12

# Scale for SNES "pixels" to screen pixels
PLAYER_PIXEL_SCALE = 3   # Player art is 16x16 chars -> 48x48 screen pixels
PLATFORM_PIXEL_SCALE = 2 # Platform tiles are 8x8 chars -> 16x16 screen pixels
STAR_PIXEL_SCALE = 2     # Star art is 8x8 chars -> 16x16 screen pixels

# Global Color Map (Character to RGB mapping)
# 'T' is our special character for transparent pixels in art strings
TRANSPARENT_CHAR = 'T'
color_map = {
    'R': (224, 0, 0),      # Red (Mario-like)
    'B': (0, 100, 224),    # Blue (Mario-like)
    'Y': (255, 255, 0),    # Yellow
    'G': (0, 160, 0),      # Green
    'W': (255, 255, 255),  # White
    'K': (0, 0, 0),        # Black
    'S': (255, 184, 152),  # Skin-tone (Mario-like)
    'N': (160, 82, 45),    # Brown (Sienna-like for blocks/ground)
    'P': (255, 105, 180),  # Pink
    'O': (255, 165, 0),    # Orange
    'C': (0, 200, 200),    # Cyan/Sky Blue
    TRANSPARENT_CHAR: (1, 2, 3, 0) # Special placeholder for transparency, actual color doesn't matter if skipped.
                                   # Using an unlikely RGB with Alpha 0 for clarity.
}
BACKGROUND_COLOR = color_map['C'] # Sky blue background

# SNES-like Graphics Functions (Using your provided functions)

def create_snes_palette(colors):
    """Creates a palette list suitable for SNES-like color indexing."""
    # The user's function just returns the list, which is fine.
    # A palette in Pygame context is typically just a list of colors.
    palette = []
    for color in colors:
        palette.append(color)
    return palette

def create_snes_tile(pixel_art_rows, palette):
    """Creates a tile represented by color indices, using the global 'color_map'."""
    # This function relies on the global 'color_map' to translate chars to RGB values,
    # and then finds the index of that RGB value in the provided 'palette'.
    # palette[0] is implicitly the default/transparent index if a char/color is not found.
    tile = []
    for row_str in pixel_art_rows:
        row = []
        for char_code in row_str:
            try:
                # Get the RGB color for the character from the global map
                actual_color_rgb = color_map[char_code]
                # Find this RGB color's index in the sprite's specific palette
                color_index = palette.index(actual_color_rgb)
            except (ValueError, KeyError): # ValueError if color not in palette, KeyError if char not in color_map
                color_index = 0  # Default to index 0 of the palette
            row.append(color_index)
        tile.append(row)
    return tile

def draw_snes_tile(screen, tile_indices, palette_rgb_colors, x, y, scale):
    """Draws an SNES-style tile on the screen.
    Skips drawing for color_index 0, assuming it's transparent for the sprite."""
    for r_idx, row_indices in enumerate(tile_indices):
        for c_idx, color_idx_in_palette in enumerate(row_indices):
            # If color_index is 0, assume it's transparent for this sprite and skip drawing
            if color_idx_in_palette == 0 and palette_rgb_colors[0] == color_map[TRANSPARENT_CHAR]:
                continue
            
            # Ensure the color index is valid for the palette
            if 0 <= color_idx_in_palette < len(palette_rgb_colors):
                actual_color_to_draw = palette_rgb_colors[color_idx_in_palette]
                pg.draw.rect(screen, actual_color_to_draw,
                             (x + c_idx * scale, y + r_idx * scale, scale, scale))
            # else:
                # This case should ideally not be reached if palettes and indices are correct
                # print(f"Warning: Invalid color index {color_idx_in_palette} for palette size {len(palette_rgb_colors)}")
                # pg.draw.rect(screen, (255,0,255), # Draw magenta for error
                #              (x + c_idx * scale, y + r_idx * scale, scale, scale))


# Pixel Art Definitions ~Meow!
# 'T' is transparent. Other letters from global_color_map.

MARIO_CAT_PIXELS_RIGHT = [ # 16x16 char art
    "TTTTTTKKKKTTTTTT",
    "TTTTKKWWWWKKTTTT",
    "TTTKWSWKKWSWKTTT",
    "TTKWSWSKKWSWSKTT",
    "TTKWSWSKKWSWSKTT",
    "TTKKSSSSSSKKKKTT",
    "TTKSRSRSSRSRSKTT",
    "TTKRRRRRRRRRRKTT",
    "TTKRRRRRRRRRRKTT",
    "KKKRRRRRRRRRRKKK",
    "KWWRRRRRRRRRRWKK",
    "KWWBBBRBBBRBBWKK",
    "KWWBBBBBBBBBBWKK",
    "TTKBBBBBBBBBBKTT",
    "TTTKKKKKKKKKKTTT",
    "TTTTTTTTTTTTTTTT"
]

PLATFORM_BRICK_PIXELS = [ # 8x8 char art for a single brick tile
    "NNNNNNNN",
    "NKKNKKNK",
    "NNNNNNNN",
    "NKKNKKNK",
    "NNNNNNNN",
    "NKKnKKNK", # Lowercase 'n' for slightly different brown if desired, or use 'N'
    "NNNNNNNN",
    "NKKNKKNK"
]
# Add a slightly different brown for variety, or map 'n' to same as 'N'
if 'n' not in color_map: color_map['n'] = (150, 70, 35)


STAR_PIXELS = [ # 8x8 char art
    "TTYKKYTT",
    "TYYYYKYT",
    "YYYYYYYK",
    "YYKYYKYK",
    "YYYKKYYK",
    "TYKKKYKT",
    "TTYKKYTT",
    "TTTKKTTT"
]

# Helper to build palette for a sprite:
# Ensures palette[0] is the color associated with TRANSPARENT_CHAR
def build_sprite_palette(pixel_art_rows):
    palette = [color_map[TRANSPARENT_CHAR]] # Index 0 is for transparency
    
    unique_colors_in_art = set()
    for row_str in pixel_art_rows:
        for char_code in row_str:
            if char_code != TRANSPARENT_CHAR and char_code in color_map:
                unique_colors_in_art.add(color_map[char_code])
    
    # Add unique colors, ensuring no duplicates with palette[0] if it happened to be a real color
    for color in sorted(list(unique_colors_in_art), key=lambda c: (c[0],c[1],c[2])): # Sort for consistency
        if color not in palette:
            palette.append(color)
    return create_snes_palette(palette)


class Player(pg.sprite.Sprite):
    def __init__(self, start_x, start_y):
        super().__init__()
        self.scale = PLAYER_PIXEL_SCALE

        # Create palette specific to player art
        self.palette = build_sprite_palette(MARIO_CAT_PIXELS_RIGHT)

        # Create indexed tile maps from pixel art strings
        self.tile_map_right = create_snes_tile(MARIO_CAT_PIXELS_RIGHT, self.palette)
        
        # Create flipped version for left-facing
        mario_cat_pixels_left = ["".join(reversed(list(row))) for row in MARIO_CAT_PIXELS_RIGHT]
        self.tile_map_left = create_snes_tile(mario_cat_pixels_left, self.palette)
        
        self.current_tile_map = self.tile_map_right # Default state

        # Dimensions from art and scale for rect
        self.art_width_chars = len(MARIO_CAT_PIXELS_RIGHT[0])
        self.art_height_chars = len(MARIO_CAT_PIXELS_RIGHT)
        
        self.rect = pg.Rect(start_x, start_y, 
                             self.art_width_chars * self.scale,
                             self.art_height_chars * self.scale)

        # Movement / physics variables
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_left = False
        self.is_jumping = False # Added to control jump initiation

    def update(self, platforms):
        keys = pg.key.get_pressed()
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pg.K_LEFT]:
            self.vel_x = -PLAYER_MOVE_SPEED
            self.facing_left = True
        if keys[pg.K_RIGHT]:
            self.vel_x = PLAYER_MOVE_SPEED
            self.facing_left = False

        # Update current tile map based on direction
        if self.facing_left:
            self.current_tile_map = self.tile_map_left
        else:
            self.current_tile_map = self.tile_map_right

        # Horizontal collision
        self.rect.x += self.vel_x
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0: # Moving right
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0: # Moving left
                    self.rect.left = plat.rect.right
        
        # Vertical movement (gravity)
        if not self.on_ground:
            self.vel_y += GRAVITY
            if self.vel_y > MAX_FALL_SPEED: # Terminal velocity
                self.vel_y = MAX_FALL_SPEED
        
        # Jumping
        if keys[pg.K_SPACE] and self.on_ground: # Check K_UP or K_SPACE for jump
            self.jump()

        # Vertical collision
        self.rect.y += self.vel_y
        self.on_ground = False # Assume not on ground until collision check
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0: # Moving down
                    self.rect.bottom = plat.rect.top
                    self.on_ground = True
                    self.is_jumping = False
                    self.vel_y = 0
                elif self.vel_y < 0: # Moving up
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0 # Stop upward movement if hit ceiling
        
        # Keep player on screen bounds (optional, can be harsh)
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        # if self.rect.top < 0: self.rect.top = 0 # Allow jumping slightly off screen
        if self.rect.bottom > SCREEN_HEIGHT: # Fell off bottom
            self.reset_position() # Or game over

    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.vel_y = -JUMP_POWER
            self.on_ground = False

    def reset_position(self):
        self.rect.topleft = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, num_tiles_wide, tile_art_8x8=PLATFORM_BRICK_PIXELS):
        super().__init__()
        self.scale = PLATFORM_PIXEL_SCALE
        
        self.tile_art_width_chars = len(tile_art_8x8[0])
        self.tile_art_height_chars = len(tile_art_8x8)

        # Palette for this platform tile (can be shared if all platforms use same art)
        self.palette = build_sprite_palette(tile_art_8x8)
        
        # Create the base 8x8 indexed tile
        self.base_indexed_tile = create_snes_tile(tile_art_8x8, self.palette)

        self.num_tiles_wide = num_tiles_wide
        self.scaled_tile_width = self.tile_art_width_chars * self.scale
        self.scaled_tile_height = self.tile_art_height_chars * self.scale

        # Pygame rect for the whole platform segment
        self.rect = pg.Rect(x, y, 
                             self.num_tiles_wide * self.scaled_tile_width,
                             self.scaled_tile_height) # Assuming platforms are 1 tile high

    def draw(self, screen):
        # Tile the base_indexed_tile across the platform's width
        for i in range(self.num_tiles_wide):
            draw_x = self.rect.x + i * self.scaled_tile_width
            draw_snes_tile(screen, self.base_indexed_tile, self.palette, 
                           draw_x, self.rect.y, self.scale)


class Star(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.scale = STAR_PIXEL_SCALE

        self.palette = build_sprite_palette(STAR_PIXELS)
        self.indexed_tile_map = create_snes_tile(STAR_PIXELS, self.palette)

        self.art_width_chars = len(STAR_PIXELS[0])
        self.art_height_chars = len(STAR_PIXELS)
        
        self.rect = pg.Rect(x, y,
                             self.art_width_chars * self.scale,
                             self.art_height_chars * self.scale)
        
        # Simple bobbing animation
        self.original_y = y
        self.bob_range = 5
        self.bob_speed = 0.05
        self.bob_angle = random.uniform(0, 2 * 3.14159) # Random start phase

    def update(self):
        self.bob_angle += self.bob_speed
        self.rect.y = self.original_y + int(self.bob_range * math.sin(self.bob_angle))

    def draw(self, screen):
         draw_snes_tile(screen, self.indexed_tile_map, self.palette, 
                        self.rect.x, self.rect.y, self.scale)


# Main Game Function
async def main_async(): # Async not strictly needed for this Pygame structure but kept from user prompt
    pg.init()
    # Need math for star bobbing if we add it
    global math; import math

    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("CATSDK SNES Game ~nya!")
    clock = pg.time.Clock()

    # Game Objects
    player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50)
    
    platforms = pg.sprite.Group()
    # Ground platform
    ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH // (8 * PLATFORM_PIXEL_SCALE) + 1)
    platforms.add(ground) # Add to sprite group for potential group operations, though we draw manually
    
    # Some other platforms
    platforms.add(Platform(200, SCREEN_HEIGHT - 120, 5))
    platforms.add(Platform(350, SCREEN_HEIGHT - 200, 7))
    platforms.add(Platform(50, SCREEN_HEIGHT - 250, 4))


    stars = pg.sprite.Group()
    stars.add(Star(400, SCREEN_HEIGHT - 160))
    stars.add(Star(100, SCREEN_HEIGHT - 300))
    stars.add(Star(250, SCREEN_HEIGHT - 280))

    score = 0
    font = pg.font.Font(None, 36) # Default Pygame font

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            # if event.type == pg.KEYDOWN: # Kept jump logic in Player.update for now
            #     if event.key == pg.K_SPACE:
            #         player.jump()

        # Updates
        player.update(platforms) # Pass all platforms for collision
        stars.update() # For animations like bobbing

        # Star Collection
        collected_stars = pg.sprite.spritecollide(player, stars, True) # True to kill star on collision
        if collected_stars:
            score += len(collected_stars) * 10
            # Add a meow sound or particle effect here, purrhaps!

        # Drawing ~nya!
        screen.fill(BACKGROUND_COLOR) # Fill screen with sky blue

        # Draw Platforms
        for plat in platforms: # platforms is a Group, iterate over its sprites
            plat.draw(screen) # Call custom draw method for tiled platforms

        # Draw Stars
        for star_obj in stars: # stars is a Group
            star_obj.draw(screen) # Call custom draw method

        # Draw Player
        draw_snes_tile(screen, player.current_tile_map, player.palette, 
                       player.rect.x, player.rect.y, player.scale)
        
        # Draw Score
        score_text = font.render(f"Score: {score}", True, color_map['W'])
        screen.blit(score_text, (10, 10))

        pg.display.flip() # Update the full screen
        clock.tick(FPS) # Maintain 60 FPS

    pg.quit()
    sys.exit()

if __name__ == '__main__':
    # Pygame doesn't typically run its main loop in an asyncio context
    # unless specifically designed for it. For a standard Pygame loop,
    # we don't need asyncio.run.
    # asyncio.run(main_async()) 
    # Replacing with a direct call:
    
    # Need to ensure main_async is treated as a normal function now
    def main(): # Renaming and removing async
        pg.init()
        global math; import math # For star bobbing

        screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("CATSDK SNES Game ~nya!")
        clock = pg.time.Clock()

        player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50)
        
        platform_sprites = [] # Keep a list for collision, Group not used for drawing here
        
        ground_tile_width = 8 * PLATFORM_PIXEL_SCALE
        ground = Platform(0, SCREEN_HEIGHT - ground_tile_width, SCREEN_WIDTH // ground_tile_width + 1)
        platform_sprites.append(ground)
        
        platform_sprites.append(Platform(200, SCREEN_HEIGHT - 120, 5))
        platform_sprites.append(Platform(350, SCREEN_HEIGHT - 200, 7))
        platform_sprites.append(Platform(50, SCREEN_HEIGHT - 250, 4))

        star_sprites = pg.sprite.Group() # Use group for easy collision and updates
        star_sprites.add(Star(400, SCREEN_HEIGHT - 160))
        star_sprites.add(Star(100, SCREEN_HEIGHT - 300))
        star_sprites.add(Star(250, SCREEN_HEIGHT - 280))

        score = 0
        try:
            font = pg.font.Font(None, 36)
        except pg.error: # Fallback if default font fails (e.g. minimal Pygame install)
             font = pg.font.SysFont("sans", 30)


        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            player.update(platform_sprites) # Pass list of platform rects for collision
            star_sprites.update()

            collected = pg.sprite.spritecollide(player, star_sprites, True)
            if collected:
                score += len(collected) * 10

            screen.fill(BACKGROUND_COLOR)

            for plat in platform_sprites:
                plat.draw(screen)
            
            for star_obj in star_sprites:
                star_obj.draw(screen)

            draw_snes_tile(screen, player.current_tile_map, player.palette, 
                           player.rect.x, player.rect.y, player.scale)
            
            score_surf = font.render(f"Score: {score}", True, color_map['W'])
            screen.blit(score_surf, (10, 10))

            pg.display.flip()
            clock.tick(FPS)

        pg.quit()
        sys.exit()

    main() # Call the synchronous main function
