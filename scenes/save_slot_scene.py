# scenes/save_slot_scene.py
import pygame
from datetime import datetime
from settings import *
from scene_manager import Scene
from asset_manager import assets
from save_manager import save_manager

class SaveSlotScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.mode = 'load'
        self.save_files = []
        self.hovered_option = -1
        
        self.show_delete_prompt = False
        self.prompt_selection = '否'
        self.prompt_rects = {}

    def setup(self, mode):
        self.mode = mode
        self.save_files = save_manager.get_all_saves()
        self.hovered_option = -1
        self.show_delete_prompt = False

    def handle_events(self, events):
        if self.show_delete_prompt:
            self.handle_delete_prompt_events(events)
            return

        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')
            
            if event.type == pygame.MOUSEMOTION:
                self.hovered_option = -1
                for i, file in enumerate(self.save_files):
                    rect = self.get_slot_rect(i)
                    if rect.collidepoint(event.pos):
                        self.hovered_option = i
                        break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered_option != -1:
                self.select_slot(self.hovered_option)

    def select_slot(self, index):
        selected_file = self.save_files[index]
        
        if self.mode == 'load':
            save_data = save_manager.load_save(selected_file['path'])
            if save_data:
                self.manager.start_new_run()
                player = self.manager.get_player()
                player_stats = save_data.get('player_stats')
                if player_stats:
                    player.from_dict(player_stats)
                
                level_select_scene = self.manager.scenes['level_select']
                level_select_scene.setup(reset_player_pos=True)
                self.manager.switch_to_scene('level_select')

        elif self.mode == 'delete':
            self.show_delete_prompt = True
            self.prompt_selection = '否'

    def handle_delete_prompt_events(self, events):
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            
            if event.type == pygame.MOUSEMOTION:
                self.prompt_selection = ''
                if self.prompt_rects['是'].collidepoint(event.pos):
                    self.prompt_selection = '是'
                elif self.prompt_rects['否'].collidepoint(event.pos):
                    self.prompt_selection = '否'

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.prompt_selection == '是':
                    save_manager.delete_save(self.save_files[self.hovered_option]['path'])
                    
                    # --- ↓↓↓ 【【【本次修改：確保刪除後也進入故事場景】】】 ↓↓↓ ---
                    save_manager.create_new_save()
                    self.manager.start_new_run()
                    
                    # 和 main_menu_scene 的邏輯保持一致
                    story_scene = self.manager.scenes['story']
                    story_scene.setup() 
                    self.manager.switch_to_scene('story')
                    # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

                elif self.prompt_selection == '否':
                    self.show_delete_prompt = False
    
    def update(self):
        """此場景為靜態，不需更新"""
        pass

    def get_slot_rect(self, index):
        rect = pygame.Rect(0, 0, 700, 80)
        rect.center = (SCREEN_WIDTH / 2, 250 + index * 100)
        return rect
        
    def draw(self, screen):
        screen.fill(UI_BG_COLOR)
        title_font = assets.get_font('title')
        menu_font = assets.get_font('weapon_ui')
        ui_font = assets.get_font('weapon_ui') 
        
        title_text = "讀取進度" if self.mode == 'load' else "刪除存檔以建立新遊戲"
        title_surf = title_font.render(title_text, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 100))
        screen.blit(title_surf, title_rect)
        
        for i, file in enumerate(self.save_files):
            rect = self.get_slot_rect(i)
            color = HOVER_COLOR if i == self.hovered_option else UI_BORDER_COLOR
            pygame.draw.rect(screen, color, rect, width=2, border_radius=5)
            
            dt_object = datetime.fromtimestamp(file['time'])
            time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            time_surf = menu_font.render(time_str, True, WHITE)
            time_rect = time_surf.get_rect(midleft=(rect.left + 20, rect.centery))
            screen.blit(time_surf, time_rect)

            highest_level = file.get('highest_level', 1)
            level_text = f"最高進度: 關卡 {highest_level}"
            level_surf = ui_font.render(level_text, True, WHITE)
            level_rect = level_surf.get_rect(midright=(rect.right - 20, rect.centery))
            screen.blit(level_surf, level_rect)

        if self.show_delete_prompt:
            self.draw_delete_prompt(screen)
            
    def draw_delete_prompt(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        prompt_font = assets.get_font('menu')
        prompt_surf = prompt_font.render("確定要刪除這個存檔嗎？", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        screen.blit(prompt_surf, prompt_rect)

        yes_surf = prompt_font.render("是", True, HOVER_COLOR if self.prompt_selection == '是' else WHITE)
        no_surf = prompt_font.render("否", True, HOVER_COLOR if self.prompt_selection == '否' else WHITE)
        
        yes_rect = yes_surf.get_rect(center=(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 50))
        no_rect = no_surf.get_rect(center=(SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT/2 + 50))

        self.prompt_rects = {'是': yes_rect, '否': no_rect}
        screen.blit(yes_surf, yes_rect)
        screen.blit(no_surf, no_rect)