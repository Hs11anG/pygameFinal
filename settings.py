# settings.py
import pygame
# from projectile import BswordProjectile, BoardProjectile

# 螢幕設定
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 800
FPS = 60

# ==== 關卡資料設定 (重構後) ====
LEVELS = {
    1: {
        'id': 'pier_assault',
        'name': 'pier_assault',
        'background_image': 'assets/images/pier_background.png',
        'protection_point': (280, 350), 
        'player_spawn_point': (380, 400),
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 30,
        'spawns': { 'gbird_alpha': 30, 'gbird_beta': 10 },
        'unlocked_weapons': [1, 2],
        'level_multiplier': 1.0,
    },
    2: {
        'id': 'pier_assault_2',
        'name': 'pier_assault_2',
        'background_image': 'assets/images/pier2_background.png',
        'protection_point': (650, 375),
        'player_spawn_point': (850, 375),
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 30,
        'spawns': { 'gbird_alpha': 30, 'gbird_beta': 10, 'solarpanel_beta': 10 },
        'unlocked_weapons': [1, 2, 3],
        'level_multiplier': 1.2,
    },
    3: {
        'id': 'pier_assault_2',
        'name': 'pier_assault_2',
        'background_image': 'assets/images/pier2_background.png',
        'protection_point': (650, 375),
        'player_spawn_point': (850, 375),
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 30,
        'spawns': { 'gbird_alpha': 30, 'gbird_beta': 10, 'solarpanel_beta': 10 },
        'unlocked_weapons': [1, 2, 3],
        'level_multiplier': 1.5,
    }
}

WEAPON_DATA = {
    1: {
        'id': 'bsword',
        'name': '竹簡劍',
        'image_path': 'assets/images/bsword.png',
        'size': (13, 70),
        'projectile_size_multiplier': 0.9,
        'damage': 30,
        'cooldown': 0.8,
        'projectile_class_name': 'BswordProjectile' ,
        'cooldown_type': 'on_fire'
    },
    2: {
        # --- ↓↓↓ 【【【本次修改：id 改為新的圖示名稱】】】 ↓↓↓ ---
        'id': 'skill1', 
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
        'name': '轉型正義',
        'image_path': 'assets/images/board.png',
        'size': (70, 70),
        'projectile_size_multiplier': 1.2,
        'damage': 50,
        'cooldown': 0.9,
        'projectile_class_name': 'BoardProjectile',
        'cooldown_type': 'on_fire'
    },
    3: {
        'id': 'bsword_heavy',
        'name': '竹簡劍-HEAVY',
        'image_path': 'assets/images/bsword.png',
        'size': (100, 100),
        'projectile_size_multiplier': 0.9,
        'damage': 100,
        'cooldown': 3.0,
        'projectile_class_name': 'BswordProjectile',
        'cooldown_type': 'on_fire'
    }
}

MONSTER_DATA = {
    'gbird_alpha': { 
        'name': 'G-Bird Alpha', 
        'health': 30, 
        'damage': 10,
        'spawn_interval': 3000, 
        'escape_time': 15000, 
        'speed': 2, 
        'escape_speed_multiplier': 1.5, 
        'image_path': 'assets/images/gbird_alpha.png', 
        'debuff': None, 
        'sizex' :50, 
        'sizey' :50,
        'animation_frames': ['gbird_alpha_a1', 'gbird_alpha_a2', 'gbird_alpha_a3', 'gbird_alpha_a4'],
        'death_frames': ['gbird_alpha_d1', 'gbird_alpha_d2']
    },
    'gbird_beta': { 
        'name': 'G-Bird Beta', 
        'health': 60, 
        'damage': 15,
        'spawn_interval': 5000, 
        'escape_time': 20000, 
        'speed': 1, 
        'escape_speed_multiplier': 1.5, 
        'image_path': 'assets/images/gbird_beta.png', 
        'debuff': None, 
        'sizex' :50, 
        'sizey' :50,
        'animation_frames': ['gbird_beta_a1', 'gbird_beta_a2', 'gbird_beta_a3', 'gbird_beta_a4'],
        'death_frames': ['gbird_beta_d1', 'gbird_beta_d2']
    },
    'solarpanel_beta': { 
        'name': 'Solarpanel_beta', 
        'health': 100, 
        'damage': 25,
        'spawn_interval': 5000, 
        'escape_time': 20000, 
        'speed': 1, 
        'escape_speed_multiplier': 1.5, 
        'image_path': 'assets/images/solarpanel_beta.png', 
        'debuff': None, 
        'sizex' :50, 
        'sizey' :50,
        'animation_frames': ['solarpanel_beta_a1', 'solarpanel_beta_a2', 'solarpanel_beta_a3', 'solarpanel_beta_a4'],
        'death_frames': ['solarpanel_beta_d1', 'solarpanel_beta_d2']
    }
}
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
HOVER_COLOR = (255, 215, 0)
Fubon = (0, 61, 122)
TITLE_FONT_SIZE = 96
MENU_FONT_SIZE = 64
UI_BG_COLOR = (20, 20, 20)
UI_BORDER_COLOR = (180, 180, 180)

UPGRADE_DATA = {
    'skill_duration_up': {'name': '路牌猛擊', 'description': '技能持續時間 +2 秒', 'type': 'add', 'stat': 'skill_1_duration', 'value': 2000},
    'skill_cooldown_down': {'name': '精神時光', 'description': '技能冷卻時間 -10%', 'type': 'multiply', 'stat': 'skill_1_cooldown', 'value': 0.9},
    'player_speed_up': {'name': '身輕如燕', 'description': '移動速度 +15%', 'type': 'multiply', 'stat': 'speed', 'value': 1.15},
    'bsword_damage_up': {'name': '打磨竹簡', 'description': '竹簡劍傷害 +5', 'type': 'add', 'weapon_id': 1, 'stat': 'damage', 'value': 5},
    'board_damage_up': {'name': '正義鐵拳', 'description': '路牌傷害 +10', 'type': 'add', 'weapon_id': 2, 'stat': 'damage', 'value': 10},
    'bsword_heavy_damage_up': {'name': '竹簡奧義', 'description': '重型竹簡劍傷害 +30', 'type': 'add', 'weapon_id': 3, 'stat': 'damage', 'value': 30}
}