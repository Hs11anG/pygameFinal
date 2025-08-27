# settings.py
import pygame

# 螢幕設定
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 800
FPS = 60

# ==== 關卡資料設定 ====
LEVELS = {
    1: {
        'protection' : '孔子的智慧',
        # --- ↓↓↓ 【【【本次修改：合併訊息】】】 ↓↓↓ ---
        'start_message': '保護好 孔子的智慧！',
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
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
        'protection' : '台南的小吃',
        # --- ↓↓↓ 【【【本次修改：合併訊息】】】 ↓↓↓ ---
        'start_message': '保護好 台南的小吃！',
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
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
        'protection' : '作者',
        # --- ↓↓↓ 【【【本次修改：合併訊息】】】 ↓↓↓ ---
        'start_message': '保護好 作者！這是最終的挑戰！',
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
        'id': 'pier_assault_2',
        'name': 'pier_assault_2',
        'background_image': 'assets/images/pier3_background.png',
        'protection_point': (650, 375),
        'player_spawn_point': (949, 616),
        'offsetx' : 20, 
        'offsety' : 20,
        'playersize': (30, 60),
        'duration': 30,
        'spawns': { 'gbird_alpha': 15, 'gbird_beta': 25, 'solarpanel_beta': 20 },
        'unlocked_weapons': [1, 2, 3],
        'level_multiplier': 1.8,
    }
}

SKILL_DATA = {
    1: {'duration': 5000, 'cooldown': 10000},
    2: {'duration': 3000, 'cooldown': 12000},
    3: {'duration': 0,    'cooldown': 45000}
}

WEAPON_DATA = {
    1: {'id': 'bsword', 'name': '竹簡劍', 'image_path': 'assets/images/bsword.png', 'size': (13, 70), 'projectile_size_multiplier': 0.9, 'damage': 30, 'cooldown': 0.6, 'projectile_class_name': 'BswordProjectile' , 'cooldown_type': 'on_fire'},
    2: {'id': 'skill1', 'name': '轉型正義', 'image_path': 'assets/images/board.png', 'size': (70, 70), 'projectile_size_multiplier': 1.2, 'damage': 50, 'cooldown': 0.5, 'projectile_class_name': 'BoardProjectile', 'cooldown_type': 'on_fire'},
    3: {'id': 'bsword_heavy', 'name': '竹簡劍-HEAVY', 'image_path': 'assets/images/bsword.png', 'size': (100, 100), 'projectile_size_multiplier': 0.9, 'damage': 100, 'cooldown': 3.0, 'projectile_class_name': 'BswordProjectile', 'cooldown_type': 'on_fire'}
}

MONSTER_DATA = {
    'gbird_alpha': { 'name': 'G-Bird Alpha', 'health': 30, 'damage': 10, 'spawn_interval': 3000, 'escape_time': 15000, 'speed': 2, 'escape_speed_multiplier': 1.5, 'image_path': 'assets/images/gbird_alpha.png', 'debuff': None, 'sizex' :50, 'sizey' :50, 'animation_frames': ['gbird_alpha_a1', 'gbird_alpha_a2', 'gbird_alpha_a3', 'gbird_alpha_a4'], 'death_frames': ['gbird_alpha_d1', 'gbird_alpha_d2']},
    'gbird_beta': { 'name': 'G-Bird Beta', 'health': 60, 'damage': 15, 'spawn_interval': 5000, 'escape_time': 20000, 'speed': 1, 'escape_speed_multiplier': 1.5, 'image_path': 'assets/images/gbird_beta.png', 'debuff': None, 'sizex' :50, 'sizey' :50, 'animation_frames': ['gbird_beta_a1', 'gbird_beta_a2', 'gbird_beta_a3', 'gbird_beta_a4'], 'death_frames': ['gbird_beta_d1', 'gbird_beta_d2']},
    'solarpanel_beta': { 'name': 'Solarpanel_beta', 'health': 100, 'damage': 25, 'spawn_interval': 5000, 'escape_time': 20000, 'speed': 1, 'escape_speed_multiplier': 1.5, 'image_path': 'assets/images/solarpanel_beta.png', 'debuff': None, 'sizex' :50, 'sizey' :50, 'animation_frames': ['solarpanel_beta_a1', 'solarpanel_beta_a2', 'solarpanel_beta_a3', 'solarpanel_beta_a4'], 'death_frames': ['solarpanel_beta_d1', 'solarpanel_beta_d2']}
}
BLACK, WHITE, GREY, HOVER_COLOR = (0,0,0), (255,255,255), (170,170,170), (255,215,0)
TITLE_FONT_SIZE, MENU_FONT_SIZE = 96, 64
UI_BG_COLOR, UI_BORDER_COLOR = (20,20,20), (180,180,180)
LEVEL_ICON_SIZE = 120

