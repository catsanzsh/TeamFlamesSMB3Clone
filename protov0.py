import pygame as pg
import sys
import random
import math # Added for more complex stuff if needed, like Star bobbing or new effects

# CATSDK Game Configuration ~nya! MORE FUCKING POWER!

# Screen Constants
SCREEN_WIDTH = 768  # 256 * 3 (Larger view for a Mario-like game)
SCREEN_HEIGHT = 672 # 224 * 3
FPS = 60
TILE_SIZE = 48 # Effective size of one game tile (e.g., a block) on screen. Player is 1 tile wide.
                # Art will be smaller (e.g., 16x16 chars) and scaled up.

# Physics Constants
GRAVITY = 0.8
PLAYER_ACCEL = 0.8
PLAYER_FRICTION = -0.15
PLAYER_MAX_SPEED_X = 6
PLAYER_JUMP_POWER = 17
MAX_FALL_SPEED = 15
ENEMY_MOVE_SPEED = 1

# Scale for SNES "pixels" to screen pixels
# If art is 16x16 chars, and TILE_SIZE is 48, then PIXEL_SCALE = 3
PIXEL_SCALE = 3 # This will be the default scale for 16x16 character art to fit TILE_SIZE

# Global Color Map (Character to RGB mapping)
TRANSPARENT_CHAR = 'T'
color_map = {
    'R': (224, 0, 0),      # Red (Mario-like hat/shirt)
    'B': (0, 100, 224),    # Blue (Mario-like overalls)
    'Y': (255, 255, 0),    # Yellow (Coins, Stars, Q-Block)
    'G': (0, 160, 0),      # Green (Pipes, Koopas, bushes)
    'W': (255, 255, 255),  # White (Eyes, highlights, text)
    'K': (0, 0, 0),        # Black (Outlines, pupils)
    'S': (255, 184, 152),  # Skin-tone (Mario-like face/hands)
    'N': (160, 82, 45),    # Brown (Blocks, ground, Goomba body)
    'n': (120, 60, 30),    # Darker Brown (Block shadows, Goomba feet)
    'O': (255, 165, 0),    # Orange (Brick blocks)
    'o': (220, 120, 0),    # Darker Orange (Brick block shadows)
    'C': (90, 200, 255),   # Cyan/Sky Blue (Background)
    'M': (200, 70, 70),    # Mushroom Red Cap
    'F': (255, 100, 0),    # Fire Flower Orange
    'L': (100, 200, 50),   # Super Leaf Green
    'X': (150, 150, 150),  # Grey (Used blocks, castle blocks)
    'D': (50, 50, 50),     # Dark Grey / Shadow
    'E': (230, 230, 50),   # Light Yellow (Star shine)
    TRANSPARENT_CHAR: (1, 2, 3, 0) # Special placeholder for transparency
}
BACKGROUND_COLOR = color_map['C']

# --- SNES-like Graphics Functions (from your example, slightly refined) ---
def build_sprite_palette(pixel_art_rows):
    """Creates a palette for a sprite, ensuring TRANSPARENT_CHAR's color is palette[0]."""
    palette = [color_map[TRANSPARENT_CHAR]]
    unique_colors_in_art = set()
    for row_str in pixel_art_rows:
        for char_code in row_str:
            if char_code != TRANSPARENT_CHAR and char_code in color_map:
                unique_colors_in_art.add(color_map[char_code])
    for color in sorted(list(unique_colors_in_art), key=lambda c: (c[0],c[1],c[2])):
        if color not in palette:
            palette.append(color)
    return palette # This is already a list of RGB tuples, suitable for Pygame

def create_snes_tile_indices(pixel_art_rows, palette_rgb_colors):
    """Creates a tile (list of lists of color indices) from pixel art strings and a given palette."""
    tile_indices = []
    for r_idx, row_str in enumerate(pixel_art_rows):
        row_of_indices = []
        for c_idx, char_code in enumerate(row_str):
            color_to_find = color_map.get(char_code)
            if char_code == TRANSPARENT_CHAR or color_to_find is None:
                index = 0 # Assume palette_rgb_colors[0] is transparent
            else:
                try:
                    index = palette_rgb_colors.index(color_to_find)
                except ValueError: # Color from art not in this specific palette (should not happen with build_sprite_palette)
                    # print(f"Warning: Color {color_to_find} for char '{char_code}' not in provided palette. Defaulting to transparent.")
                    index = 0 
            row_of_indices.append(index)
        tile_indices.append(row_of_indices)
    return tile_indices

def draw_snes_tile_indexed(screen, tile_indices_map, palette_rgb_colors, x, y, scale):
    """Draws an SNES-style tile on the screen using pre-calculated indices."""
    # Assumes palette_rgb_colors[0] is the transparent color.
    is_transparent_color_defined = palette_rgb_colors and palette_rgb_colors[0] == color_map[TRANSPARENT_CHAR]

    for r_idx, row_of_indices in enumerate(tile_indices_map):
        for c_idx, color_idx_in_palette in enumerate(row_of_indices):
            if is_transparent_color_defined and color_idx_in_palette == 0:
                continue # Skip drawing transparent pixels if palette[0] is the designated transparent color

            if 0 <= color_idx_in_palette < len(palette_rgb_colors):
                actual_color_to_draw = palette_rgb_colors[color_idx_in_palette]
                pg.draw.rect(screen, actual_color_to_draw,
                             (x + c_idx * scale, y + r_idx * scale, scale, scale))
            # else: # Debugging for out-of-bounds index
                # print(f"Error: Invalid color index {color_idx_in_palette} for palette of size {len(palette_rgb_colors)}")


# --- ASSET DEFINITIONS (ALL FUCKING PIXEL ART STRINGS) ---
# Using 16x16 character grids for most sprites for now. Player Super might be 16x32.
# Scale will be PIXEL_SCALE (e.g., 3), so 16*3 = 48 pixels on screen.

