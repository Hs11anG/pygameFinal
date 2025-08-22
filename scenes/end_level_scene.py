# scenes/end_level_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets

class EndLevelScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.result = ""
        self.current_level = 0
        self.options = []
        self.option_rects = []
        self.hovered_option = -1
        
    def setup(self, result, level):
        self.result = result
        self.current_level = level
        self.hovered_option = -1
        
        if self.result == 'victory':
            self.title = "勝利"
            self.title_color = WHITE
            if (self.current_level + 1) in LEVELS:
                self.options = ["下一關", "回到主畫面"]
            else:
                self.options = ["回到主畫面"]
        else: # defeat
            self.title = "失敗"
            self.title_color = HOVER_COLOR
            self.options = ["重新挑戰", "回到主畫面"]
            
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
                        self.hovered_option = i; break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered_option != -1:
                    self.select_option(self.hovered_option)

    def select_option(self, index):
        if index == -1: return

        selected = self.options[index]
        
        if selected == "下一關":
            level_select_scene = self.manager.scenes['level_select']
            
            # ↓↓↓ 【【【這就是修正的地方】】】 ↓↓↓
            # 將 setup_level_icons() 改為 setup()
            level_select_scene.setup() 
            
            self.manager.switch_to_scene('level_select')
            
        elif selected == "重新挑戰":
            gameplay_scene = self.manager.scenes['gameplay']
            gameplay_scene.load_level(self.current_level)
            self.manager.switch_to_scene('gameplay')

        elif selected == "回到主畫面":
            self.manager.switch_to_scene('main_menu')
            
    def update(self):
        pass

    def draw(self, screen):
        gameplay_scene = self.manager.scenes['gameplay']
        gameplay_scene.draw(screen)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        
        title_font = assets.get_font('title')
        title_surf = title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3))
        screen.blit(title_surf, title_rect)
        
        menu_font = assets.get_font('menu')
        for i, (option_text, rect) in enumerate(zip(self.options, self.option_rects)):
            color = HOVER_COLOR if i == self.hovered_option else WHITE
            text_surf = menu_font.render(option_text, True, color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)