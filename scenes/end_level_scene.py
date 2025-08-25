# scenes/end_level_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets

class EndLevelScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.result = 'victory' # 'victory' or 'defeat'
        self.next_level = 0
        self.hovered_option = ''

    def setup(self, result, level):
        self.result = result
        self.next_level = level + 1
        self.hovered_option = ''

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            
            if event.type == pygame.MOUSEMOTION:
                self.hovered_option = ''
                if self.get_next_level_rect().collidepoint(event.pos) and self.result == 'victory':
                    self.hovered_option = 'next'
                elif self.get_menu_rect().collidepoint(event.pos):
                    self.hovered_option = 'menu'

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered_option == 'next':
                    level_select_scene = self.manager.scenes['level_select']
                    level_select_scene.setup()
                    self.manager.switch_to_scene('level_select')
                elif self.hovered_option == 'menu':
                    self.manager.switch_to_scene('main_menu')
    
    # --- ↓↓↓ 【【【補上 update 方法】】】 ↓↓↓ ---
    def update(self):
        """此場景為靜態，不需更新"""
        pass
    # --- ↑↑↑ 【【【補上 update 方法】】】 ↓↓↓ ---

    def get_next_level_rect(self):
        return pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT * 0.6, 300, 70)

    def get_menu_rect(self):
        return pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT * 0.6 + 90, 300, 70)

    def draw(self, screen):
        screen.fill(UI_BG_COLOR)
        title_font = assets.get_font('title')
        menu_font = assets.get_font('menu')
        
        # 顯示結果
        result_text = "通關成功" if self.result == 'victory' else "挑戰失敗"
        result_color = HOVER_COLOR if self.result == 'victory' else (255, 80, 80)
        result_surf = title_font.render(result_text, True, result_color)
        result_rect = result_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.3))
        screen.blit(result_surf, result_rect)

        # 顯示選項
        if self.result == 'victory':
            next_color = WHITE if self.hovered_option != 'next' else HOVER_COLOR
            next_surf = menu_font.render("前往下一關", True, next_color)
            screen.blit(next_surf, next_surf.get_rect(center=self.get_next_level_rect().center))

        menu_color = WHITE if self.hovered_option != 'menu' else HOVER_COLOR
        menu_surf = menu_font.render("返回主選單", True, menu_color)
        screen.blit(menu_surf, menu_surf.get_rect(center=self.get_menu_rect().center))