UPGRADE_DATA = {
    1: {
        'tactical_reset_skill_1': {'name': '靈光一閃', 'description': '「轉型正義」冷卻立即完成', 'category': 'tactical', 'type': 'reset_cooldown', 'skill_id': 1},
        'tactical_reset_all_skills': {'name': '文思泉湧', 'description': '所有技能冷卻立即完成', 'category': 'tactical', 'type': 'reset_cooldown', 'skill_id': 'all'},
        'tactical_add_duration_1': {'name': '正義延長', 'description': '本次「轉型正義」持續時間 +5 秒', 'category': 'tactical', 'type': 'add_duration', 'skill_id': 1, 'value': 5000},
        'tactical_bsword_damage_burst': {'name': '鋒芒畢露', 'description': '本局「竹簡劍」基礎攻擊力 x1.5', 'category': 'tactical', 'type': 'multiply', 'weapon_id': 1, 'stat': 'damage', 'value': 1.5},
        'permanent_skill1_cooldown': {'name': '熟能生巧', 'description': '「轉型正義」冷卻時間 -10%', 'category': 'permanent', 'type': 'multiply', 'stat': 'skill_cooldown', 'skill_id': 1, 'value': 0.9},
        'permanent_bsword_damage_1': {'name': '打磨竹簡', 'description': '「竹簡劍」攻擊力 +5', 'category': 'permanent', 'type': 'add', 'weapon_id': 1, 'stat': 'damage', 'value': 5},
        'permanent_board_damage_1': {'name': '正義鐵拳', 'description': '「轉型正義」攻擊力 +10', 'category': 'permanent', 'type': 'add', 'weapon_id': 2, 'stat': 'damage', 'value': 10},
    },
    2: {
        'tactical_reset_skill_2': {'name': '醍醐灌頂', 'description': '「融會貫通」冷卻立即完成', 'category': 'tactical', 'type': 'reset_cooldown', 'skill_id': 2},
        'tactical_add_duration_2': {'name': '貫通延長', 'description': '本次「融會貫通」持續時間 +5 秒', 'category': 'tactical', 'type': 'add_duration', 'skill_id': 2, 'value': 5000},
        'permanent_skill2_cooldown': {'name': '心領神會', 'description': '「融會貫通」冷卻時間 -10%', 'category': 'permanent', 'type': 'multiply', 'stat': 'skill_cooldown', 'skill_id': 2, 'value': 0.9},
        'permanent_bsword_damage_2': {'name': '精煉竹簡', 'description': '「竹簡劍」攻擊力 +10', 'category': 'permanent', 'type': 'add', 'weapon_id': 1, 'stat': 'damage', 'value': 10},
        'permanent_board_damage_2': {'name': '正義昇華', 'description': '「轉型正義」攻擊力 +20', 'category': 'permanent', 'type': 'add', 'weapon_id': 2, 'stat': 'damage', 'value': 20},
    },
    3: {
        'tactical_reset_skill_3': {'name': '天賜良機', 'description': '「搏命救援」冷卻立即完成', 'category': 'tactical', 'type': 'reset_cooldown', 'skill_id': 3},
        'permanent_rescue_speed': {'name': '老馬識途', 'description': '「搏命救援」後段速度減慢 10%', 'category': 'permanent', 'type': 'multiply', 'stat': 'rescue_skill_speed', 'value': 0.9},
    }
}