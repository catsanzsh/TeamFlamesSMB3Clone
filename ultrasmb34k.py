import pygame as pg
import asyncio
import platform
import random

# Game Configuration
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 672
FPS = 60
TILE_SIZE = 48
PIXEL_SCALE = 3

# Physics Constants
GRAVITY = 0.8
PLAYER_ACCEL = 0.8
PLAYER_FRICTION = -0.15
PLAYER_MAX_SPEED_X = 6
PLAYER_JUMP_POWER = 17
MAX_FALL_SPEED = 15
ENEMY_MOVE_SPEED = 1

# Color Map
TRANSPARENT_CHAR = 'T'
color_map = {
    'R': (224, 0, 0), 'B': (0, 100, 224), 'Y': (255, 255, 0), 'G': (0, 160, 0),
    'W': (255, 255, 255), 'K': (0, 0, 0), 'S': (255, 184, 152), 'N': (160, 82, 45),
    'n': (120, 60, 30), 'O': (255, 165, 0), 'o': (220, 120, 0), 'C': (90, 200, 255),
    'M': (200, 70, 70), 'F': (255, 100, 0), 'L': (100, 200, 50), 'X': (150, 150, 150),
    'D': (50, 50, 50), 'E': (230, 230, 50)
}
BACKGROUND_COLOR = color_map['C']

# SNES-like Graphics Functions
def build_sprite_palette(pixel_art_rows):
    palette = [color_map[TRANSPARENT_CHAR]]
    unique_colors = set()
    for row in pixel_art_rows:
        for char in row:
            if char != TRANSPARENT_CHAR and char in color_map:
                unique_colors.add(color_map[char])
    palette.extend(sorted(unique_colors, key=lambda c: (c[0], c[1], c[2])))
    return palette

def create_snes_tile_indices(pixel_art_rows, palette):
    tile_indices = []
    for row in pixel_art_rows:
        indices = []
        for char in row:
            color = color_map.get(char)
            indices.append(0 if char == TRANSPARENT_CHAR or color is None else palette.index(color))
        tile_indices.append(indices)
    return tile_indices

def draw_snes_tile_indexed(screen, tile_indices, palette, x, y, scale):
    for r_idx, row in enumerate(tile_indices):
        for c_idx, color_idx in enumerate(row):
            if color_idx != 0:
                pg.draw.rect(screen, palette[color_idx], (x + c_idx * scale, y + r_idx * scale, scale, scale))

