# scenes/level_select_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets
from player import Player
from level_icon import LevelIcon
from save_manager import save_manager

class LevelSelectScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.background = assets.get_image('level_select_bg')
        self.walkable_mask = pygame.mask.from_surface(assets.get_image('level_select_mask'))
        
        # 這個 player 只是用於在地圖上移動，不是遊戲內的玩家
        self.map_player = Player(start_pos=(156, 668), level_number=1) 
        self.player_group = pygame.sprite.Group(self.map_player)
        self.level_icons = pygame.sprite.Group()

        self.can_interact = True

    def setup(self):
        self.level_icons.empty()
        positions = {1: (630, 435), 2: (790, 360), 3: (930, 325)}
        for level_num, pos in positions.items():
            if level_num in LEVELS:
                is_unlocked = save_manager.is_level_unlocked(level_num)
                icon = LevelIcon(pos, level_num, is_unlocked)
                self.level_icons.add(icon)

    def handle_events(self, events):
        keys = pygame.key.get_pressed()
        self.map_player.move(keys)

        if keys[pygame.K_e]:
            if self.can_interact:
                for icon in self.level_icons:
                    if icon.interaction_text == "按E進入關卡":
                        gameplay_scene = self.manager.scenes['gameplay']
                        gameplay_scene.load_level(icon.level_number)
                        self.manager.switch_to_scene('gameplay')
                        break
                self.can_interact = False
        else:
            self.can_interact = True
            
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')

    # --- ↓↓↓ 【【【補上 update 方法】】】 ↓↓↓ ---
    def update(self):
        """更新關卡圖示的互動狀態"""
        self.level_icons.update(self.map_player)
    # --- ↑↑↑ 【【【補上 update 方法】】】 ↑↑↑ ---

    def draw(self, screen):
        screen.blit(self.background, (0,0))
        self.level_icons.draw(screen)
        for icon in self.level_icons:
            icon.draw_ui(screen)
        self.player_group.draw(screen)