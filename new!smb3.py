import pygame as pg
import asyncio
import platform
import random

# Game Configuration
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 672
FPS = 60
TILE_SIZE = 48  # Each tile is 16 chars * PIXEL_SCALE = 16 * 3 = 48 pixels
PIXEL_SCALE = 3

# Physics Constants
GRAVITY = 0.8
PLAYER_ACCEL = 0.8
PLAYER_FRICTION = -0.15
PLAYER_MAX_SPEED_X = 6
PLAYER_JUMP_POWER = 17 # Might need tweaking for SMB3 feel
MAX_FALL_SPEED = 15
ENEMY_MOVE_SPEED = 1

# --- SMB3 Color Map (Hallucinated Palette Data) ---
TRANSPARENT_CHAR = 'T'
SMB3_COLOR_MAP = {
    'T': (0,0,0,0),      # Transparent
    'R': (220, 0, 0),    # Mario Red
    'B': (0, 80, 200),   # Mario Blue overalls
    'S': (255, 200, 150),# Mario Skin
    'Y': (255, 240, 30), # Question Block Yellow
    'O': (210, 120, 30), # Block Orange/Brown (Bricks, Used Q-Block)
    'o': (160, 80, 20),  # Block Darker Orange/Brown (Shading)
    'K': (10, 10, 10),   # Black (Outlines, Eyes, Mario Hair)
    'W': (250, 250, 250),# White (Eyes, '?' on Q-block)
    'G': (0, 180, 0),    # Leaf Green / Pipe Green / Flag Green
    'g': (140, 70, 20),  # Ground Brown / Leaf Stem accent
    'N': (130, 80, 50),  # Goomba Brown Body
    'n': (80, 50, 30),   # Goomba Dark Brown Feet / Mario Shoes
    'L': (90, 200, 255), # Sky Blue (Background)
    'F': (100, 200, 50), # Leaf Light Green part
    'X': (190, 190, 190),# Light Grey (Q-Block Rivets, Flagpole)
    'D': (60, 60, 60),   # Dark Grey (general shadow/detail)
    'U': (180, 100, 60)  # Used Block main color (slightly different from brick)
}
color_map = SMB3_COLOR_MAP # Use this globally
BACKGROUND_COLOR = color_map['L']


# --- SMB3 Asset Definitions (Hallucinated ROM Graphics Data) ---