# == PLAYER ==
# Small Player (16x16 art)
PLAYER_SM_IDLE_R_ART = [ # Small Mario-like Idle Right
    "TTTTRRRRTTTTTTTT",
    "TTTRRRRRRTTTTTTT",
    "TTTKKSSKKTTTTTTT", # Hat K, Skin S, Hair K
    "TTKSRBRSKTTTTTTT", # Skin S, Red R shirt, Blue B overall, Red R shirt, Skin S
    "TTKSBBBSKTTTTTTT", # Skin, Blue overalls, Skin
    "TTTKBKBKKTTTTTTT", # Blue overalls, buttons K?
    "TTTTBBBBBTTTTTTT",
    "TTTBRRBRBTTTTTTT", # Boots (use N for brown maybe?)
    "TTTRRNNRRTTTTTTT",
    "TTTRRTRRTRTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]
PLAYER_SM_WALK1_R_ART = [ # Small Mario-like Walk1 Right
    "TTTTRRRRTTTTTTTT",
    "TTTRRRRRRTTTTTTT",
    "TTTKKSSKKTTTTTTT",
    "TTKSRBRSKTTTTTTT",
    "TTKSBBBSKTTTTTTT",
    "TTTKBKBKKTTTTTTT",
    "TTTBBBBB TTTTTTT", # Leg moving
    "TTBRRBRB TTTTTTT",
    "TTRRNNRR TTTTTTT",
    "TTRRTRRT TTTTTTT",
    "TTT TTT TTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]
PLAYER_SM_WALK2_R_ART = [ # Small Mario-like Walk2 Right
    "TTTTRRRRTTTTTTTT",
    "TTTRRRRRRTTTTTTT",
    "TTTKKSSKKTTTTTTT",
    "TTKSRBRSKTTTTTTT",
    "TTKSBBBSKTTTTTTT",
    "TTTKBKBKKTTTTTTT",
    " TTTBBBBBTTTTTTT", # Other leg moving
    " TTRRRBRBTTTTTTT",
    " TTRNNRRTTTTTTTT",
    " TTRRTRTRTTTTTTT",
    "TTTT TTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]
PLAYER_SM_JUMP_R_ART = [ # Small Mario-like Jump Right
    "TTTTRRRRTTTTTTTT",
    "TTTRRRRRRTTTTTTT",
    "TTTKKWWKKTTTTTTT", # Wide eyes W
    "TTKSRBRSKTTTTTTT",
    "TTKSBBBSKTTTTTTT",
    "TTKKBBKKKTTTTTTT", # Arms up a bit
    "TT RBBBR RTTTTTT",
    "T R BRRB R TTTTT",
    "T R NN R TTTTTTT",
    "T RRTRRT TTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]

# Super Player (16x32 art, composed of two 16x16 tiles conceptually for drawing)
# For simplicity here, we'll define one 16x32 array of chars.
# Drawing logic will need to handle this. Or player class will have height factor.
PLAYER_LG_IDLE_R_ART = [ # Super Mario-like Idle Right (16 wide, 30-32 tall)
    "TTTTTRRRRTTTTTTT", # Row 0
    "TTTTTRRRRRTTTTTT",
    "TTTTKKKSSKKTTTTT",
    "TTTKKSWRWSKKTTTT", # W for white of eye
    "TTTKSWRWRSKTTTTT",
    "TTTKKRRRRKKTTTTT", # Red shirt part
    "TTTTTRRRRRTTTTTT",
    "TTTTTBBBBBTTTTTT", # Blue overalls part
    "TTTTBBYBYBBTTTTT", # Y for yellow buttons
    "TTTTBBBBBBBTTTTT", # Row 9
    "TTTTBBBBBBBTTTTT",
    "TTTKBKKBKBKTTTTT", # Part of arm K, then Blue, Skin, Blue ...
    "TTKSBSBKSBKTTTTT",
    "TTKSSSKSSSKTTTTT", # Hands S
    "TTKKKKKKKKKTTTTT",
    "TTTTBBBBBBBTTTTT", # Lower body / legs
    "TTTTBBBBBBBTTTTT",
    "TTTTBBBBBBBTTTTT",
    "TTT BBRRB TTTTTT",
    "TTT BBRRB TTTTTT", # Row 19
    "TTTNNRRNNTTTTTTT", # N for Brown boots
    "TTTNNRRNNTTTTTTT",
    "TTNNRRNNRRNTTTTT",
    "TTNNRRNNRRNTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT", # Row 29
    # "TTTTTTTTTTTTTTTT", # Row 30
    # "TTTTTTTTTTTTTTTT", # Row 31 - if needed for 32 height
]
# Other Super Player ART (Walk, Jump) would be similar variations. For brevity, only Idle.

# == ENEMIES ==
GOOMBA_WALK1_ART = [ # 16x16
    "TTTTNNNNNNTTTTTT", # N Brown body
    "TTTNNNNNNNNTTTTT",
    "TTNNWWNNWWNNTTTT", # W White eyes
    "TTNKKNNKKNNTTTTT", # K Black pupils
    "TTNNNNNNNNNNTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTNNNNTTTTTTT",
    "TTTTTKKKKTTTTTTT", # K Black mouth line
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTnnnnnnnnTTTTT", # n darker brown feet
    "TTTnnTTTTnnTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]
GOOMBA_WALK2_ART = [ # Slightly different for animation
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWNNWWNNTTTT",
    "TTNKKNNKKNNTTTTT",
    "TTNNNNNNNNNNTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTNNNNTTTTTTT",
    "TTTTTKKKKTTTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTnnnnnnnnTTTTT",
    "TTTTnnTTTTnnTTTT", # Feet shift
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]
GOOMBA_SQUISHED_ART = [
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWXXWWNNTTTT", # X for squished eyes
    "TTNKKNNKKNNTTTTT",
    "TTNNNNNNNNNNTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTnnnnnTTTTTT", # Squished feet
    "TTTTnnnnnnnTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]

# == BLOCKS == (All 16x16 art)
BRICK_BLOCK_ART = [
    "OOOOOOOOOOOOOOOO", # O Orange
    "OKKOOKKOOKKOOKKO", # K Black lines
    "OOOOOOOOOOOOOOOO",
    "KOOKKOOKKOOKKOOK",
    "OOOOOOOOOOOOOOOO",
    "OKKOOKKOOKKOOKKO",
    "OOOOOOOOOOOOOOOO",
    "KOOKKOOKKOOKKOOK",
    "OOOOOOOOOOOOOOOO",
    "OKKOOKKOOKKOOKKO",
    "OOOOOOOOOOOOOOOO",
    "KOOKKOOKKOOKKOOK",
    "OOOOOOOOOOOOOOOO",
    "OKKOOKKOOKKOOKKO",
    "OOOOOOOOOOOOOOOO",
    "oooooooooooooooo", # o darker orange bottom shadow
]
QUESTION_BLOCK_ART_FRAME1 = [ # Yellow block with '?'
    "YYYYYYYYYYYYYYYY", # Y Yellow
    "YKWYYYYYYYWKYYYY", # K Black, W White for '?'
    "YKKWYYYYYWKKYYYY",
    "YTTKWYYYYWKTTYYY",
    "YTTTKWWWKTTTTYYY",
    "YTTTTKWKTTTTTYYY",
    "YTTTTKWYTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YTTTTTTTTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YYYYYYYYYYYYYYYY",
    "YKKKKKKKKKKKKKKY",
    "YyyyyyyyyyyyyyyY", # y for darker yellow shadow
    "yyyyyyyyyyyyyyyy",
]
QUESTION_BLOCK_ART_FRAME2 = [ # Slight animation for '?'
    "YYYYYYYYYYYYYYYY",
    "YKWYYYYYYYWKYYYY",
    "YKKWYYYYYWKKYYYY",
    "YTTKWWYYWWKTTYYY", # '?' shifts a bit
    "YTTTKWWKTTTTTYYY",
    "YTTTTKWKTTTTTYYY",
    "YTTTTKWYTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YTTTTTTTTTTTTYYY",
    "YTTTTKWTTTTTTYYY",
    "YTTTTKWYTTTTTYYY", # Another shift
    "YYYYYYYYYYYYYYYY",
    "YKKKKKKKKKKKKKKY",
    "YyyyyyyyyyyyyyyY",
    "yyyyyyyyyyyyyyyy",
]
USED_BLOCK_ART = [ # Greyed out block
    "XXXXXXXXXXXXXXXX", # X Grey
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "XKKXKKXKKXKKXKKX",
    "XXXXXXXXXXXXXXXX",
    "DDDDDDDDDDDDDDDD", # D Dark grey shadow
]
GROUND_BLOCK_ART = [ # Simple brown ground
    "NNNNNNNNNNNNNNNN", # N Brown
    "NnnnnnnnnnnnnnnN", # n darker brown top edge
    "NnnnnnnnnnnnnnnN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN",
]

# == POWER-UPS ==
MUSHROOM_ART = [ # 16x16
    "TTTTTMMMMTTTTTTT", # M Mushroom Red Cap
    "TTTTMMMMMMTTTTTT",
    "TTTMMWWMMWWMTTTT", # W White spots
    "TTMMWWMMWWMMTTTT",
    "TTMMMMMMMMMMTTTT",
    "TTTSSSSSSSSTTTTT", # S Skin-colored stalk
    "TTSSKKSSKKSTTTTT", # K Black eyes
    "TTSSKKSSKKSTTTTT",
    "TTTSSSSSSSSTTTTT",
    "TTTTSSSSSTTTTTTT",
    "TTTTTnnnNTTTTTTT", # n, N for base shading
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]

# == COIN ==
COIN_ART_FRAME1 = [ # 16x16
    "TTTTTYYYYYYTTTTT",
    "TTTYKKKKKKYYTTTT", # K for darker outline/shading on Y coin
    "TTYKKWWWWKKYTTTT", # W for shine
    "TTYKKWWWWKKYTTTT",
    "TTYKKKKKKKKYTTTT",
    "TTYKKKKKKKKYTTTT",
    "TTYKKKKKKKKYTTTT",
    "TTYKKWWWWKKYTTTT",
    "TTYKKWWWWKKYTTTT",
    "TTTYKKKKKKYYTTTT",
    "TTTTTYYYYYYTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]
COIN_ART_FRAME2 = [ # Spinning effect - thinner
    "TTTTTTKYKTTTTTTT",
    "TTTTTKYKYKTTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTKKYKYKKTTTTT",
    "TTTTTKYKYKTTTTTT",
    "TTTTTTKYKTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
]


# --- HELPER FUNCTION TO FLIP ART ---
def flip_pixel_art(pixel_art_rows):
    return ["".join(reversed(list(row))) for row in pixel_art_rows]

# --- AnimatedSprite Class (Base for animated things) ---
class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation_frames = {} # Store {'action_facing': [ (tile_indices, palette), ... ]}
        self.current_frame_index = 0
        self.animation_speed = 0.1 # How many frames to show one sprite frame
        self.animation_timer = 0
        self.image_scale = PIXEL_SCALE
        self.state = "idle" # e.g. "idle", "walk", "jump"
        self.facing_left = False

    def load_animation_frames(self, action_name, frame_art_list_right):
        # Right-facing frames
        key_r = f"{action_name}_right"
        self.animation_frames[key_r] = []
        for art in frame_art_list_right:
            palette = build_sprite_palette(art)
            tile_indices = create_snes_tile_indices(art, palette)
            self.animation_frames[key_r].append((tile_indices, palette))
        
        # Left-facing frames (flipped)
        key_l = f"{action_name}_left"
        self.animation_frames[key_l] = []
        for art in frame_art_list_right: # Iterate original art
            flipped_art = flip_pixel_art(art)
            palette = build_sprite_palette(flipped_art) # Palette might be same if symmetrical, but build just in case
            tile_indices = create_snes_tile_indices(flipped_art, palette)
            self.animation_frames[key_l].append((tile_indices, palette))

    def get_current_animation_set(self):
        direction = "left" if self.facing_left else "right"
        # Fallback logic: if specific state (e.g. jump_left) not found, try idle_left, then action_right, then idle_right
        possible_keys = [
            f"{self.state}_{direction}",
            f"idle_{direction}",
            f"{self.state}_right", # Fallback to right if left version of state not defined
            "idle_right" # Absolute fallback
        ]
        for key in possible_keys:
            if key in self.animation_frames and self.animation_frames[key]:
                return self.animation_frames[key]
        # If truly nothing found (should not happen if idle_right is defined)
        print(f"CRITICAL FUCKING ERROR: No animation found for state {self.state}, direction {direction}")
        return [(create_snes_tile_indices(["K"], [color_map['K']]), [color_map['K']])] # Return a black square


    def update_animation(self, dt):
        self.animation_timer += dt * FPS * self.animation_speed # dt is fraction of a second
        
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set: return # Should not happen

        if self.animation_timer >= 1: # Advance frame
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(current_animation_set)
            
    def draw(self, screen, camera_offset_x, camera_offset_y):
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set: return

        tile_indices, palette = current_animation_set[self.current_frame_index]
        
        # Calculate art dimensions from tile_indices (assuming all rows same length)
        art_height_chars = len(tile_indices)
        art_width_chars = len(tile_indices[0]) if art_height_chars > 0 else 0
        
        # Adjust draw position if sprite is taller than standard tile (e.g. Super Player)
        # Player rect.y is usually ground level. If player is 2 tiles high, draw starts 1 tile above.
        draw_x = self.rect.x - camera_offset_x
        draw_y = self.rect.y - camera_offset_y
        
        # If this sprite's art is taller than TILE_SIZE when scaled (e.g., Super Mario)
        # And its rect is defined for its feet:
        # E.g. Super Mario art is 32 chars high, player_height_tiles = 2
        # rect.y is at the bottom of the 2 tiles. We need to draw starting from rect.y - (scaled_art_height - TILE_SIZE)
        
        # For Super Player (art is 16xw, ~30-32h), and rect is 1 TILE_SIZE wide, 2 TILE_SIZE high.
        # The rect.y for super player would be the top of its 2-tile height.
        # So, no special adjustment here needed if rect itself reflects the full height.
        
        # However, if player.rect.height is TILE_SIZE but art is 2*TILE_SIZE high (small vs super)
        # then if player.is_super: draw_y -= TILE_SIZE (approx)

        if hasattr(self, 'is_super_form') and self.is_super_form:
             # Super player art (e.g. PLAYER_LG_IDLE_R_ART) might be ~30-32 "chars" high.
             # Scaled art height = art_height_chars * self.image_scale
             # If player.rect.height is 2 * TILE_SIZE. And player.rect.y is its top.
             # Then this draw_y is correct.
             pass


        draw_snes_tile_indexed(screen, tile_indices, palette, draw_x, draw_y, self.image_scale)


# --- PLAYER CLASS ---
class Player(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        
        self.is_super_form = False
        self.set_form(small=True) # Initialize as small

        self.on_ground = False
        self.can_jump = True # For coyote time or double jump later, maybe
        self.jump_timer = 0 # To prevent holding jump for continuous mega jumps
        self.score = 0
        self.lives = 3
        self.invincible_timer = 0 # After taking damage or getting powerup

        self.debug_draw_rect = False # Toggle to see collision box

    def set_form(self, small=False, super_form=False):
        # Unload previous animations if any, or be smart about it
        self.animation_frames = {} # Clear old animations

        if super_form:
            self.is_super_form = True
            self.art_height_chars = 30 # Approximate for PLAYER_LG_IDLE_R_ART
            self.art_width_chars = 16
            self.player_height_tiles = 2 
            self.load_animation_frames("idle", [PLAYER_LG_IDLE_R_ART]) # Add walk/jump later
            # TODO: Define PLAYER_LG_WALK_ART, PLAYER_LG_JUMP_ART
            self.load_animation_frames("walk", [PLAYER_LG_IDLE_R_ART, PLAYER_LG_IDLE_R_ART]) # Placeholder walk
            self.load_animation_frames("jump", [PLAYER_LG_IDLE_R_ART]) # Placeholder jump
            self.image_scale = PIXEL_SCALE 
        else: # Small form
            self.is_super_form = False
            self.art_height_chars = 16 
            self.art_width_chars = 16
            self.player_height_tiles = 1
            self.load_animation_frames("idle", [PLAYER_SM_IDLE_R_ART])
            self.load_animation_frames("walk", [PLAYER_SM_WALK1_R_ART, PLAYER_SM_WALK2_R_ART])
            self.load_animation_frames("jump", [PLAYER_SM_JUMP_R_ART])
            self.image_scale = PIXEL_SCALE
        
        # Recalculate rect based on new form
        # Position is bottom-left for consistency, adjust rect.topleft
        current_bottom = self.pos.y + (self.player_height_tiles * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, 
                             current_bottom - (self.player_height_tiles * TILE_SIZE),
                             self.art_width_chars * self.image_scale, # Width of hitbox
                             self.player_height_tiles * TILE_SIZE)   # Height of hitbox
        self.current_frame_index = 0 # Reset animation


    def jump(self):
        if self.on_ground: # Can only jump if on ground
            self.vel.y = -PLAYER_JUMP_POWER
            self.on_ground = False
            self.can_jump = False # Prevent re-jump until key release or timer

    def hit_q_block(self, q_block):
        # Example: Spawn a mushroom if player is small, or score if super
        print("Player hit Q-Block!")
        if q_block.state == 'active':
            q_block.set_state('used')
            item_x = q_block.rect.centerx - (TILE_SIZE // 2)
            item_y = q_block.rect.top - TILE_SIZE # Spawn above block
            if not self.is_super_form:
                self.game.all_sprites.add(Mushroom(self.game, item_x / TILE_SIZE, item_y / TILE_SIZE))
                self.game.items.add(self.game.all_sprites.sprites()[-1]) # Add to items group
            else:
                self.score += 200 # Or spawn a coin
                # TODO: Coin spawn logic


    def grow(self):
        if not self.is_super_form:
            # Store bottom position before changing form
            bottom_pos_y = self.rect.bottom
            self.set_form(super_form=True)
            # Adjust rect.top to maintain bottom position
            self.rect.bottom = bottom_pos_y
            self.pos.y = self.rect.top # Update main pos vector
            self.invincible_timer = 60 # Brief invincibility during/after transform (1 sec)
            print("Player GROWS! WAHOO!")

    def shrink(self):
        if self.is_super_form:
            bottom_pos_y = self.rect.bottom
            self.set_form(small=True)
            self.rect.bottom = bottom_pos_y
            self.pos.y = self.rect.top
            self.invincible_timer = 120 # 2 seconds of invincibility after hit
            print("Player SHRINKS! Oh no!")
        else:
            self.die() # Small player hit again

    def die(self):
        print("Player DIED! GAME OVER MAN (not really, just lost a life)")
        self.lives -= 1
        if self.lives > 0:
            self.game.reset_level() # Or send to world map
        else:
            self.game.game_over = True # Trigger game over state
            print("ACTUAL GAME OVER! NO MORE LIVES!")


    def update(self, dt, platforms):
        self.acc = pg.math.Vector2(0, GRAVITY)
        keys = pg.key.get_pressed()

        if self.invincible_timer > 0:
            self.invincible_timer -=1

        # Horizontal Movement
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACCEL
            self.facing_left = True
        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACCEL
            self.facing_left = False
        else:
            self.facing_left = self.facing_left # Keep facing last direction if no input

        # Friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Equations of motion
        self.vel.x += self.acc.x * dt * FPS
        # Limit speed
        if abs(self.vel.x) < 0.1: self.vel.x = 0 # Stop if slow enough
        self.vel.x = max(-PLAYER_MAX_SPEED_X, min(self.vel.x, PLAYER_MAX_SPEED_X))
        
        self.pos.x += self.vel.x * dt * FPS + 0.5 * self.acc.x * (dt*FPS)**2
        self.rect.x = self.pos.x

        self.collide_with_platforms_x(platforms)

        # Vertical Movement & Jumping
        # Jump key handling needs to be edge-triggered or timed to prevent mega jumps from holding space
        if keys[pg.K_SPACE] and self.can_jump:
            self.jump()
        if not keys[pg.K_SPACE]: # Allow re-jump once key is released
             self.can_jump = True

        self.vel.y += self.acc.y * dt * FPS # Gravity applied
        if self.vel.y > MAX_FALL_SPEED: self.vel.y = MAX_FALL_SPEED
        
        self.pos.y += self.vel.y * dt * FPS + 0.5 * self.acc.y * (dt*FPS)**2
        self.rect.y = self.pos.y
        self.on_ground = False # Assume not on ground until collision check
        self.collide_with_platforms_y(platforms)

        # Determine animation state
        if abs(self.vel.x) > 0.2: # Threshold for walking animation
            self.state = "walk"
        else:
            self.state = "idle"
        if not self.on_ground:
            self.state = "jump"
        
        super().update_animation(dt)

        # Check if fell off screen
        if self.rect.top > SCREEN_HEIGHT + TILE_SIZE: # Give some leeway
            self.die()


    def collide_with_platforms_x(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0: # Moving right
                    self.rect.right = plat.rect.left
                    self.vel.x = 0
                elif self.vel.x < 0: # Moving left
                    self.rect.left = plat.rect.right
                    self.vel.x = 0
                self.pos.x = self.rect.x # Update pos from rect after collision

    def collide_with_platforms_y(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0: # Moving down
                    self.rect.bottom = plat.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0: # Moving up (hit head)
                    self.rect.top = plat.rect.bottom
                    self.vel.y = 0
                    # If it's a special block (e.g. Q-Block, Brick)
                    if hasattr(plat, 'hit_from_bottom'):
                        plat.hit_from_bottom(self) # Pass player to block
                self.pos.y = self.rect.y # Update pos from rect

    def draw_override(self, screen, camera): # Use this to ensure it's drawn via camera
        # Flashing effect if invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 6) % 2 == 0: # Blink every 6 frames
            return # Skip drawing to make it flash
            
        super().draw(screen, camera.offset.x, camera.offset.y)
        if self.debug_draw_rect:
            debug_rect = pg.Rect(self.rect.x - camera.offset.x, self.rect.y - camera.offset.y, self.rect.width, self.rect.height)
            pg.draw.rect(screen, (255,0,0), debug_rect, 1)


# --- BLOCK CLASSES ---
class Block(AnimatedSprite): # Base for all blocks
    def __init__(self, game, x_tile, y_tile, art_frames, solid=True, block_type="generic"):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.art_width_chars = 16
        self.art_height_chars = 16
        self.image_scale = PIXEL_SCALE # TILE_SIZE / self.art_width_chars 
        self.load_animation_frames("idle", art_frames) # Default state is 'idle'
        self.state = "idle" # Could be 'active', 'used', 'hit', 'breaking'
        self.animation_speed = 0.2 # Slower for blocks typically
        self.solid = solid
        self.block_type = block_type

    def hit_from_bottom(self, entity_hitting):
        # Generic hit behavior, specific blocks override this
        print(f"{self.block_type} block hit by {type(entity_hitting)}")
        # Could add a little bump animation
        pass 
    
    def update(self, dt): # Blocks might animate (e.g. Q-Block pulsing)
        super().update_animation(dt)

    def draw_override(self, screen, camera): # Use this to ensure it's drawn via camera
        super().draw(screen, camera.offset.x, camera.offset.y)

class BrickBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [BRICK_BLOCK_ART], solid=True, block_type="brick")

    def hit_from_bottom(self, player_hitting):
        if player_hitting.is_super_form:
            print("Super Player breaks Brick Block!")
            # TODO: Spawn debris particles
            self.kill() # Remove block
            # player_hitting.score += 50
        else:
            print("Small Player hits Brick Block, bonk!")
            # TODO: Small bump animation for block

class QuestionBlock(Block):
    def __init__(self, game, x_tile, y_tile, item_type="mushroom"): # item_type: mushroom, coin, fireflower, etc.
        super().__init__(game, x_tile, y_tile, 
                         [QUESTION_BLOCK_ART_FRAME1, QUESTION_BLOCK_ART_FRAME2], 
                         solid=True, block_type="qblock")
        self.state = "active" # 'active' or 'used'
        self.item_type = item_type
        self.animation_speed = 0.3 # For the '?' pulsing

    def hit_from_bottom(self, player_hitting):
        if self.state == "active":
            print("Player hit active Q-Block!")
            self.set_state_used()
            self.spawn_item(player_hitting)
        else:
            print("Player hit used Q-Block. Clunk.")
            # TODO: Play a 'clunk' sound

    def set_state_used(self):
        self.state = "used"
        # Change art to 'USED_BLOCK_ART'
        self.animation_frames = {} # Clear old animations
        self.load_animation_frames("idle", [USED_BLOCK_ART])
        self.current_frame_index = 0 # Reset animation to show used block art
        self.animation_speed = 1000 # Effectively stop animation for static used block

    def spawn_item(self, player_hitting):
        item_x_tile = self.pos.x / TILE_SIZE
        item_y_tile = (self.pos.y / TILE_SIZE) -1 # Spawn one tile above
        
        new_item = None
        if self.item_type == "mushroom":
            if not player_hitting.is_super_form: # Only spawn mushroom if player is small
                new_item = Mushroom(self.game, item_x_tile, item_y_tile)
            else: # Player is super, spawn a coin or score instead
                player_hitting.score += 200 
                # Could spawn a visual Coin object that collects itself quickly
                print("Q-Block: Player is Super, gave score instead of mushroom.")
                # TODO: Spawn a Coin animation
                pass
        elif self.item_type == "coin":
            player_hitting.score += 100
            # TODO: Spawn Coin object that animates and collects
            print("Q-Block: Coin spawned (conceptually)!")

        if new_item:
            self.game.all_sprites.add(new_item)
            self.game.items.add(new_item)


class GroundBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [GROUND_BLOCK_ART], solid=True, block_type="ground")
        # Ground blocks typically don't react to being hit from bottom in SMB
    
    def hit_from_bottom(self, player_hitting):
        # Usually, ground blocks don't do anything when hit from below
        pass

# --- ENEMY CLASSES ---
class Goomba(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE) # Standard 1x1 tile enemy
        self.art_width_chars = 16
        self.art_height_chars = 16
        self.image_scale = PIXEL_SCALE
        
        self.load_animation_frames("walk", [GOOMBA_WALK1_ART, GOOMBA_WALK2_ART])
        self.load_animation_frames("squished", [GOOMBA_SQUISHED_ART])
        
        self.state = "walk" # 'walk', 'squished'
        self.animation_speed = 0.4
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0) # Start moving left
        self.squish_timer = 0

    def update(self, dt, platforms):
        if self.state == "walk":
            self.pos.x += self.vel.x * dt * FPS
            self.rect.x = self.pos.x
            self.check_platform_edges_and_walls(platforms)
            super().update_animation(dt)
        elif self.state == "squished":
            self.squish_timer -= dt * FPS
            if self.squish_timer <= 0:
                self.kill() # Remove from all groups

        # Simple gravity (Goombas fall if platform ends)
        # This needs a proper vertical collision check too.
        # For now, assume Goombas are always on a platform or get stuck.
        # A more robust Goomba would have its own simple physics.
        # For now, let's simplify: no gravity, just horizontal movement & wall collision.

    def check_platform_edges_and_walls(self, platforms):
        # Collision with walls
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0: # Moving right, hit wall on right
                    self.rect.right = plat.rect.left
                    self.vel.x *= -1 # Turn around
                elif self.vel.x < 0: # Moving left, hit wall on left
                    self.rect.left = plat.rect.right
                    self.vel.x *= -1 # Turn around
                self.pos.x = self.rect.x
                break # Stop checking after one collision

        # Rudimentary edge detection (needs improvement, doesn't handle gaps well)
        # A better way is to cast a point down in front of the Goomba.
        # If no ground there, turn around. This is complex.
        # For now, only wall collision. Goombas might walk off edges.

    def get_squished(self, player):
        if self.state == "walk":
            self.state = "squished"
            self.vel.x = 0 # Stop moving
            self.current_frame_index = 0 # Show squished frame
            self.squish_timer = 30 # Frames to show squished sprite before disappearing
            player.score += 100
            player.vel.y = -PLAYER_JUMP_POWER / 2 # Small bounce for player
            print("Goomba SQUISHED!")

    def draw_override(self, screen, camera):
        super().draw(screen, camera.offset.x, camera.offset.y)

# --- POWER-UP / ITEM CLASSES ---
class Mushroom(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.art_width_chars = 16
        self.art_height_chars = 16
        self.image_scale = PIXEL_SCALE

        self.load_animation_frames("idle", [MUSHROOM_ART])
        self.state = "idle" # Could be 'emerging', 'moving'
        self.animation_speed = 1.0 # Static image
        self.vel = pg.math.Vector2(ENEMY_MOVE_SPEED / 2, 0) # Moves slowly
        self.on_ground = False
        self.spawn_timer = 30 # Frames to 'emerge' from block before moving

    def update(self, dt, platforms):
        if self.spawn_timer > 0:
            self.spawn_timer -= dt * FPS
            # Could add upward movement here if emerging from block
            return

        # Basic horizontal movement
        self.pos.x += self.vel.x * dt * FPS
        self.rect.x = self.pos.x
        
        # Horizontal collision with platforms (like Goomba)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0: self.rect.right = plat.rect.left; self.vel.x *= -1
                elif self.vel.x < 0: self.rect.left = plat.rect.right; self.vel.x *= -1
                self.pos.x = self.rect.x
                break
        
        # Simple gravity for mushroom
        if not self.on_ground:
            self.pos.y += GRAVITY * 2 * dt * FPS # Falls faster perhaps
            self.rect.y = self.pos.y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y >= 0: # Moving down or still
                    self.rect.bottom = plat.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.pos.y = self.rect.y
                    break 
        # No animation update needed for static mushroom sprite
        # super().update_animation(dt)

    def collected_by_player(self, player):
        if not player.is_super_form:
            player.grow()
            self.kill() # Remove mushroom
            # player.score += 1000
        else: # Player already super, just score
            player.score += 1000 
            self.kill()


    def draw_override(self, screen, camera):
        super().draw(screen, camera.offset.x, camera.offset.y)


# --- CAMERA CLASS ---
class Camera:
    def __init__(self, width_tiles, height_tiles):
        self.camera_rect = pg.Rect(0, 0, width_tiles * TILE_SIZE, height_tiles * TILE_SIZE)
        self.offset = pg.math.Vector2(0,0)
        self.world_width_pixels = 0 # Set this after loading map

    def apply(self, entity_rect): # Adjusts an entity's rect for drawing
        return entity_rect.move(self.offset.x, self.offset.y)

    def update(self, target_player):
        # Center camera on player, with limits at map edges
        # Target x is negative of player's position relative to half screen width
        x = -target_player.rect.centerx + SCREEN_WIDTH // 2
        y = -target_player.rect.centery + SCREEN_HEIGHT // 2 # Basic vertical follow too

        # Clamp camera to map boundaries
        x = min(0, x)  # Don't scroll left past map start
        y = min(0, y)  # Don't scroll up past map start
        
        # Requires knowing total map width/height in pixels
        # Max scroll left (camera x becomes negative)
        if self.world_width_pixels > SCREEN_WIDTH:
             x = max(-(self.world_width_pixels - SCREEN_WIDTH), x)
        else: # Map is narrower than screen
            x = 0 
        
        # Max scroll up (camera y becomes negative) - Assuming map height >= screen height
        # For SMB3, vertical scrolling is often limited or different (e.g., auto-scroll up)
        # Simple clamping for now:
        if self.game.map_height_pixels > SCREEN_HEIGHT:
             y = max(-(self.game.map_height_pixels - SCREEN_HEIGHT), y)
        else:
            y = 0

        self.offset = pg.math.Vector2(x, y)
        self.camera_rect.topleft = (-x, -y) # The actual viewport in world coordinates


# --- LEVEL / MAP DATA ---
# G = Ground, B = Brick, Q = Question (Mushroom), q = Question (Coin), E = Goomba, P = Player Start
# . = Empty space
LEVEL_1_DATA = [
    "............................................................",
    "............................................................",
    "............................................................",
    "..................BBQB......................................",
    "............................................................",
    "............................................................",
    ".........................BBBB...............................",
    "............................................................",
    "...................E................E.......................",
    "GGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGG",
    "GGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]


# --- GAME CLASS (Main Orchestrator) ---
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("CATSDK's Fucking SMB3 Engine - MEOW!")
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 0 # Delta time
        self.font = pg.font.Font(None, 36)
        self.game_over = False
        self.debug_mode = False

    def load_level(self, level_data):
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group() # For collision
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group() # Powerups, coins

        player_start_pos = (2, len(level_data) - 3) # Default if 'P' not found

        for row_idx, row in enumerate(level_data):
            for col_idx, tile_char in enumerate(row):
                if tile_char == 'G':
                    block = GroundBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif tile_char == 'B':
                    block = BrickBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif tile_char == 'Q': # Mushroom Q-Block
                    block = QuestionBlock(self, col_idx, row_idx, item_type="mushroom")
                    self.all_sprites.add(block)
                    self.platforms.add(block) # Q-blocks are platforms
                elif tile_char == 'q': # Coin Q-Block (not implemented visually different yet)
                    block = QuestionBlock(self, col_idx, row_idx, item_type="coin")
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif tile_char == 'E':
                    enemy = Goomba(self, col_idx, row_idx)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                elif tile_char == 'P':
                    player_start_pos = (col_idx, row_idx)
        
        self.player = Player(self, player_start_pos[0], player_start_pos[1])
        self.all_sprites.add(self.player) # Add player last so it's drawn on top of some things if needed

        self.map_width_pixels = len(level_data[0]) * TILE_SIZE
        self.map_height_pixels = len(level_data) * TILE_SIZE
        self.camera = Camera(len(level_data[0]), len(level_data))
        self.camera.game = self # Give camera a reference to game for map dims
        self.camera.world_width_pixels = self.map_width_pixels


    def reset_level(self):
        # Find player start 'P' in LEVEL_1_DATA or use a default
        player_start_x_tile, player_start_y_tile = 2, len(LEVEL_1_DATA) - 5 # A safe default
        for r, row_str in enumerate(LEVEL_1_DATA):
            for c, char_code in enumerate(row_str):
                if char_code == 'P':
                    player_start_x_tile, player_start_y_tile = c, r
                    break
            if char_code == 'P': break
        
        self.player.pos = pg.math.Vector2(player_start_x_tile * TILE_SIZE, player_start_y_tile * TILE_SIZE)
        self.player.vel = pg.math.Vector2(0, 0)
        self.player.rect.topleft = (self.player.pos.x, self.player.pos.y)
        self.player.set_form(small=True) # Reset to small Mario
        self.player.invincible_timer = 60 # Brief invincibility on reset
        
        # TODO: Reset enemies and blocks if they were changed (e.g. Goombas killed, blocks broken)
        # For now, a full reload is simpler for a reset:
        self.load_level(LEVEL_1_DATA)


    def run(self):
        self.load_level(LEVEL_1_DATA) # Load initial level
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0 # Time since last frame in seconds

            self.events()
            if not self.game_over:
                self.update()
            self.draw()
        
        pg.quit()
        sys.exit()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_F1: # Debug toggle
                    self.debug_mode = not self.debug_mode
                    self.player.debug_draw_rect = self.debug_mode
                    print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}, motherfucker!")
                if event.key == pg.K_r and self.game_over: # Restart game if game over
                    self.game_over = False
                    self.player.lives = 3
                    self.player.score = 0
                    self.reset_level()
                if event.key == pg.K_p: # Test grow
                    if not self.player.is_super_form: self.player.grow()
                    else: self.player.shrink()


    def update(self):
        self.player.update(self.dt, self.platforms)
        
        for enemy in self.enemies:
            enemy.update(self.dt, self.platforms) # Pass platforms for enemy AI/collision

        for item in self.items:
            if hasattr(item, 'update'): # Mushrooms, etc. need updates
                 item.update(self.dt, self.platforms)


        self.camera.update(self.player)

        # Player-Enemy collisions
        if self.player.invincible_timer <= 0: # Only check if not invincible
            for enemy in self.enemies:
                if enemy.state == "walk" and self.player.rect.colliderect(enemy.rect):
                    # Check if player is stomping (higher and falling)
                    # A common way: player's bottom is near enemy's top, and player is falling
                    player_bottom_center_y = self.player.rect.centery + self.player.rect.height / 2
                    is_stomp = (player_bottom_center_y < enemy.rect.centery and 
                                self.player.vel.y > 0 and 
                                self.player.rect.bottom < enemy.rect.centery + (TILE_SIZE / 3) ) # Tolerance
                    
                    if is_stomp:
                        if isinstance(enemy, Goomba):
                            enemy.get_squished(self.player)
                    else: # Player hit enemy from side or bottom
                        self.player.shrink() # Or die if already small
                        if self.player.lives <=0 and not self.game_over : self.game_over = True
                        break # Stop checking enemies for this frame after one hit

        # Player-Item collisions
        for item in self.items:
            if self.player.rect.colliderect(item.rect):
                if isinstance(item, Mushroom):
                    item.collected_by_player(self.player)
                # Add other item types (Coin, FireFlower) here

        # Update all other sprites (like animated blocks)
        for sprite in self.all_sprites:
            if sprite != self.player and sprite not in self.enemies and sprite not in self.items: # Avoid double-updating
                if hasattr(sprite, 'update'): # Check if it has an update method
                     sprite.update(self.dt)


    def draw_text(self, text, x, y, color_char='W'):
        surf = self.font.render(text, True, color_map[color_char])
        rect = surf.get_rect(topleft=(x,y))
        self.screen.blit(surf, rect)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Draw all sprites offset by camera
        # A bit inefficient to iterate all_sprites then player separately, but fine for now
        # Could sort by Y for pseudo-3D or use layers if needed.
        for sprite in self.all_sprites:
            # Only draw if on screen (basic culling) - camera viewport check
            # Sprite.rect is world coords. Camera.camera_rect is viewport in world_coords
            if sprite.rect.colliderect(self.camera.camera_rect):
                 if hasattr(sprite, 'draw_override'): # Sprites with special draw needs via camera
                    sprite.draw_override(self.screen, self.camera)
                 elif hasattr(sprite, 'draw'): # Generic animated sprite draw method
                    sprite.draw(self.screen, self.camera.offset.x, self.camera.offset.y)
        
        # UI / HUD (drawn last, not affected by camera)
        self.draw_text(f"SCORE: {self.player.score}", 20, 10)
        self.draw_text(f"LIVES: {self.player.lives}", SCREEN_WIDTH - 150, 10)
        self.draw_text(f"FPS: {self.clock.get_fps():.0f}", SCREEN_WIDTH - 150, 40, 'Y')

        if self.debug_mode:
            self.draw_text(f"Player Pos: ({self.player.pos.x:.0f}, {self.player.pos.y:.0f})", 20, 40, 'Y')
            self.draw_text(f"Player Vel: ({self.player.vel.x:.1f}, {self.player.vel.y:.1f})", 20, 70, 'Y')
            self.draw_text(f"Player State: {self.player.state}", 20, 100, 'Y')
            self.draw_text(f"On Ground: {self.player.on_ground}", 20, 130, 'Y')
            self.draw_text(f"Cam Offset: ({self.camera.offset.x:.0f}, {self.camera.offset.y:.0f})", 20, 160, 'Y')


        if self.game_over:
            s = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA) # Per-pixel alpha
            s.fill((50,50,50, 200)) # Semi-transparent dark overlay
            self.screen.blit(s, (0,0))
            self.draw_text("GAME OVER, YOU FUCKING NOOB!", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 50, 'R')
            self.draw_text("Press 'R' to suck again", SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2, 'W')

        pg.display.flip()


if __name__ == '__main__':
    print("Starting CATSDK's Fucking Awesome Game Engine Thing...")
    game_instance = Game()
    game_instance.run()
    print("Exited CATSDK's Game. Hope you didn't shit your pants.")