# Asset Definitions (Simplified for brevity; full definitions in original code)
PLAYER_SM_IDLE_R_ART = [
    "TTTTRRRRTTTTTTTT", "TTTRRRRRRTTTTTTT", "TTTKKSSKKTTTTTTT", "TTKSRBRSKTTTTTTT",
    "TTKSBBBSKTTTTTTT", "TTTKBKBKKTTTTTTT", "TTTTBBBBBTTTTTTT", "TTTBRRBRBTTTTTTT",
    "TTTRRNNRRTTTTTTT", "TTTRRTRRTRTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT"
]
GOOMBA_WALK1_ART = [
    "TTTTNNNNNNTTTTTT", "TTTNNNNNNNNTTTTT", "TTNNWWNNWWNNTTTT", "TTNKKNNKKNNTTTTT",
    "TTNNNNNNNNNNTTTT", "TTTNNNNNNNNTTTTT", "TTTTNNNNNNTTTTTT", "TTTTTNNNNTTTTTTT",
    "TTTTTKKKKTTTTTTT", "TTTTNNNNNNTTTTTT", "TTTNNNNNNNNTTTTT", "TTTnnnnnnnnTTTTT",
    "TTTnnTTTTnnTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT"
]
BRICK_BLOCK_ART = [
    "OOOOOOOOOOOOOOOO", "OKKOOKKOOKKOOKKO", "OOOOOOOOOOOOOOOO", "KOOKKOOKKOOKKOOK",
    "OOOOOOOOOOOOOOOO", "OKKOOKKOOKKOOKKO", "OOOOOOOOOOOOOOOO", "KOOKKOOKKOOKKOOK",
    "OOOOOOOOOOOOOOOO", "OKKOOKKOOKKOOKKO", "OOOOOOOOOOOOOOOO", "KOOKKOOKKOOKKOOK",
    "OOOOOOOOOOOOOOOO", "OKKOOKKOOKKOOKKO", "OOOOOOOOOOOOOOOO", "oooooooooooooooo"
]
QUESTION_BLOCK_ART_FRAME1 = [
    "YYYYYYYYYYYYYYYY", "YKWYYYYYYYWKYYYY", "YKKWYYYYYWKKYYYY", "YTTKWYYYYWKTTYYY",
    "YTTTKWWWKTTTTYYY", "YTTTTKWKTTTTTYYY", "YTTTTKWYTTTTTYYY", "YTTTTKWTTTTTTYYY",
    "YTTTTKWTTTTTTYYY", "YTTTTTTTTTTTTYYY", "YTTTTKWTTTTTTYYY", "YTTTTKWTTTTTTYYY",
    "YYYYYYYYYYYYYYYY", "YKKKKKKKKKKKKKKY", "YyyyyyyyyyyyyyyY", "yyyyyyyyyyyyyyyy"
]
GROUND_BLOCK_ART = [
    "NNNNNNNNNNNNNNNN", "NnnnnnnnnnnnnnnN", "NnnnnnnnnnnnnnnN", "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN", "NNNNNNNNNNNNNNNN"
]
MUSHROOM_ART = [
    "TTTTTMMMMTTTTTTT", "TTTTMMMMMMTTTTTT", "TTTMMWWMMWWMTTTT", "TTMMWWMMWWMMTTTT",
    "TTMMMMMMMMMMTTTT", "TTTSSSSSSSSTTTTT", "TTSSKKSSKKSTTTTT", "TTSSKKSSKKSTTTTT",
    "TTTSSSSSSSSTTTTT", "TTTTSSSSSTTTTTTT", "TTTTTnnnNTTTTTTT", "TTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT"
]
FLAGPOLE_ART = [
    "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTTTTTTTTTTTTT", "TTTTGGTTTTTTTTTT",
    "TTTGGGGTTTTTTTTT", "TTGGGGGGTTTTTTTT", "TTTKGGGKTTTTTTTT", "TTTTKKKTTTTTTTTT",
    "TTTTKKKTTTTTTTTT", "TTTTKKKTTTTTTTTT", "TTTTKKKTTTTTTTTT", "TTTTKKKTTTTTTTTT",
    "TTTTKKKTTTTTTTTT", "TTTTKKKTTTTTTTTT", "TTTTKKKTTTTTTTTT", "TTTTKKKTTTTTTTTT"
]

def flip_pixel_art(pixel_art_rows):
    return ["".join(reversed(row)) for row in pixel_art_rows]

# Classes
class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation_frames = {}
        self.current_frame_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.image_scale = PIXEL_SCALE
        self.state = "idle"
        self.facing_left = False

    def load_animation_frames(self, action_name, frame_art_list_right):
        key_r = f"{action_name}_right"
        self.animation_frames[key_r] = [(create_snes_tile_indices(art, build_sprite_palette(art)), build_sprite_palette(art)) for art in frame_art_list_right]
        key_l = f"{action_name}_left"
        self.animation_frames[key_l] = [(create_snes_tile_indices(flip_pixel_art(art), build_sprite_palette(art)), build_sprite_palette(art)) for art in frame_art_list_right]

    def get_current_animation_set(self):
        direction = "left" if self.facing_left else "right"
        key = f"{self.state}_{direction}"
        return self.animation_frames.get(key, self.animation_frames.get("idle_right", []))

    def update_animation(self, dt):
        self.animation_timer += dt * FPS * self.animation_speed
        current_animation_set = self.get_current_animation_set()
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(current_animation_set)

    def draw(self, screen, camera_offset_x, camera_offset_y):
        tile_indices, palette = self.get_current_animation_set()[self.current_frame_index]
        draw_snes_tile_indexed(screen, tile_indices, palette, self.rect.x - camera_offset_x, self.rect.y - camera_offset_y, self.image_scale)

