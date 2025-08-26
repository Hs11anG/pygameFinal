# scenes/end_level_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets

class EndLevelScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.result = 'victory'
        self.hovered_button_text = ''
        self.background_image = None
        self.kills_this_level = 0
        self.current_level = 0
        self.buttons = {} # 使用字典來儲存按鈕

    def setup(self, result, level, kills, background_image=None):
        self.result = result
        self.current_level = level
        self.kills_this_level = kills
        self.hovered_button_text = ''
        self.background_image = background_image
        self.create_buttons() # 每次 setup 都重新建立按鈕

    # --- ↓↓↓ 【【【本次修改：重構按鈕建立邏輯】】】 ↓↓↓ ---
    def create_buttons(self):
        self.buttons = {} # 清空舊按鈕
        button_y_start = SCREEN_HEIGHT * 0.6
        button_height = 70
        button_gap = 90

        if self.result == 'victory':
            # 勝利時的按鈕
            if (self.current_level + 1) in LEVELS:
                self.buttons['前往下一關'] = pygame.Rect(SCREEN_WIDTH/2 - 150, button_y_start, 300, button_height)
            self.buttons['返回主選單'] = pygame.Rect(SCREEN_WIDTH/2 - 150, button_y_start + button_gap, 300, button_height)
        else: # defeat
            # 失敗時的按鈕
            self.buttons['重來一次'] = pygame.Rect(SCREEN_WIDTH/2 - 150, button_y_start, 300, button_height)
            self.buttons['返回關卡選擇'] = pygame.Rect(SCREEN_WIDTH/2 - 150, button_y_start + button_gap, 300, button_height)
    # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            
            if event.type == pygame.MOUSEMOTION:
                self.hovered_button_text = ''
                for text, rect in self.buttons.items():
                    if rect.collidepoint(event.pos):
                        self.hovered_button_text = text
                        break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered_button_text:
                    self.on_button_click(self.hovered_button_text)
    
    # --- ↓↓↓ 【【【本次新增：處理按鈕點擊事件的函式】】】 ↓↓↓ ---
    def on_button_click(self, button_text):
        level_select_scene = self.manager.scenes['level_select']
        gameplay_scene = self.manager.scenes['gameplay']

        if button_text == '前往下一關':
            # 前往下一關時，不重置玩家在地圖上的位置
            level_select_scene.setup(reset_player_pos=False)
            self.manager.switch_to_scene('level_select')

        elif button_text == '返回主選單':
            self.manager.switch_to_scene('main_menu')

        elif button_text == '重來一次':
            gameplay_scene.load_level(self.current_level)
            self.manager.switch_to_scene('gameplay')

        elif button_text == '返回關卡選擇':
            # 失敗後返回關卡選擇，不重置玩家位置
            level_select_scene.setup(reset_player_pos=False)
            self.manager.switch_to_scene('level_select')
    # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

    def update(self):
        """此場景為靜態，不需更新"""
        pass

    def draw(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(UI_BG_COLOR)

        title_font = assets.get_font('title')
        menu_font = assets.get_font('menu')
        ui_font = assets.get_font('ui')
        
        result_text = "通關成功" if self.result == 'victory' else "挑戰失敗"
        result_color = HOVER_COLOR if self.result == 'victory' else (255, 80, 80)
        result_surf = title_font.render(result_text, True, result_color)
        result_rect = result_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.3))
        screen.blit(result_surf, result_rect)

        kills_text = f"本關擊殺: {self.kills_this_level}"
        kills_surf = ui_font.render(kills_text, True, WHITE)
        kills_rect = kills_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.45))
        screen.blit(kills_surf, kills_rect)

        # --- ↓↓↓ 【【【本次修改：繪製所有按鈕】】】 ↓↓↓ ---
        for text, rect in self.buttons.items():
            color = HOVER_COLOR if self.hovered_button_text == text else WHITE
            text_surf = menu_font.render(text, True, color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---