# scenes/save_slot_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets
from save_manager import save_manager, MAX_SAVES

class SaveSlotScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.mode = 'load' # 'load' or 'delete'
        self.saves = []
        self.selected_slot = -1
        self.hovered_slot = -1
        self.hovered_button = None # 'confirm' or 'cancel'
        
        # 刪除確認的狀態
        self.confirm_delete_prompt = False

    def setup(self, mode):
        self.mode = mode
        self.saves = save_manager.get_all_saves()
        self.selected_slot = -1
        self.hovered_slot = -1
        self.hovered_button = None
        self.confirm_delete_prompt = False

    def handle_events(self, events):
        # 處理刪除確認提示
        if self.confirm_delete_prompt:
            self.handle_delete_prompt_events(events)
            return

        # 正常模式下的事件處理
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')
                
            if event.type == pygame.MOUSEMOTION:
                self.hovered_slot = -1
                self.hovered_button = None
                for i, rect in self.get_slot_rects():
                    if rect.collidepoint(event.pos): self.hovered_slot = i; break
                for name, rect in self.get_button_rects().items():
                    if rect.collidepoint(event.pos): self.hovered_button = name; break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered_slot != -1: self.selected_slot = self.hovered_slot
                if self.hovered_button == 'confirm': self.on_confirm()
                if self.hovered_button == 'cancel': self.manager.switch_to_scene('main_menu')

    def handle_delete_prompt_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.hovered_button = None
                for name, rect in self.get_prompt_button_rects().items():
                    if rect.collidepoint(event.pos): self.hovered_button = name; break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered_button == 'yes_delete':
                    save_manager.delete_save(self.saves[self.selected_slot]['filepath'])
                    save_manager.create_new_save()
                    level_select_scene = self.manager.scenes['level_select']
                    level_select_scene.setup()
                    self.manager.switch_to_scene('level_select')
                if self.hovered_button == 'no_cancel':
                    self.confirm_delete_prompt = False

    def on_confirm(self):
        if self.selected_slot == -1: return
        
        if self.mode == 'load':
            save_manager.load_save(self.saves[self.selected_slot]['filepath'])
            level_select_scene = self.manager.scenes['level_select']
            level_select_scene.setup() # 每次進入時都重新整理
            self.manager.switch_to_scene('level_select')
        elif self.mode == 'delete':
            self.confirm_delete_prompt = True

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(Fubon) # 背景色
        title_font = assets.get_font('title')
        font = assets.get_font('ui')

        # 畫標題
        title_text = "讀取存檔" if self.mode == 'load' else "選擇要覆蓋的存檔"
        title_surf = title_font.render(title_text, True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(centerx=SCREEN_WIDTH/2, y=50))

        # 畫存檔槽
        for i, rect in self.get_slot_rects():
            save = self.saves[i]
            # 根據狀態決定顏色
            color = HOVER_COLOR if i == self.hovered_slot else WHITE
            if i == self.selected_slot: color = HOVER_COLOR
            
            # 顯示存檔資訊
            line1 = f"{i+1}. {save['display_name']}"
            line2 = f"進度: Level {save['unlocked_level']}   金幣: {save['gold']}"
            line1_surf = font.render(line1, True, color)
            line2_surf = font.render(line2, True, GREY)
            screen.blit(line1_surf, rect.topleft)
            screen.blit(line2_surf, (rect.left, rect.top + 40))

        # 畫確認/取消按鈕
        if self.selected_slot != -1:
            for name, rect in self.get_button_rects().items():
                color = HOVER_COLOR if name == self.hovered_button else WHITE
                text_surf = font.render(name.capitalize(), True, color)
                screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        # 畫刪除確認提示
        if self.confirm_delete_prompt:
            self.draw_delete_prompt(screen)

    def draw_delete_prompt(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        font = assets.get_font('menu')
        prompt_text = "刪除後無法復原，確定嗎?"
        text_surf = font.render(prompt_text, True, HOVER_COLOR)
        screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
        
        # 畫是/否按鈕
        ui_font = assets.get_font('ui')
        for name, rect in self.get_prompt_button_rects().items():
            color = HOVER_COLOR if name == self.hovered_button else WHITE
            text = "確定刪除" if name == 'yes_delete' else "取消"
            btn_surf = ui_font.render(text, True, color)
            screen.blit(btn_surf, btn_surf.get_rect(center=rect.center))

    # --- Helper methods for rects ---
    def get_slot_rects(self):
        rects = []
        for i in range(len(self.saves)):
            rects.append((i, pygame.Rect(SCREEN_WIDTH/2 - 300, 200 + i * 100, 600, 80)))
        return rects

    def get_button_rects(self):
        return {
            'confirm': pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT - 150, 100, 50),
            'cancel': pygame.Rect(SCREEN_WIDTH/2 + 50, SCREEN_HEIGHT - 150, 100, 50)
        }

    def get_prompt_button_rects(self):
        return {
            'yes_delete': pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 + 50, 150, 50),
            'no_cancel': pygame.Rect(SCREEN_WIDTH/2 + 50, SCREEN_HEIGHT/2 + 50, 100, 50)
        }