class Player(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        self.is_super_form = False
        self.set_form(small=True)
        self.on_ground = False
        self.can_jump = True
        self.score = 0
        self.lives = 3
        self.invincible_timer = 0

    def set_form(self, small=False):
        self.animation_frames = {}
        if small:
            self.is_super_form = False
            self.art_height_chars = 16
            self.player_height_tiles = 1
            self.load_animation_frames("idle", [PLAYER_SM_IDLE_R_ART])
            self.load_animation_frames("walk", [PLAYER_SM_IDLE_R_ART, PLAYER_SM_IDLE_R_ART])
            self.load_animation_frames("jump", [PLAYER_SM_IDLE_R_ART])
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, self.player_height_tiles * TILE_SIZE)

    def jump(self):
        if self.on_ground:
            self.vel.y = -PLAYER_JUMP_POWER
            self.on_ground = False
            self.can_jump = False

    def update(self, dt, platforms):
        self.acc = pg.math.Vector2(0, GRAVITY)
        keys = pg.key.get_pressed()
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACCEL
            self.facing_left = True
        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACCEL
            self.facing_left = False
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel.x += self.acc.x * dt * FPS
        self.vel.x = max(-PLAYER_MAX_SPEED_X, min(self.vel.x, PLAYER_MAX_SPEED_X))
        self.pos.x += self.vel.x * dt * FPS + 0.5 * self.acc.x * (dt * FPS) ** 2
        self.rect.x = self.pos.x
        self.collide_with_platforms_x(platforms)
        if keys[pg.K_SPACE] and self.can_jump:
            self.jump()
        if not keys[pg.K_SPACE]:
            self.can_jump = True
        self.vel.y = min(self.vel.y + self.acc.y * dt * FPS, MAX_FALL_SPEED)
        self.pos.y += self.vel.y * dt * FPS + 0.5 * self.acc.y * (dt * FPS) ** 2
        self.rect.y = self.pos.y
        self.on_ground = False
        self.collide_with_platforms_y(platforms)
        self.state = "jump" if not self.on_ground else "walk" if abs(self.vel.x) > 0.2 else "idle"
        self.update_animation(dt)
        if self.rect.top > SCREEN_HEIGHT + TILE_SIZE:
            self.die()

    def collide_with_platforms_x(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0:
                    self.rect.right = plat.rect.left
                    self.vel.x = 0
                elif self.vel.x < 0:
                    self.rect.left = plat.rect.right
                    self.vel.x = 0
                self.pos.x = self.rect.x

    def collide_with_platforms_y(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel.y = 0
                    if hasattr(plat, 'hit_from_bottom'):
                        plat.hit_from_bottom(self)
                self.pos.y = self.rect.y

    def die(self):
        self.lives -= 1
        if self.lives > 0:
            self.game.reset_level()
        else:
            self.game.game_over = True

class Block(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile, art_frames, solid=True, block_type="generic"):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", art_frames)
        self.solid = solid
        self.block_type = block_type

    def update(self, dt):
        self.update_animation(dt)

class BrickBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [BRICK_BLOCK_ART], solid=True, block_type="brick")

    def hit_from_bottom(self, player):
        if player.is_super_form:
            self.kill()

class QuestionBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [QUESTION_BLOCK_ART_FRAME1], solid=True, block_type="qblock")
        self.state = "active"
        self.animation_speed = 0.3

    def hit_from_bottom(self, player):
        if self.state == "active":
            self.state = "used"
            self.load_animation_frames("idle", [BRICK_BLOCK_ART])
            self.game.all_sprites.add(Mushroom(self.game, self.pos.x / TILE_SIZE, self.pos.y / TILE_SIZE - 1))
            self.game.items.add(self.game.all_sprites.sprites()[-1])

class GroundBlock(Block):
    def __init__(self, game, x_tile, y_tile):
        super().__init__(game, x_tile, y_tile, [GROUND_BLOCK_ART], solid=True, block_type="ground")

