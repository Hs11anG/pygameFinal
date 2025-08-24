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
        # 【修改】移除 walkable_mask_image，遊戲場景不再需要
        
        # 【修改】舊的 spawn_point 現在是保護目標的位置
        'protection_point': (280, 350), 
        # 【修改】玩家出生點改為舊武器的位置
        'player_spawn_point': (380, 400),
        
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 30,
        'spawns': { 'gbird_alpha': 30, 'gbird_beta': 10 },
        'victory_monster_limit': 20,
        # 【修改】移除 weapon_spawns，武器改由玩家持有
        'unlocked_weapons': [1, 2] # <--- 【新增】定義本關可用的武器 ID
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
        'victory_monster_limit': 20,
        'unlocked_weapons': [1, 2, 3] # 第二關解鎖所有武器
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
        'victory_monster_limit': 20,
        'unlocked_weapons': [1, 2, 3] # 第二關解鎖所有武器
    }
    # (第三關可以暫時移除或照此格式修改)
}

WEAPON_DATA = {
    1: {
        'id': 'bsword',
        'name': '竹簡劍',
        'image_path': 'assets/images/bsword.png',
        'size': (13, 70),
        'projectile_size_multiplier': 0.9,
        'damage': 30,
        'cooldown': 0.1,
        # ↓↓↓ 【【【核心修正：將 projectile_class 改為 projectile_class_name】】】 ↓↓↓
        'projectile_class_name': 'BswordProjectile' ,
        'cooldown_type': 'on_fire' # 射出即冷卻
    },
    2: {
        'id': 'board', 
        'name': '轉型正義',
        'image_path': 'assets/images/board.png',
        'size': (70, 70),
        'projectile_size_multiplier': 0.9,
        'damage': 50,
        'cooldown': 0.1,
        'projectile_class_name': 'BoardProjectile',
        'cooldown_type': 'on_fire' # 射出即冷卻
    },
    3: {
        'id': 'bsword_heavy', # 修正了重複的ID
        'name': '竹簡劍-HEAVY',
        'image_path': 'assets/images/bsword.png',
        'size': (100, 100),
        'projectile_size_multiplier': 0.9,
        'damage': 100,
        'cooldown': 3.0,
        'projectile_class_name': 'BswordProjectile',
        'cooldown_type': 'on_fire' # 射出即冷卻
    }
}

# (MONSTER_DATA, 顏色, 字體設定不變)
MONSTER_DATA = {
    'gbird_alpha': { 'name': 'G-Bird Alpha', 'health': 30, 'spawn_interval': 3000, 'escape_time': 15000, 'speed': 2, 'escape_speed_multiplier': 1.5, 'image_path': 'assets/images/gbird_alpha.png', 'debuff': None, 'sizex' :50, 'sizey' :50 },
    'gbird_beta': { 'name': 'G-Bird Beta', 'health': 60, 'spawn_interval': 5000, 'escape_time': 20000, 'speed': 1, 'escape_speed_multiplier': 1.5, 'image_path': 'assets/images/gbird_beta.png', 'debuff': None, 'sizex' :50, 'sizey' :50 },
    'solarpanel_beta': { 'name': 'Solarpanel_beta', 'health': 100, 'spawn_interval': 5000, 'escape_time': 20000, 'speed': 1, 'escape_speed_multiplier': 1.5, 'image_path': 'assets/images/solarpanel_beta.png', 'debuff': None, 'sizex' :50, 'sizey' :50 }
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