# Small Mario (Right Facing - SMB3 Style)
SMB3_MARIO_SMALL_IDLE_R_ART = [ # Standing
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKRTTTTTT", # K for hair, S for face, R for hat side
    "TTKSRSRSKRTTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT", # R for red shirt part of overall
    "TTBBBBBBBBTTTTTT", # B for blue overalls
    "TTBBRBBBRBTTTTTT",
    "TTTRRnnRRTTTTTTT", # n for brown shoes
    "TTTRnnnnRTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_MARIO_SMALL_WALK_R_ART_1 = [ # Walk frame 1
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKRTTTTTT",
    "TTKSRSRSKRTTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT",
    "TTBBBBBBBBTTTTTT",
    "TTBBRBBBRBTTTTTT",
    "TTTRRTRnRTTTTTTT", # One leg forward
    "TTTRnnnnRTTTTTTT",
    "TTTTTTnnTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_MARIO_SMALL_WALK_R_ART_2 = [ # Walk frame 2
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKRTTTTTT",
    "TTKSRSRSKRTTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT",
    "TTBBBBBBBBTTTTTT",
    "TTBBRBBBRBTTTTTT",
    "TTTRRnnRRTTTTTTT", # Other leg slightly back
    "TTTRTRTRRTTTTTTT",
    "TTTTTTnnTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_MARIO_SMALL_JUMP_R_ART = [ # Jumping
    "TTTTTRRRRTTTTTTT",
    "TTTTRRRRRRTTTTTT",
    "TTTKKSSSKBBTTTTT", # B for hand up
    "TTKSRSRSKBBTTTTT",
    "TTKSSSSSKRTTTTTT",
    "TTTKRKRRKTTTTTTT",
    "TTBBBBBBBBTTTTTT",
    "TTBBRBBBRBTTTTTT",
    "TTTTRnRTRTTTTTTT", # Legs tucked a bit
    "TTTTRnRnRTTTTTTT",
    "TTTTnnTTnnTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]

# Goomba (SMB3 Style)
SMB3_GOOMBA_WALK1_ART = [
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT", # W White part of eye, K Pupil
    "TTNKKWWWWKKNNTTT", # K Darker outline for eye
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTnnnnTTTTTTT", # n for feet
    "TTTTNnnnnNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_GOOMBA_WALK2_ART = [ # Second walk frame for Goomba
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT",
    "TTNKKWWWWKKNNTTT",
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTnnNNnnTTTTTT", # Feet alternate
    "TTTTNnnnnNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]
SMB3_GOOMBA_SQUISHED_ART = [ # Goomba when squished
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTNNNNNNNNTTTTT",
    "TTNNWWKKWWNNTTTT",
    "TTNKKWWWWKKNNTTT",
    "TTNNNNNNNNNNTTTT",
    "TTNNNNNNNNNNNNTT",
    "TTTNNNNNNNNTTTTT",
    "TTTTNNNNNNTTTTTT",
    "TTTTTnnnnTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]


# Brick Block (SMB3 Style) - Orangey-brown
SMB3_BRICK_BLOCK_ART = [
    "OOOOOOOOOOOOOOOO", # O is main brick color
    "OKKOoKKOoKKOoKKO", # K black lines, o shadow
    "OOOOOOOOOOOOOOOO",
    "OoKKOoKKOoKKOoKK",
    "OOOOOOOOOOOOOOOO",
    "OKKOoKKOoKKOoKKO",
    "OOOOOOOOOOOOOOOO",
    "OoKKOoKKOoKKOoKK",
    "OOOOOOOOOOOOOOOO",
    "OKKOoKKOoKKOoKKO",
    "OOOOOOOOOOOOOOOO",
    "OoKKOoKKOoKKOoKK",
    "OOOOOOOOOOOOOOOO",
    "OKKOoKKOoKKOoKKO",
    "OOOOOOOOOOOOOOOO",
    "oooooooooooooooo"  # Bottom shadow
]

# Question Block (SMB3 Style)
SMB3_QUESTION_BLOCK_ART_FRAME1 = [
    "YYYYYYYYYYYYYYYY", # Y is main yellow
    "YXWYYYYYYYWXYYYY", # X for rivet, W for start of '?'
    "YWKKWYYYYYWKKYWY", # K for '?' outline/shadow
    "YTWKKWYYYWKKWTYY", # T for transparent parts inside '?'
    "YTTWKKWWKKWTTTYY",
    "YTTTWKWWKWTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YTTTTWKKWTTTTTYY",
    "YTTTTWKKWTTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YXTTKWKKWKTTTXYY",
    "YWWWWKKKKWWWWWYW", # Full '?' at bottom
    "YYYYYYYYYYYYYYYY",
    "YXXXXXXXXXXXXXXY", # Rivets line
    "YooooooooooooooY", # o for shadow
    "oooooooooooooooo"
]
SMB3_QUESTION_BLOCK_ART_FRAME2 = [ # Slight '?' animation (e.g. shimmer)
    "YYYYYYYYYYYYYYYY",
    "YXWYYYYYYYWXYYYY",
    "YWKKYYYYYYWKKYWY", # '?' thinner here
    "YTWKKWYYYWKKWTYY",
    "YTTWKKWWKKWTTTYY",
    "YTTTWKWWKWTTTTYY",
    "YTTTTWKKWTTTTTYY", # '?' slightly different shape
    "YTTTTWKKWTTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YTTTTWWWWTTTTTYY",
    "YXTTKWWWWKTTTXYY", # '?' part wider
    "YWWWWKKKKWWWWWYW",
    "YYYYYYYYYYYYYYYY",
    "YXXXXXXXXXXXXXXY",
    "YooooooooooooooY",
    "oooooooooooooooo"
]
SMB3_USED_BLOCK_ART = [ # After hit, becomes a plain darker block
    "UUUUUUUUUUUUUUUU", # U for Used block color
    "UooUooUooUooUooU", # o for darker spots/texture
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "UUUUUUUUUUUUUUUU",
    "UooUooUooUooUooU",
    "UooUooUooUooUooU",
    "oooooooooooooooo" # Bottom shadow always dark
]

# Ground Block (SMB3 Style) - Brownish with some pattern
SMB3_GROUND_BLOCK_ART = [
    "gggggggggggggggg", # g as a general ground brown
    "gOgOgOgOgOgOgOgO", # O for lighter spots/texture
    "gOgOgOgOgOgOgOgO",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "DDDDDDDDDDDDDDDD", # D for darker bottom half or shadow layer
    "DDDDDDDDDDDDDDDD",
    "gggggggggggggggg",
    "gOgOgOgOgOgOgOgO",
    "gOgOgOgOgOgOgOgO",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "gggggggggggggggg",
    "DDDDDDDDDDDDDDDD",
    "DDDDDDDDDDDDDDDD"
]

# Super Leaf (SMB3 Style)
SMB3_SUPER_LEAF_ART = [
    "TTTTTTGGTTTTTTTT", # G for main green
    "TTTTTGGGGTTTTTTT",
    "TTTTGGGGGGTTTTTT",
    "TTTGGFFFFFFGTTTT", # F for light green part of leaf
    "TTGGFFFFFFFFGTTT",
    "TTGFFFFgFFFFFGTT", # g for stem/darker part
    "TTGFFFggFFFFFGTT",
    "TTGFFFggFFFFFGTT",
    "TTTGFFggggFFGTTT",
    "TTTTGFFggFFGTTTT",
    "TTTTTGFFGGTTTTTT",
    "TTTTTTGggGTTTTTT", # stem
    "TTTTTTTggTTTTTTT",
    "TTTTTTTggTTTTTTT",
    "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT"
]

# Flagpole (SMB3 Style - simplified)
SMB3_FLAGPOLE_ART = [
    "TTTTTTTTXTTTTTTT", # X for grey pole
    "TTTTTTGGGXTTTTTT", # G for green flag
    "TTTTTGGGGGXTTTTT",
    "TTTTGGGGGGXTTTTT",
    "TTTGGGGGGGXTTTTT",
    "TTTTGGGGGXTTTTTT",
    "TTTTTTGGGXTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT",
    "TTTTTTTTXTTTTTTT"
]

# SNES-like Graphics Functions (remain mostly the same, PALETTE IS KEY)
def build_sprite_palette(pixel_art_rows):
    # The global `color_map` is now our SMB3_COLOR_MAP
    # This function now implicitly uses the SMB3 palette definitions.
    palette = [(0,0,0,0)] # Index 0 is always transparent
    unique_colors_in_art = set()
    for row in pixel_art_rows:
        for char_code in row:
            if char_code != TRANSPARENT_CHAR and char_code in color_map:
                unique_colors_in_art.add(color_map[char_code])
    
    # Sort colors for consistency, though for SMB3 fixed palette this is less critical
    # if we were to dynamically build palettes per sprite.
    # Forcing it to use the global color_map as the reference for indices
    # is more accurate to how old consoles worked with fixed palettes.
    
    # Let's create a consistent palette based on sorted global color_map values
    # This ensures that the same char_code always maps to the same palette index *if* that color is used.
    # However, for SNES-style, each sprite might have a SUBSET of the master palette.
    # The current approach builds a minimal palette PER SPRITE from the global map.

    # For this implementation, we'll stick to the original dynamic palette building
    # but ensure it pulls from our SMB3_COLOR_MAP.
    
    # Create a temporary list of unique colors from the art, then sort them.
    # This means palette indices could vary per sprite if they use different subsets of colors.
    # For a more "authentic" fixed-palette system, we'd predefine palette indices.
    # But for simplicity and to keep existing structure:
    sorted_unique_colors = sorted(list(unique_colors_in_art), key=lambda c: (c[0], c[1], c[2]))
    palette.extend(sorted_unique_colors)
    return palette

def create_snes_tile_indices(pixel_art_rows, palette):
    tile_indices = []
    # The global `color_map` is used to look up the RGB tuple for a character.
    # Then, that RGB tuple is found in the *sprite's specific* `palette` list.
    for row_str in pixel_art_rows:
        indices_for_row = []
        for char_code in row_str:
            if char_code == TRANSPARENT_CHAR:
                indices_for_row.append(0) # Transparent index
            else:
                actual_color_tuple = color_map.get(char_code)
                if actual_color_tuple:
                    try:
                        indices_for_row.append(palette.index(actual_color_tuple))
                    except ValueError: # Color defined in art but somehow not in its generated palette
                        indices_for_row.append(0) # Default to transparent if error
                else: # char_code not in color_map
                    indices_for_row.append(0) # Default to transparent
        tile_indices.append(indices_for_row)
    return tile_indices

def draw_snes_tile_indexed(screen, tile_indices, palette, x, y, scale):
    for r_idx, row_of_indices in enumerate(tile_indices):
        for c_idx, palette_idx in enumerate(row_of_indices):
            if palette_idx != 0: # Palette index 0 is transparent
                color_tuple = palette[palette_idx]
                pg.draw.rect(screen, color_tuple, (x + c_idx * scale, y + r_idx * scale, scale, scale))

# Classes
class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation_frames = {}  # Stores {'action_dir': [(indices, palette), ...]}
        self.current_frame_idx = 0
        self.animation_speed = 0.1 # Default, can be overridden
        self.animation_timer = 0
        self.image_scale = PIXEL_SCALE
        self.state = "idle"
        self.facing_left = False
        # self.palette_cache = {} # Cache for palettes to avoid re-building

    def load_animation_frames(self, action_name, frame_art_list_right):
        # Right-facing frames
        key_r = f"{action_name}_right"
        processed_frames_r = []
        for art_strings in frame_art_list_right:
            #palette = self.palette_cache.get(str(art_strings))
            #if not palette:
            palette = build_sprite_palette(art_strings)
                #self.palette_cache[str(art_strings)] = palette
            indices = create_snes_tile_indices(art_strings, palette)
            processed_frames_r.append((indices, palette))
        self.animation_frames[key_r] = processed_frames_r

        # Left-facing frames (flipped)
        key_l = f"{action_name}_left"
        processed_frames_l = []
        for art_strings in frame_art_list_right: # Iterate original right-facing art
            flipped_art_strings = flip_pixel_art(art_strings)
            #palette = self.palette_cache.get(str(flipped_art_strings))
            #if not palette:
            palette = build_sprite_palette(flipped_art_strings) # Palette might be different if colors aren't symmetrical
                #self.palette_cache[str(flipped_art_strings)] = palette
            indices = create_snes_tile_indices(flipped_art_strings, palette)
            processed_frames_l.append((indices, palette))
        self.animation_frames[key_l] = processed_frames_l


    def get_current_animation_set(self):
        direction = "left" if self.facing_left else "right"
        key = f"{self.state}_{direction}"
        # Fallback to idle_right if specific animation is missing
        return self.animation_frames.get(key, self.animation_frames.get("idle_right", [([[]], [(0,0,0,0)])]))


    def update_animation(self, dt):
        self.animation_timer += dt * FPS * self.animation_speed
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set or not current_animation_set[0][0]: # Check if empty or invalid
            return

        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(current_animation_set)

    def draw(self, screen, camera_offset_x, camera_offset_y):
        current_animation_set = self.get_current_animation_set()
        if not current_animation_set or not current_animation_set[0][0]: # Check for empty animation set
             # print(f"Warning: Empty animation set for {self.__class__.__name__} state {self.state}")
             return

        if self.current_frame_index >= len(current_animation_set): # Safety check
            self.current_frame_index = 0
        
        tile_indices, palette = current_animation_set[self.current_frame_index]
        if not tile_indices: # Further safety for empty indices
            # print(f"Warning: Empty tile_indices for {self.__class__.__name__} frame {self.current_frame_index}")
            return

        draw_snes_tile_indexed(screen, tile_indices, palette, 
                               self.rect.x - camera_offset_x, 
                               self.rect.y - camera_offset_y, 
                               self.image_scale)

def flip_pixel_art(pixel_art_rows):
    return ["".join(reversed(row)) for row in pixel_art_rows]

class Player(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        self.is_super_form = False # SMB3 has more forms, but we'll stick to small for now
        self.set_form(small=True) # This will now load SMB3 small Mario
        self.on_ground = False
        self.can_jump = True # Prevent multi-jumps if key held
        self.score = 0
        self.lives = 3
        self.invincible_timer = 0 # After taking damage

    def set_form(self, small=False): # 'small' param is a bit legacy now, always small SMB3
        self.animation_frames = {} 
        # Always load small Mario SMB3 style for this version
        self.is_super_form = False 
        self.art_height_chars = 16 # Standard 16 char height for art
        self.player_height_tiles = 1 # Small Mario is 1 tile high for collision
        
        # Load SMB3 specific art
        self.load_animation_frames("idle", [SMB3_MARIO_SMALL_IDLE_R_ART])
        self.load_animation_frames("walk", [SMB3_MARIO_SMALL_WALK_R_ART_1, SMB3_MARIO_SMALL_WALK_R_ART_2])
        self.load_animation_frames("jump", [SMB3_MARIO_SMALL_JUMP_R_ART])
        
        current_x, current_y = self.pos.x, self.pos.y
        self.rect = pg.Rect(current_x, current_y, TILE_SIZE, self.player_height_tiles * TILE_SIZE)
        self.pos.x = self.rect.x # Ensure pos matches rect after potential TILE_SIZE alignment
        self.pos.y = self.rect.y


    def jump(self):
        if self.on_ground:
            self.vel.y = -PLAYER_JUMP_POWER
            self.on_ground = False
            self.can_jump = False # Set to false, reset when jump key released

    def update(self, dt, platforms):
        self.acc = pg.math.Vector2(0, GRAVITY)
        keys = pg.key.get_pressed()

        if self.invincible_timer > 0:
            self.invincible_timer -= 1 # Simple decrement, could use dt for time-based

        # Movement
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACCEL
            self.facing_left = True
        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACCEL
            self.facing_left = False
        
        # Friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Kinematics
        self.vel.x += self.acc.x * dt * FPS
        self.vel.x = max(-PLAYER_MAX_SPEED_X, min(self.vel.x, PLAYER_MAX_SPEED_X)) # Cap speed
        
        self.pos.x += self.vel.x * dt * FPS + 0.5 * self.acc.x * (dt * FPS)**2
        self.rect.x = round(self.pos.x)
        self.collide_with_platforms_x(platforms)

        # Jumping
        if keys[pg.K_SPACE]:
            if self.can_jump: # Only jump if allowed (key was released prior)
                 self.jump()
        else: # Jump key released
            self.can_jump = True

        # Vertical movement
        self.vel.y += self.acc.y * dt * FPS # Apply gravity
        self.vel.y = min(self.vel.y, MAX_FALL_SPEED) # Cap fall speed
        self.pos.y += self.vel.y * dt * FPS + 0.5 * self.acc.y * (dt*FPS)**2
        self.rect.y = round(self.pos.y)
        
        self.on_ground = False # Assume not on ground until collision check
        self.collide_with_platforms_y(platforms)

        # Update animation state
        if not self.on_ground:
            self.state = "jump"
        elif abs(self.vel.x) > 0.2: # Threshold for walking animation
            self.state = "walk"
        else:
            self.state = "idle"
        
        self.update_animation(dt)

        # Check for falling out of world
        if self.rect.top > SCREEN_HEIGHT + TILE_SIZE * 2: # A bit more leeway
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
                self.pos.x = self.rect.x

    def collide_with_platforms_y(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0: # Moving down
                    self.rect.bottom = plat.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0: # Moving up
                    self.rect.top = plat.rect.bottom
                    self.vel.y = 0 # Stop upward movement
                    if hasattr(plat, 'hit_from_bottom'):
                        plat.hit_from_bottom(self) # Player instance
                self.pos.y = self.rect.y
    
    def die(self):
        # Basic death: lose a life, reset position (or game over)
        # Add sound effect / animation later if desired
        self.lives -= 1
        if self.lives > 0:
            self.game.reset_level_soft() # Or a method that just resets player position
        else:
            self.game.game_over = True
            # Could switch to a "game over" screen state

class Block(AnimatedSprite): # Base class for static blocks
    def __init__(self, game, x_tile, y_tile, art_frames_list, solid=True, block_type="generic"):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", art_frames_list) # Blocks usually just have "idle"
        self.solid = solid
        self.block_type = block_type
        self.animation_speed = 0 # Static blocks usually don't animate unless specified

    def update(self, dt): # Blocks might animate (e.g. Q-Block)
        if self.animation_speed > 0:
             self.update_animation(dt)

class BrickBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [SMB3_BRICK_BLOCK_ART], solid=True, block_type="brick")

    def hit_from_bottom(self, player):
        # In SMB3, small Mario just bumps it. Super Mario breaks it.
        # We only have "small" Mario visually for now.
        # For simplicity, let's make it breakable if player.is_super_form (even if not visually super)
        # Or, just bump. Let's make it bump and not break for now.
        # Add a small visual bump? (move up and down quickly)
        # print(f"Brick hit by player (Super: {player.is_super_form})")
        if player.is_super_form: # Placeholder if we add super form later
             # self.kill() # Remove from all groups
             # Spawn debris? Score?
             pass # For now, super form does nothing special to bricks
        else:
            # Sound effect: bump
            pass


class QuestionBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        # Q-Blocks animate their '?'
        super().__init__(game, x_tile, y_tile, 
                         [SMB3_QUESTION_BLOCK_ART_FRAME1, SMB3_QUESTION_BLOCK_ART_FRAME2], 
                         solid=True, block_type="qblock")
        self.is_active = True # Has it been hit?
        self.animation_speed = 0.3 # Makes the '?' animate

    def hit_from_bottom(self, player):
        if self.is_active:
            self.is_active = False
            self.animation_speed = 0 # Stop '?' animation
            self.load_animation_frames("idle", [SMB3_USED_BLOCK_ART]) # Change to used block art
            self.current_frame_idx = 0 # Ensure it shows the first (only) frame of used block

            # Spawn a Super Leaf (SMB3 style)
            leaf = SuperLeaf(self.game, self.pos.x / TILE_SIZE, self.pos.y / TILE_SIZE -1) # Spawn above block
            self.game.all_sprites.add(leaf)
            self.game.items.add(leaf)
            # Add score for hitting block? Usually for item collected.

class GroundBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [SMB3_GROUND_BLOCK_ART], solid=True, block_type="ground")

class Goomba(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("walk", [SMB3_GOOMBA_WALK1_ART, SMB3_GOOMBA_WALK2_ART])
        self.load_animation_frames("squished", [SMB3_GOOMBA_SQUISHED_ART]) # Squished frame
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0) # Start moving left
        self.state = "walk"
        self.animation_speed = 0.2
        self.squish_timer = 0 # How long to show squished frame

    def update(self, dt, platforms):
        if self.state == "walk":
            self.pos.x += self.vel.x * dt * FPS
            self.rect.x = round(self.pos.x)
            
            # Basic platform collision to turn around
            for plat in platforms: # Check against solid platforms
                if plat.solid and self.rect.colliderect(plat.rect):
                    if self.vel.x > 0: # Moving right, hit something
                        self.rect.right = plat.rect.left
                        self.vel.x *= -1
                        self.facing_left = True
                    elif self.vel.x < 0: # Moving left, hit something
                        self.rect.left = plat.rect.right
                        self.vel.x *= -1
                        self.facing_left = False
                    self.pos.x = self.rect.x
                    break 
            # Gravity (Goombas are affected by gravity in SMB3 on edges)
            # Simplified: They don't fall off edges unless map designed for it
            # More advanced: raycast down to check for ground ahead.
            # For now, they turn at obstacles.

            self.update_animation(dt)

        elif self.state == "squished":
            self.squish_timer -= dt * FPS
            if self.squish_timer <= 0:
                self.kill() # Remove from game

    def get_current_animation_set(self): # Override for squished state
        if self.state == "squished":
            return self.animation_frames.get("squished_right", []) # Assumes squished art is not dir-specific
        return super().get_current_animation_set()


class SuperLeaf(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile_spawn_base): # y_tile is block's y
        super().__init__()
        self.game = game
        # Spawn animation: rise from block, then float
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile_spawn_base * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", [SMB3_SUPER_LEAF_ART]) # Leaf doesn't really animate frames
        
        self.vel = pg.math.Vector2(ENEMY_MOVE_SPEED * 0.7, 0) # Horizontal drift speed
        self.on_ground = False
        
        self.spawn_state = "rising" # "rising", "drifting", "landed"
        self.rise_height_target = (y_tile_spawn_base - 1.5) * TILE_SIZE # Rise 1.5 tiles
        self.rise_speed = -2 # Pixels per update step (negative is up)
        
        self.drift_amplitude_y = TILE_SIZE / 2 # How much it moves up/down while drifting
        self.drift_frequency_y = 0.05 # Speed of up/down drift
        self.drift_timer_y = random.uniform(0, 2 * 3.14159) # Start at random point in sine wave
        self.base_y_drift = 0 # Stores the Y pos when drifting starts

    def update(self, dt, platforms):
        if self.spawn_state == "rising":
            self.pos.y += self.rise_speed # Simple rise for now
            if self.pos.y <= self.rise_height_target:
                self.pos.y = self.rise_height_target
                self.spawn_state = "drifting"
                self.base_y_drift = self.pos.y # Set base for Y oscillation
                # Start moving horizontally, pick random direction
                self.vel.x = random.choice([ENEMY_MOVE_SPEED * 0.7, -ENEMY_MOVE_SPEED * 0.7])


        elif self.spawn_state == "drifting":
            self.pos.x += self.vel.x * dt * FPS
            
            # Y oscillation (sine wave)
            self.drift_timer_y += self.drift_frequency_y * dt * FPS
            offset_y = self.drift_amplitude_y * math.sin(self.drift_timer_y)
            self.pos.y = self.base_y_drift + offset_y

            self.rect.x = round(self.pos.x)
            self.rect.y = round(self.pos.y)

            # Collision with platforms (simplified: stop if hit solid)
            for plat in platforms:
                if plat.solid and self.rect.colliderect(plat.rect):
                    # If hit side, reverse horizontal
                    if self.vel.x > 0 and self.rect.right > plat.rect.left:
                        self.rect.right = plat.rect.left
                        self.vel.x *= -1
                    elif self.vel.x < 0 and self.rect.left < plat.rect.right:
                        self.rect.left = plat.rect.right
                        self.vel.x *= -1
                    
                    # If lands on top
                    # This drifting logic doesn't use gravity, so landing is tricky.
                    # For simplicity, leaf might pass through floor if oscillation is too large.
                    # A proper solution would involve gravity and landing detection.
                    # Let's make it stop if it hits the top of a block.
                    # Check if center of leaf is roughly above center of block it hit.
                    if abs(self.rect.centery - plat.rect.top) < TILE_SIZE / 2 and self.vel.y >=0 : # crude check for landing
                         self.pos.y = plat.rect.top - TILE_SIZE
                         self.spawn_state = "landed"
                         self.vel.x = 0 # Stop moving
                         break
                    self.pos.x = self.rect.x

        elif self.spawn_state == "landed":
            # Item sits still or slowly fades
            pass

        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        # Leaf doesn't use multi-frame animation, but call for consistency
        self.update_animation(dt) 


class Flagpole(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        # Flagpole art is usually taller than 1 tile. Rect should cover interactive part.
        # For simplicity, let's make the base tile interactive.
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE * 4) # Make it taller for collision
        self.load_animation_frames("idle", [SMB3_FLAGPOLE_ART])
        self.animation_speed = 0 # Flag usually static unless animating after grab

# Camera (remains the same)
class Camera:
    def __init__(self, width_tiles, height_tiles): # Level dimensions in tiles
        # Camera viewport is SCREEN_WIDTH, SCREEN_HEIGHT
        self.camera_rect_on_screen = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.offset = pg.math.Vector2(0, 0) # How much the world is shifted left/up
        self.world_width_pixels = 0 # Set this when level loads
        self.world_height_pixels = 0 # Set this when level loads

    def update(self, target_player):
        # Center camera on player, with bounds for level edges
        # Target x for camera's top-left such that player is centered
        target_cam_x = -target_player.rect.centerx + SCREEN_WIDTH // 2
        # Target y (if vertical scrolling was enabled)
        # target_cam_y = -target_player.rect.centery + SCREEN_HEIGHT // 2

        # Clamp camera to world boundaries
        # Max offset is 0 (left edge of world at left edge of screen)
        # Min offset is -(world_width - screen_width) (right edge of world at right edge of screen)
        clamped_cam_x = min(0, max(target_cam_x, -(self.world_width_pixels - SCREEN_WIDTH)))
        
        # For SMB3, usually no vertical scrolling unless in specific areas. For now, fixed Y.
        clamped_cam_y = 0 # Or implement vertical scrolling rules

        self.offset.x = clamped_cam_x
        self.offset.y = clamped_cam_y
        
        # The camera_rect_on_world represents the part of the world currently visible.
        # Its topleft is (-offset.x, -offset.y)
        # self.camera_rect_on_world.topleft = (-self.offset.x, -self.offset.y) # If needed for culling outside draw loop

    def get_world_view_rect(self): # Gets the rect of the camera in world coordinates
        return pg.Rect(-self.offset.x, -self.offset.y, SCREEN_WIDTH, SCREEN_HEIGHT)


# Level and Overworld Data
LEVEL_1_1_DATA = [ # Example SMB3-like structure
    "..........................................................................................F.",
    "..........................................................................................F.",
    "..................BBQB....................................................................F.",
    "..........................................................................................F.",
    ".........................BBBB.........QQQ.................................................F.",
    "..........................................................................................F.",
    "...................E................E.........E.E.........................................F.",
    "GGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
]
# Overworld not focus of this change, kept simple
OVERWORLD_DATA = [
    "                    ",
    " P . . . . . . . .  ",
    "   1   2   3   4    ",
    " . . . . . . . . .  ",
    "   5   6   7   8    ",
    " . . . . . . . . .  ",
    "   9   A   B   C    ", # A, B, C could be other worlds/castles
    "                    "
]
import math # For SuperLeaf sine wave

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("SMB3 Style Game Engine - Hallucinated ROM")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 36) # Default Pygame font
        
        self.game_state = "overworld" # "overworld", "level", "game_over", "level_complete"
        self.overworld_data = OVERWORLD_DATA
        self.mario_overworld_pos = (2,1) # Default start on 'P'
        for r, row in enumerate(self.overworld_data): # Find 'P'
            for c, char_code in enumerate(row):
                if char_code == 'P':
                    self.mario_overworld_pos = (c, r)
                    break
            if self.mario_overworld_pos[0] != 2 or self.mario_overworld_pos[1] !=1 : # if P was found
                 break
        self.overworld_cell_size = TILE_SIZE # Overworld map cells

        self.levels = {'1': LEVEL_1_1_DATA, '2': LEVEL_1_1_DATA} # Add more levels later
        
        self.game_over = False
        self.debug_mode = False # Toggle with F1

        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group() # Solid collision objects
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.flagpoles = pg.sprite.Group() # For level end

        self.player = None # Player instance, created in load_level
        self.camera = Camera(0,0) # Placeholder, configured in load_level

        self.current_level_char = '1' # To know which level to reset

    def load_level(self, level_data_str_array):
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.items.empty()
        self.flagpoles.empty()

        player_start_pos_tiles = (2, len(level_data_str_array) - 3) # Default if no 'P' in level

        for row_idx, row_str in enumerate(level_data_str_array):
            for col_idx, char_code in enumerate(row_str):
                x_pos = col_idx * TILE_SIZE
                y_pos = row_idx * TILE_SIZE
                
                if char_code == 'G':
                    block = GroundBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'B':
                    block = BrickBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'Q':
                    block = QuestionBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char_code == 'E':
                    enemy = Goomba(self, col_idx, row_idx)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                elif char_code == 'F': # Flagpole
                    flagpole = Flagpole(self, col_idx, row_idx)
                    self.all_sprites.add(flagpole)
                    self.flagpoles.add(flagpole)
                # Add 'P' for player start in level data if needed
                # elif char_code == 'P':
                #    player_start_pos_tiles = (col_idx, row_idx)
        
        self.player = Player(self, player_start_pos_tiles[0], player_start_pos_tiles[1])
        self.all_sprites.add(self.player)
        
        level_width_pixels = len(level_data_str_array[0]) * TILE_SIZE
        level_height_pixels = len(level_data_str_array) * TILE_SIZE
        self.camera = Camera(level_width_pixels // TILE_SIZE, level_height_pixels // TILE_SIZE)
        self.camera.world_width_pixels = level_width_pixels
        self.camera.world_height_pixels = level_height_pixels


    def enter_level(self, level_char_id):
        if level_char_id in self.levels:
            self.current_level_char = level_char_id
            self.load_level(self.levels[level_char_id])
            self.game_state = "level"
            self.game_over = False # Reset game over flag when entering new level
            # Player lives and score persist between levels unless reset explicitly

    def complete_level(self):
        # Play animation, tally score, then go to overworld or next level
        print("Level Complete!") # Placeholder
        self.game_state = "overworld" # For now, back to overworld
        # Could unlock next level on overworld map here

    def reset_level_soft(self): # Player died, reset position, keep score/lives
        if self.player:
            self.player.kill() # Remove old player
        player_start_pos_tiles = (2, len(self.levels[self.current_level_char]) - 3) #粗糙的
        self.player = Player(self, player_start_pos_tiles[0], player_start_pos_tiles[1])
        self.player.score = self.player.score # Keep score from before death
        self.player.lives = self.player.lives # Lives already decremented in Player.die()
        self.all_sprites.add(self.player)
        # Enemies and blocks should ideally reset too. For simplicity, only player reset.
        # A full reset would call self.load_level(self.levels[self.current_level_char])
        # but then we need to manage score/lives persistence carefully.
        # Let's do a full reload for proper reset of enemies/blocks
        current_score = self.player.score
        current_lives = self.player.lives
        self.load_level(self.levels[self.current_level_char])
        self.player.score = current_score
        self.player.lives = current_lives
        if self.player.lives <= 0: # Should be caught by Player.die but double check
            self.game_over = True


    def reset_game_hard(self): # Game Over, R pressed
        self.game_over = False
        # Reset score and lives fully for the selected level (or overall game score)
        # For now, restarting level '1' with full lives/zero score
        self.enter_level('1') # Default to level 1
        if self.player:
            self.player.score = 0
            self.player.lives = 3


    def draw_overworld(self):
        self.screen.fill(BACKGROUND_COLOR) # Use the SMB3 sky blue
        ow_tile_size = self.overworld_cell_size
        for r, row_str in enumerate(self.overworld_data):
            for c, char_code in enumerate(row_str):
                x, y = c * ow_tile_size, r * ow_tile_size
                rect = (x, y, ow_tile_size, ow_tile_size)
                if char_code == ' ': # Path or empty space
                    pg.draw.rect(self.screen, color_map['B'], rect) # Dark blue path
                elif char_code == '.': # Non-interactive decoration
                    pg.draw.rect(self.screen, color_map['G'], rect) # Green decoration
                elif char_code.isdigit() or char_code.isalpha() and char_code not in 'P': # Level node
                    pg.draw.rect(self.screen, color_map['Y'], rect) # Yellow for level
                    self.draw_text(char_code, x + ow_tile_size // 3, y + ow_tile_size // 4, 'K')
        
        # Draw Mario on overworld
        mario_ow_x = self.mario_overworld_pos[0] * ow_tile_size
        mario_ow_y = self.mario_overworld_pos[1] * ow_tile_size
        # Simple red square for Mario on overworld
        pg.draw.rect(self.screen, color_map['R'], 
                     (mario_ow_x, mario_ow_y, ow_tile_size, ow_tile_size))


    def draw_text(self, text_str, x, y, color_char_code='W'):
        text_surface = self.font.render(text_str, True, color_map[color_char_code])
        self.screen.blit(text_surface, (x,y))

    async def main(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                        return
                    if event.key == pg.K_F1: # Debug toggle
                        self.debug_mode = not self.debug_mode
                    
                    if self.game_state == "level":
                        if self.game_over and event.key == pg.K_r:
                            self.reset_game_hard()

                    elif self.game_state == "overworld":
                        new_mario_ow_pos = list(self.mario_overworld_pos)
                        moved = False
                        if event.key == pg.K_LEFT:
                            new_mario_ow_pos[0] -= 1
                            moved = True
                        elif event.key == pg.K_RIGHT:
                            new_mario_ow_pos[0] += 1
                            moved = True
                        elif event.key == pg.K_UP:
                            new_mario_ow_pos[1] -= 1
                            moved = True
                        elif event.key == pg.K_DOWN:
                            new_mario_ow_pos[1] += 1
                            moved = True
                        
                        if moved: # Check if new position is valid
                            if (0 <= new_mario_ow_pos[0] < len(self.overworld_data[0]) and
                                0 <= new_mario_ow_pos[1] < len(self.overworld_data)):
                                target_char = self.overworld_data[new_mario_ow_pos[1]][new_mario_ow_pos[0]]
                                if target_char != ' ': # Can only move on non-empty spaces
                                    self.mario_overworld_pos = tuple(new_mario_ow_pos)

                        if event.key == pg.K_SPACE: # Enter level
                            char_at_mario = self.overworld_data[self.mario_overworld_pos[1]][self.mario_overworld_pos[0]]
                            if char_at_mario in self.levels:
                                self.enter_level(char_at_mario)
            
            # --- Update Logic ---
            if self.game_state == "level" and not self.game_over:
                self.player.update(dt, self.platforms)
                for enemy in list(self.enemies): # Iterate copy for safe removal
                    enemy.update(dt, self.platforms)
                for item in list(self.items):
                    item.update(dt, self.platforms)
                
                self.camera.update(self.player)

                # Collisions: Player vs Enemies
                if self.player.invincible_timer <= 0:
                    for enemy in list(self.enemies): # Use list() if modifying group
                        if isinstance(enemy, Goomba) and enemy.state == "walk":
                            if self.player.rect.colliderect(enemy.rect):
                                # Player stomps Goomba
                                if (self.player.vel.y > 0 and # Player is falling
                                    self.player.rect.bottom < enemy.rect.centery + TILE_SIZE / 4 and # Player's feet hit top of Goomba
                                    not self.player.on_ground): # Player not on ground (mid-stomp)
                                    
                                    enemy.state = "squished"
                                    enemy.animation_speed = 0 # Stop walk animation
                                    enemy.current_frame_idx = 0 # Show squished frame
                                    enemy.vel.x = 0
                                    enemy.squish_timer = 30 # Show squished frame for 0.5 sec
                                    self.player.vel.y = -PLAYER_JUMP_POWER / 2 # Small bounce
                                    self.player.score += 100
                                else: # Player hit Goomba from side or bottom
                                    self.player.die() 
                                    break # Stop checking other enemies this frame
                
                # Collisions: Player vs Items
                for item in list(self.items):
                    if self.player.rect.colliderect(item.rect):
                        if isinstance(item, SuperLeaf):
                            # Player gets leaf - for now, just score
                            self.player.score += 1000
                            # Could set player.is_super_form = True or give raccoon powers
                            # print("Collected Super Leaf!")
                        item.kill() # Remove item

                # Collisions: Player vs Flagpole
                for flagpole in self.flagpoles:
                    if self.player.rect.colliderect(flagpole.rect):
                        self.complete_level()
                        break # Only one flagpole hit needed
            
            # --- Drawing Logic ---
            self.screen.fill(BACKGROUND_COLOR) # Sky blue

            if self.game_state == "overworld":
                self.draw_overworld()
            elif self.game_state == "level":
                # Draw all sprites relative to camera
                world_view = self.camera.get_world_view_rect()
                for sprite in self.all_sprites:
                    if sprite.rect.colliderect(world_view): # Basic culling
                         sprite.draw(self.screen, self.camera.offset.x, self.camera.offset.y)
                
                # HUD
                if self.player:
                    self.draw_text(f"SCORE: {self.player.score}", 20, 10, 'W')
                    self.draw_text(f"LIVES: {self.player.lives}", SCREEN_WIDTH - 150, 10, 'W')

                if self.game_over:
                    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
                    overlay.fill((50, 50, 50, 180)) # Semi-transparent dark overlay
                    self.screen.blit(overlay, (0,0))
                    self.draw_text("GAME OVER", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 'R')
                    self.draw_text("Press R to Restart Level", SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2, 'W')
            
            pg.display.flip()
            await asyncio.sleep(0) # Let other asyncio tasks run if any (for web version)

        pg.quit()


if __name__ == "__main__":
    # Standard desktop execution
    game_instance = Game()
    asyncio.run(game_instance.main())
# For Emscripten (web) build:
# if platform.system() == "Emscripten":
#    game_instance = Game()
#    asyncio.run(game_instance.main())