class Goomba(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("walk", [GOOMBA_WALK1_ART, GOOMBA_WALK1_ART])
        self.vel = pg.math.Vector2(-ENEMY_MOVE_SPEED, 0)
        self.state = "walk"

    def update(self, dt, platforms):
        if self.state == "walk":
            self.pos.x += self.vel.x * dt * FPS
            self.rect.x = self.pos.x
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.vel.x > 0:
                        self.rect.right = plat.rect.left
                        self.vel.x *= -1
                    elif self.vel.x < 0:
                        self.rect.left = plat.rect.right
                        self.vel.x *= -1
                    self.pos.x = self.rect.x
            self.update_animation(dt)

class Mushroom(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", [MUSHROOM_ART])
        self.vel = pg.math.Vector2(ENEMY_MOVE_SPEED / 2, 0)
        self.on_ground = False

    def update(self, dt, platforms):
        self.pos.x += self.vel.x * dt * FPS
        self.rect.x = self.pos.x
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0:
                    self.rect.right = plat.rect.left
                    self.vel.x *= -1
                elif self.vel.x < 0:
                    self.rect.left = plat.rect.right
                    self.vel.x *= -1
                self.pos.x = self.rect.x
        if not self.on_ground:
            self.pos.y += GRAVITY * 2 * dt * FPS
            self.rect.y = self.pos.y
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect) and self.vel.y >= 0:
                self.rect.bottom = plat.rect.top
                self.vel.y = 0
                self.on_ground = True
                self.pos.y = self.rect.y

class Flagpole(AnimatedSprite):
    def __init__(self, game, x_tile, y_tile):
        super().__init__()
        self.game = game
        self.pos = pg.math.Vector2(x_tile * TILE_SIZE, y_tile * TILE_SIZE)
        self.rect = pg.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.load_animation_frames("idle", [FLAGPOLE_ART])
        self.animation_speed = 1.0

class Camera:
    def __init__(self, width_tiles, height_tiles):
        self.camera_rect = pg.Rect(0, 0, width_tiles * TILE_SIZE, height_tiles * TILE_SIZE)
        self.offset = pg.math.Vector2(0, 0)
        self.world_width_pixels = 0

    def update(self, target_player):
        x = -target_player.rect.centerx + SCREEN_WIDTH // 2
        x = min(0, max(x, -(self.world_width_pixels - SCREEN_WIDTH)))
        self.offset = pg.math.Vector2(x, 0)
        self.camera_rect.topleft = (-x, 0)

# Level and Overworld Data
LEVEL_1_1_DATA = [
    "............................................................",
    "............................................................",
    "..................BBQB......................................",
    "............................................................",
    ".........................BBBB...............................",
    "............................................................",
    "...................E................E.......................",
    "GGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGFGGG",
    "GGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGGGGGGGGGGG...GGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
]
OVERWORLD_DATA = [
    "                    ",
    " P . . . . . . .   ",
    "   1   2   3   4   ",
    " . . . . . . . .   ",
    "   5   6   7   8   ",
    " . . . . . . . .   ",
    "   9   A   B   C   ",
    "                    "
]

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Mario-like Game Engine")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 36)
        self.game_state = "overworld"
        self.overworld_data = OVERWORLD_DATA
        self.mario_overworld_pos = None
        for r, row in enumerate(self.overworld_data):
            for c, char in enumerate(row):
                if char == 'P':
                    self.mario_overworld_pos = (c, r)
                    break
            if self.mario_overworld_pos:
                break
        self.overworld_cell_size = 48
        self.levels = {'1': LEVEL_1_1_DATA, '2': LEVEL_1_1_DATA, '3': LEVEL_1_1_DATA, '4': LEVEL_1_1_DATA,
                       '5': LEVEL_1_1_DATA, '6': LEVEL_1_1_DATA, '7': LEVEL_1_1_DATA, '8': LEVEL_1_1_DATA}
        self.game_over = False
        self.debug_mode = False
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.flagpoles = pg.sprite.Group()

    def load_level(self, level_data):
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.items.empty()
        self.flagpoles.empty()
        player_start_pos = (2, len(level_data) - 3)
        for row_idx, row in enumerate(level_data):
            for col_idx, char in enumerate(row):
                if char == 'G':
                    block = GroundBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char == 'B':
                    block = BrickBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char == 'Q':
                    block = QuestionBlock(self, col_idx, row_idx)
                    self.all_sprites.add(block)
                    self.platforms.add(block)
                elif char == 'E':
                    enemy = Goomba(self, col_idx, row_idx)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                elif char == 'F':
                    flagpole = Flagpole(self, col_idx, row_idx)
                    self.all_sprites.add(flagpole)
                    self.flagpoles.add(flagpole)
                elif char == 'P':
                    player_start_pos = (col_idx, row_idx)
        self.player = Player(self, player_start_pos[0], player_start_pos[1])
        self.all_sprites.add(self.player)
        self.camera = Camera(len(level_data[0]), len(level_data))
        self.camera.world_width_pixels = len(level_data[0]) * TILE_SIZE

    def enter_level(self, level_char):
        if level_char in self.levels:
            self.load_level(self.levels[level_char])
            self.game_state = "level"

    def complete_level(self):
        self.game_state = "overworld"

    def reset_level(self):
        self.enter_level('1')

    def draw_overworld(self):
        self.screen.fill(BACKGROUND_COLOR)
        for r, row in enumerate(self.overworld_data):
            for c, char in enumerate(row):
                x = c * self.overworld_cell_size
                y = r * self.overworld_cell_size
                if char == ' ':
                    pg.draw.rect(self.screen, (0, 0, 100), (x, y, self.overworld_cell_size, self.overworld_cell_size))
                elif char == '.':
                    pg.draw.rect(self.screen, (0, 200, 0), (x, y, self.overworld_cell_size, self.overworld_cell_size))
                elif char in '12345678':
                    pg.draw.rect(self.screen, (255, 255, 0), (x, y, self.overworld_cell_size, self.overworld_cell_size))
                    self.draw_text(char, x + self.overworld_cell_size // 2 - 10, y + self.overworld_cell_size // 2 - 10, 'K')
        mario_x = self.mario_overworld_pos[0] * self.overworld_cell_size
        mario_y = self.mario_overworld_pos[1] * self.overworld_cell_size
        pg.draw.rect(self.screen, (255, 0, 0), (mario_x, mario_y, self.overworld_cell_size, self.overworld_cell_size))

    def draw_text(self, text, x, y, color_char='W'):
        surf = self.font.render(text, True, color_map[color_char])
        self.screen.blit(surf, (x, y))

    async def main(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if event.key == pg.K_F1:
                        self.debug_mode = not self.debug_mode
                    if event.key == pg.K_r and self.game_over:
                        self.game_over = False
                        self.player.lives = 3
                        self.player.score = 0
                        self.reset_level()
                    if self.game_state == "overworld":
                        new_pos = self.mario_overworld_pos
                        if event.key == pg.K_LEFT:
                            new_pos = (self.mario_overworld_pos[0] - 1, self.mario_overworld_pos[1])
                        elif event.key == pg.K_RIGHT:
                            new_pos = (self.mario_overworld_pos[0] + 1, self.mario_overworld_pos[1])
                        elif event.key == pg.K_UP:
                            new_pos = (self.mario_overworld_pos[0], self.mario_overworld_pos[1] - 1)
                        elif event.key == pg.K_DOWN:
                            new_pos = (self.mario_overworld_pos[0], self.mario_overworld_pos[1] + 1)
                        elif event.key == pg.K_SPACE:
                            char = self.overworld_data[self.mario_overworld_pos[1]][self.mario_overworld_pos[0]]
                            if char in '12345678':
                                self.enter_level(char)
                        if 0 <= new_pos[0] < len(self.overworld_data[0]) and 0 <= new_pos[1] < len(self.overworld_data):
                            if self.overworld_data[new_pos[1]][new_pos[0]] in '.12345678':
                                self.mario_overworld_pos = new_pos

            if not self.game_over and self.game_state == "level":
                self.player.update(dt, self.platforms)
                for enemy in self.enemies:
                    enemy.update(dt, self.platforms)
                for item in self.items:
                    item.update(dt, self.platforms)
                self.camera.update(self.player)
                if self.player.invincible_timer <= 0:
                    for enemy in self.enemies:
                        if enemy.state == "walk" and self.player.rect.colliderect(enemy.rect):
                            if self.player.vel.y > 0 and self.player.rect.bottom < enemy.rect.centery + TILE_SIZE / 3:
                                enemy.state = "squished"
                                enemy.vel.x = 0
                                self.player.vel.y = -PLAYER_JUMP_POWER / 2
                                self.player.score += 100
                            else:
                                self.player.die()
                                break
                for item in self.items:
                    if self.player.rect.colliderect(item.rect):
                        item.kill()
                        self.player.score += 1000
                for flagpole in self.flagpoles:
                    if self.player.rect.colliderect(flagpole.rect):
                        self.complete_level()
                        break

            self.screen.fill(BACKGROUND_COLOR)
            if self.game_state == "overworld":
                self.draw_overworld()
            elif self.game_state == "level":
                for sprite in self.all_sprites:
                    if sprite.rect.colliderect(self.camera.camera_rect):
                        sprite.draw(self.screen, self.camera.offset.x, self.camera.offset.y)
                self.draw_text(f"SCORE: {self.player.score}", 20, 10)
                self.draw_text(f"LIVES: {self.player.lives}", SCREEN_WIDTH - 150, 10)
            if self.game_over:
                overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
                overlay.fill((50, 50, 50, 200))
                self.screen.blit(overlay, (0, 0))
                self.draw_text("Game Over! Press R to restart", SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2, 'W')
            pg.display.flip()
            await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(Game().main())
else:
    if __name__ == "__main__":
        asyncio.run(Game().main())
