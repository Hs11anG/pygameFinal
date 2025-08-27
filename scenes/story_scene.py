# scenes/story_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets

class StoryScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.story_lines = GAME_STORY
        self.current_line_index = 0
        self.last_line_time = 0
        self.line_duration = 2000  # 每行顯示 3.5 秒
        self.fade_duration = 400   # 0.5 秒淡入淡出
        self.font = assets.get_font('des')
        self.title_font = assets.get_font('menu')
        
    def setup(self):
        """當切換到此場景時，重置所有狀態"""
        self.current_line_index = 0
        self.last_line_time = pygame.time.get_ticks()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return False
                exit()
            # 按下空白鍵可以跳過當前行或結束故事
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.advance_story()
        return True
    def update(self):
        now = pygame.time.get_ticks()
        # 時間到了自動播放下一行
        if now - self.last_line_time > self.line_duration:
            self.advance_story()

    def advance_story(self):
        self.current_line_index += 1
        self.last_line_time = pygame.time.get_ticks()
        # 如果故事已經結束，就切換到關卡選擇場景
        if self.current_line_index >= len(self.story_lines):
            level_select_scene = self.manager.scenes['level_select']
            level_select_scene.setup(reset_player_pos=True)
            self.manager.switch_to_scene('level_select')

    def draw(self, screen):
        screen.fill(BLACK) # 背景為黑色
        
        if self.current_line_index >= len(self.story_lines):
            return

        line_text = self.story_lines[self.current_line_index]
        
        # 根據文字內容選擇不同字體
        font_to_use = self.title_font if "淨 化 錄" in line_text else self.font
        text_surf = font_to_use.render(line_text, True, WHITE)

        # 計算淡入淡出效果的透明度
        now = pygame.time.get_ticks()
        elapsed = now - self.last_line_time
        alpha = 255
        
        if elapsed < self.fade_duration: # 淡入
            alpha = int(255 * (elapsed / self.fade_duration))
        elif elapsed > self.line_duration - self.fade_duration: # 淡出
            alpha = int(255 * ((self.line_duration - elapsed) / self.fade_duration))
        
        alpha = max(0, min(255, alpha)) # 確保 alpha 值在 0-255 之間
        text_surf.set_alpha(alpha)
        
        # 將文字置中繪製
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(text_surf, text_rect)