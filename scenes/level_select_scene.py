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
        
        # --- ↓↓↓ 【【【本次修改：不再自己創建 Player】】】 ↓↓↓ ---
        self.player = None
        self.player_group = pygame.sprite.Group() # 先建立一個空的 Group
        self.level_icons = pygame.sprite.Group()
        self.last_map_position = (156, 668) # 儲存玩家在地圖上的最後位置
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

        self.can_interact = True

    def setup(self, reset_player_pos=False):
        # --- ↓↓↓ 【【【本次修改：從 Manager 取得唯一的 Player 物件】】】 ↓↓↓ ---
        self.player = self.manager.get_player()
        # Fallback: 如果因為某些流程錯誤導致沒有 player，就建立一個新的
        if not self.player:
            self.manager.start_new_run()
            self.player = self.manager.get_player()
        
        self.player.can_move = True # 在這個場景，玩家永遠是可以移動的
        self.player_group.empty()   # 清空 group
        self.player_group.add(self.player) # 將唯一的 player 加入 group
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
        
        self.level_icons.empty()
        positions = {1: (630, 435), 2: (790, 370), 3: (930, 325)}
        for level_num, pos in positions.items():
            if level_num in LEVELS:
                is_unlocked = save_manager.is_level_unlocked(level_num)
                icon = LevelIcon(pos, level_num, is_unlocked)
                self.level_icons.add(icon)
        
        if reset_player_pos:
            self.player.rect.midbottom = (156, 668)
        else:
            # 返回時，將 player 的位置還原到離開地圖前的最後位置
            self.player.rect.midbottom = self.last_map_position


    def handle_events(self, events):
        keys = pygame.key.get_pressed()
        
        # --- ↓↓↓ 【【【本次修改：對唯一的 Player 進行操作】】】 ↓↓↓ ---
        if self.player:
            self.player.move(keys, self.walkable_mask)

        if keys[pygame.K_e]:
            if self.can_interact and self.player:
                for icon in self.level_icons:
                    if icon.interaction_text == "按E進入關卡":
                        # 離開前，記錄下當前在地圖上的位置
                        self.last_map_position = self.player.rect.midbottom
                        
                        gameplay_scene = self.manager.scenes['gameplay']
                        # 直接載入關卡，不再需要傳遞 player，因為 manager 已經知道是誰
                        gameplay_scene.load_level(icon.level_number)
                        self.manager.switch_to_scene('gameplay')
                        break
                self.can_interact = False
        else:
            self.can_interact = True
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
            
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')

    def update(self):
        # --- ↓↓↓ 【【【本次修改：對唯一的 Player 進行操作】】】 ↓↓↓ ---
        if self.player:
            self.level_icons.update(self.player)
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---


    def draw(self, screen):
        screen.blit(self.background, (0,0))
        self.level_icons.draw(screen)
        for icon in self.level_icons:
            icon.draw_ui(screen)
        self.player_group.draw(screen)