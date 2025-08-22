# scenes/end_level_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets

class EndLevelScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.result = "" # "victory" or "defeat"
        self.current_level = 0
        self.options = []
        self.option_rects = []
        self.hovered_option = -1
        
    def setup(self, result, level):
        """從 GameplayScene 接收關卡結果"""
        self.result = result
        self.current_level = level
        self.hovered_option = -1
        
        # 根據結果設定選項
        if self.result == 'victory':
            self.title = "勝利"
            self.title_color = WHITE
            # 檢查是否有下一關
            if (self.current_level + 1) in LEVELS:
                self.options = ["下一關", "回到主畫面"]
            else:
                self.options = ["回到主畫面"] # 沒有下一關了
        else: # defeat
            self.title = "失敗"
            self.title_color = HOVER_COLOR
            self.options = ["重新挑戰", "回到主畫面"]
            
        # 建立選項的 Rect
        self.option_rects = []
        for i, option in enumerate(self.options):
            rect = pygame.Rect(0, 0, 400, 70)
            rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.5 + i * 90)
            self.option_rects.append(rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEMOTION:
                self.hovered_option = -1
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.hovered_option = i
                        break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.select_option(self.hovered_option)

    def select_option(self, index):
        if index == -1: return

        selected = self.options[index]
        gameplay_scene = self.manager.scenes['gameplay']

        if selected == "下一關":
            gameplay_scene.load_level(self.current_level + 1)
            self.manager.switch_to_scene('gameplay')
        elif selected == "重新挑戰":
            gameplay_scene.load_level(self.current_level)
            self.manager.switch_to_scene('gameplay')
        elif selected == "回到主畫面":
            self.manager.switch_to_scene('main_menu')
            
    def update(self):
        pass

    def draw(self, screen):
        # 顯示最後一幀的遊戲畫面作為背景
        gameplay_scene = self.manager.scenes['gameplay']
        gameplay_scene.draw(screen)

        # 畫一個半透明的遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # 黑色，180/255 的透明度
        screen.blit(overlay, (0,0))
        
        # 畫標題
        title_font = assets.get_font('title')
        title_surf = title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3))
        screen.blit(title_surf, title_rect)
        
        # 畫選項
        menu_font = assets.get_font('menu')
        for i, (option_text, rect) in enumerate(zip(self.options, self.option_rects)):
            color = HOVER_COLOR if i == self.hovered_option else WHITE
            text_surf = menu_font.render(option_text, True, color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)