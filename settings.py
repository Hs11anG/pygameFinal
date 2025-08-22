# settings.py
import pygame

# 螢幕設定
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 800
FPS = 60

# ==== 關卡資料設定 ====
LEVELS = {
    1: {
        'id': 'pier_assault',
        'name': 'pier_assault',
        'background_image': 'assets/images/pier_background.png',
        'walkable_mask_image': 'assets/images/pier_walkable_mask.png',
        'spawn_point': (280, 350),
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 5,
        'spawns': {
            'gbird_alpha': 5,
            'gbird_beta': 10
        },
        'victory_monster_limit': 20,
        
        # ↓↓↓ 【【【新增武器生成設定】】】 ↓↓↓
        'weapon_spawns': [
            # 格式是 (武器類型ID, (x, y)座標)
            (1, (380, 400)) 
            # (1, (380, 400)) ,
            # (2, (610, 550)) ,
            # (3, (490, 475)) 
        ]
    },
    2: {
        'id': 'pier_assault_2',
        'name': 'pier_assault_2',
        'background_image': 'assets/images/pier2_background.png',
        'walkable_mask_image': 'assets/images/pier2_walkable_mask.png',
        'spawn_point': (650, 375),
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 30,
        'spawns': {
            'gbird_alpha': 30,
            'gbird_beta': 10,
            'solarpanel_beta': 10
        },
        'victory_monster_limit': 20,
        
        # ↓↓↓ 【【【新增武器生成設定】】】 ↓↓↓
        'weapon_spawns': [
            # 格式是 (武器類型ID, (x, y)座標)
            (1, (1100, 375)) ,
            (2, (950, 375)) ,
            (3, (850, 375)) 
        ]
    },
    3: {
    'id': 'pier_assault_3',
    'name': 'pier_assault_3',
    'background_image': 'assets/images/pier3_background.png',
    'walkable_mask_image': 'assets/images/pier3_walkable_mask.png',
    'spawn_point': (650, 375),
    'offsetx' : 20, 
    'offsety' : 20,
    'playersize': (30, 60),
    'duration': 30,
    'spawns': {
        'gbird_alpha': 30,
        'gbird_beta': 10,
        'solarpanel_beta': 10
    },
    'victory_monster_limit': 20,
    
    # ↓↓↓ 【【【新增武器生成設定】】】 ↓↓↓
    'weapon_spawns': [
        # 格式是 (武器類型ID, (x, y)座標)
        (1, (1100, 375)) ,
        (2, (950, 375)) ,
        (3, (850, 375)) 
    ]
}
    
}


WEAPON_DATA = {
    1: {
        'id': 'bsword',
        'name': '竹簡劍-fast',
        'image_path': 'assets/images/bsword.png',
        'size': (50, 50),       # 武器在地面上或頭頂上的圖標大小
        'projectile_size_multiplier': 0.9, # 飛出去的武器是圖標的 0.5 倍大
        'damage': 30,
        'cooldown': 0.1 # 0.5 秒冷卻
    },
    2: {
        'id': 'board',
        'name': '轉型正義',
        'image_path': 'assets/images/board.png',
        'size': (70, 70),       # 武器在地面上或頭頂上的圖標大小
        'projectile_size_multiplier': 0.9, # 飛出去的武器是圖標的 0.5 倍大
        'damage': 50,
        'cooldown': 0.1 # 0.5 秒冷卻
    } ,
    3: {
        'id': 'bsword',
        'name': '竹簡劍-HEAVY',
        'image_path': 'assets/images/bsword.png',
        'size': (100, 100),       # 武器在地面上或頭頂上的圖標大小
        'projectile_size_multiplier': 0.9, # 飛出去的武器是圖標的 0.5 倍大
        'damage': 100,
        'cooldown': 20 # 0.5 秒冷卻
    }
    # 未來可以新增 2: { ... }
}

# ==== 怪物資料設定 ====
MONSTER_DATA = {
    'gbird_alpha': {
        'name': 'G-Bird Alpha',
        'health': 30,
        'spawn_interval': 3000,
        'escape_time': 15000,
        'speed': 2,
        'escape_speed_multiplier': 1.5,
        'image_path': 'assets/images/gbird_alpha.png',
        'debuff': None,
        'sizex' :50,
        'sizey' :50
    },
    'gbird_beta': {
        'name': 'G-Bird Beta',
        'health': 60,
        'spawn_interval': 5000,
        'escape_time': 20000,
        'speed': 1,
        'escape_speed_multiplier': 1.5,
        'image_path': 'assets/images/gbird_beta.png',
        'debuff': None,
        'sizex' :50,
        'sizey' :50
    },
    'solarpanel_beta': {
        'name': 'Solarpanel_beta',
        'health': 100,
        'spawn_interval': 5000,
        'escape_time': 20000,
        'speed': 1,
        'escape_speed_multiplier': 1.5,
        'image_path': 'assets/images/solarpanel_beta.png',
        'debuff': None,
        'sizex' :50,
        'sizey' :50
    }
}

# 顏色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
HOVER_COLOR = (255, 215, 0)
Fubon = (0, 61, 122)

# 字體設定
TITLE_FONT_SIZE = 96
MENU_FONT_SIZE = 64

UI_BG_COLOR = (20, 20, 20)      # 深灰色作為背景
UI_BORDER_COLOR = (180, 180, 180) # 亮灰色作為邊框