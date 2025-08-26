# scenes/gameplay_scene.py
import pygame
import random
import math
from settings import *
from scene_manager import Scene
from asset_manager import assets
from player import Player
from monster_manager import MonsterManager
from save_manager import save_manager
from projectile import BswordProjectile, BoardProjectile
from protection_target import ProtectionTarget
# --- ↓↓↓ 【【【本次新增：引入新技能類別】】】 ↓↓↓ ---
from skill_effects import RescueSkill
# --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

class GameplayScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.game_state = 'inactive'
        
        self.player_group = pygame.sprite.GroupSingle()
        self.target_group = pygame.sprite.GroupSingle()
        self.projectile_group = pygame.sprite.Group()
        self.monster_manager = None
        # --- ↓↓↓ 【【【本次新增：技能3專用的 Sprite Group】】】 ↓↓↓ ---
        self.rescue_skill_group = pygame.sprite.GroupSingle()
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        
        self.player = None
        self.protection_target = None
        self.background_image = None
        self.level_duration = 0
        self.level_start_time = 0
        self.events = []
        self.current_level = 0
        
        self.kill_count = 0
        self.kills_for_upgrade = 10
        self.level_total_kills = 0
        
        self.current_upgrade_choices = []
        self.upgrade_choice_rects = []
        
        self.pause_start_time = 0 

        self.countdown_font = pygame.font.Font('NotoSerifTC-ExtraBold.ttf', 150)
        self.show_victory_message = False
        self.victory_message_start_time = 0
        self.victory_message_duration = 2000

    def load_level(self, level_number):
        self.current_level = level_number
        level_data = LEVELS.get(level_number)
        if not level_data: return
        
        print(f"載入關卡 {level_number}: {level_data['name']}")
        
        self.player_group.empty()
        self.target_group.empty()
        self.projectile_group.empty()
        # --- ↓↓↓ 【【【本次新增：清空技能3 Group】】】 ↓↓↓ ---
        self.rescue_skill_group.empty()
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        
        self.player = self.manager.get_player()
        if not self.player:
            print("警告：找不到玩家物件，將創建一個新的")
            self.manager.start_new_run()
            self.player = self.manager.get_player()

        self.player.can_move = False
        self.player.reset_cooldowns()

        spawn_point = level_data['player_spawn_point']
        self.player.rect.midbottom = spawn_point
        self.player_group.add(self.player)

        level_id = level_data['id']
        self.background_image = assets.get_image(f'{level_id}_bg')
        
        target_pos = level_data['protection_point']
        self.protection_target = ProtectionTarget(target_pos, level_number)
        self.target_group.add(self.protection_target)
        
        self.monster_manager = MonsterManager(level_data, self)
        
        self.level_duration = level_data.get('duration', 60) * 1000
        self.level_start_time = pygame.time.get_ticks()
        self.game_state = 'playing'
        
        self.kill_count = 0
        self.level_total_kills = 0

        self.current_upgrade_choices = []
        self.upgrade_choice_rects = []
        
        self.show_victory_message = False
        self.victory_message_start_time = 0
        
    # --- ↓↓↓ 【【【本次新增：產生技能3實體的方法】】】 ↓↓↓ ---
    def spawn_rescue_skill(self):
        # 檢查畫面上是否已經有救援車輛了，防止重複施放
        if not self.rescue_skill_group.sprite:
            # 讓車輛與保護目標等高
            y_pos = self.protection_target.rect.centery
            new_skill_effect = RescueSkill(y_pos)
            self.rescue_skill_group.add(new_skill_effect)
            return True # 回傳 True 表示成功產生
        return False # 回傳 False 表示畫面上已有實體，產生失敗
    # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

    def handle_events(self, events):
        self.events = events
        if self.game_state in ['playing', 'victory_countdown']:
            for event in self.events:
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.manager.switch_to_scene('main_menu')
        
        if self.game_state == 'choosing_upgrade':
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(self.upgrade_choice_rects):
                        if rect.collidepoint(event.pos):
                            pause_duration = pygame.time.get_ticks() - self.pause_start_time
                            self.player.adjust_timers_for_pause(pause_duration)
                            self.level_start_time += pause_duration

                            chosen_upgrade = self.current_upgrade_choices[i]
                            self.player.apply_upgrade(chosen_upgrade)
                            self.game_state = 'playing'
                            self.current_upgrade_choices = []
                            self.upgrade_choice_rects = []
                            break
                
    def check_collisions(self):
        if not self.monster_manager: return

        # --- ↓↓↓ 【【【本次新增：技能3與怪物的碰撞偵測】】】 ↓↓↓ ---
        if self.rescue_skill_group.sprite:
            rescue_skill = self.rescue_skill_group.sprite
            
            # 使用一個自訂的回呼函式來做 mask perfect collision
            def check_fire_collision(skill_sprite, monster_sprite):
                # 計算兩個 mask 的相對偏移
                offset = (monster_sprite.rect.x - skill_sprite.fire_rect.x, 
                          monster_sprite.rect.y - skill_sprite.fire_rect.y)
                # 檢查怪物的 mask 是否與火焰的 mask 重疊
                monster_mask = pygame.mask.from_surface(monster_sprite.image)
                return skill_sprite.fire_mask.overlap(monster_mask, offset)

            # 找出所有與火焰碰撞的怪物
            monsters_hit = pygame.sprite.spritecollide(
                rescue_skill, 
                self.monster_manager.monsters, 
                False, # 不要自動刪除怪物
                check_fire_collision
            )
            
            for monster in monsters_hit:
                if monster.state == 'alive':
                    # 直接呼叫 die() 來觸發死亡動畫並計入擊殺
                    if monster.take_damage(monster.max_health): # 用最大血量確保秒殺
                        self.kill_count += 1
                        self.level_total_kills += 1
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

        possible_hits = pygame.sprite.groupcollide(
            self.projectile_group, 
            self.monster_manager.monsters, 
            False, False
        )
        for projectile, monsters_hit in possible_hits.items():
            for monster in monsters_hit:
                if pygame.sprite.collide_mask(projectile, monster) and monster not in projectile.hit_monsters:
                    just_died = monster.take_damage(projectile.damage)
                    if just_died:
                        self.kill_count += 1
                        self.level_total_kills += 1
                    
                    projectile.hit_monsters.add(monster)
                    
                    is_piercing_bsword = isinstance(projectile, BswordProjectile) and projectile.piercing
                    if not isinstance(projectile, BoardProjectile) and not is_piercing_bsword:
                         projectile.kill()
                    
                    if not is_piercing_bsword:
                        break 

        if self.protection_target:
            hits = pygame.sprite.spritecollide(
                self.protection_target,
                self.monster_manager.monsters,
                False,
                pygame.sprite.collide_mask
            )
            for monster in hits:
                if monster.state == 'alive': 
                    self.protection_target.take_damage(monster.damage)
                    monster.knockback()

    def check_game_over(self):
        if self.protection_target and self.protection_target.current_health <= 0:
            self.game_state = 'defeat'
            end_scene = self.manager.scenes['end_level']
            end_scene.setup('defeat', self.current_level, self.level_total_kills, self.background_image)
            self.manager.switch_to_scene('end_level')
            return

        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        if elapsed_time >= self.level_duration:
            if self.protection_target.current_health > 0:
                self.game_state = 'victory_countdown'
                if not self.show_victory_message:
                    self.show_victory_message = True
                    self.victory_message_start_time = pygame.time.get_ticks()
            else:
                self.game_state = 'defeat'
                end_scene = self.manager.scenes['end_level']
                end_scene.setup('defeat', self.current_level, self.level_total_kills, self.background_image)
                self.manager.switch_to_scene('end_level')

    def trigger_upgrade_choice(self):
        self.game_state = 'choosing_upgrade'
        self.kill_count -= self.kills_for_upgrade
        self.pause_start_time = pygame.time.get_ticks()
        available_upgrades = list(UPGRADE_DATA.keys())
        k = min(3, len(available_upgrades))
        if k > 0:
            chosen_keys = random.sample(available_upgrades, k=k)
            self.current_upgrade_choices = [UPGRADE_DATA[key] for key in chosen_keys]
        else:
            self.current_upgrade_choices = []

    def update(self):
        if self.game_state == 'playing':
            keys = pygame.key.get_pressed()
            if self.player:
                # --- ↓↓↓ 【【【本次修改：傳入 gameplay_scene 給 player】】】 ↓↓↓ ---
                self.player.update(keys, self.events, self, self.projectile_group)
                # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
            if self.monster_manager:
                self.monster_manager.update()
            self.projectile_group.update()
            # --- ↓↓↓ 【【【本次新增：更新技能3】】】 ↓↓↓ ---
            self.rescue_skill_group.update()
            # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
            self.check_collisions()
            self.check_game_over()
            if self.kill_count >= self.kills_for_upgrade:
                self.trigger_upgrade_choice()
        
        elif self.game_state == 'victory_countdown':
            now = pygame.time.get_ticks()
            if self.show_victory_message and now >= self.victory_message_start_time + self.victory_message_duration:
                save_manager.unlock_next_level(self.current_level)
                save_manager.save_game(self.player)
                
                end_scene = self.manager.scenes['end_level']
                end_scene.setup('victory', self.current_level, self.level_total_kills, self.background_image)
                self.manager.switch_to_scene('end_level')

    def draw_hud(self, screen):
        font = assets.get_font('ui')
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        remaining_time = max(0, self.level_duration - elapsed_time)
        time_text = f"Time: {remaining_time / 1000:.1f}"
        time_surf = font.render(time_text, True, WHITE)
        screen.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 20, 20))
        
        kills_text = f"Kills: {self.level_total_kills}"
        kills_surf = font.render(kills_text, True, WHITE)
        screen.blit(kills_surf, (SCREEN_WIDTH - kills_surf.get_width() - 20, 60))
        
        if self.protection_target:
            target_health_text = f"Target HP: {self.protection_target.current_health}"
            target_health_surf = font.render(target_health_text, True, (0, 255, 255))
            screen.blit(target_health_surf, (20, 20))

    def draw_upgrade_ui(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_font = assets.get_font('ui')
        desc_font = assets.get_font('weapon_ui')
        
        title_surf = title_font.render("選擇一項強化", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(title_surf, title_rect)
        
        card_width, card_height = 300, 250
        total_width = 3 * card_width + 2 * 50
        start_x = (SCREEN_WIDTH - total_width) / 2
        card_y = SCREEN_HEIGHT / 2 - card_height / 2
        
        self.upgrade_choice_rects = []
        for i, upgrade in enumerate(self.current_upgrade_choices):
            card_x = start_x + i * (card_width + 50)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.upgrade_choice_rects.append(card_rect)
            
            pygame.draw.rect(screen, UI_BG_COLOR, card_rect, border_radius=10)
            pygame.draw.rect(screen, UI_BORDER_COLOR, card_rect, width=2, border_radius=10)
            
            name_surf = title_font.render(upgrade['name'], True, HOVER_COLOR)
            name_rect = name_surf.get_rect(center=(card_rect.centerx, card_rect.top + 60))
            screen.blit(name_surf, name_rect)

            desc_surf = desc_font.render(upgrade['description'], True, WHITE)
            desc_rect = desc_surf.get_rect(center=(card_rect.centerx, card_rect.top + 150))
            screen.blit(desc_surf, desc_rect)

    def draw_countdown_and_victory(self, screen):
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        remaining_time_ms = max(0, self.level_duration - elapsed_time)
        
        if self.game_state == 'playing' and remaining_time_ms <= 5000:
            countdown_sec = math.ceil(remaining_time_ms / 1000)
            text = str(countdown_sec)
            
            time_since_sec_change = 1000 - (remaining_time_ms % 1000)
            scale = 1.0 + (time_since_sec_change / 1000) * 0.5 
            font_size = int(150 * scale)
            
            dynamic_font = pygame.font.Font('NotoSerifTC-ExtraBold.ttf', font_size)
            text_surf = dynamic_font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(text_surf, text_rect)
            
        elif self.show_victory_message:
            now = pygame.time.get_ticks()
            time_since_victory_start = now - self.victory_message_start_time
            
            if time_since_victory_start < self.victory_message_duration:
                initial_font_size = 80
                max_font_size = 180
                progress = min(1.0, time_since_victory_start / self.victory_message_duration)
                current_font_size = int(initial_font_size + (max_font_size - initial_font_size) * progress)
                
                dynamic_font = pygame.font.Font('NotoSerifTC-ExtraBold.ttf', current_font_size)
                text_surf = dynamic_font.render("! 成 功 守 護 !", True, HOVER_COLOR)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                screen.blit(text_surf, text_rect)

    def draw_skill_ui(self, screen):
        if not self.player: return
        
        # --- ↓↓↓ 【【【本次修改：調整UI位置，為技能3留出空間】】】 ↓↓↓ ---
        self.draw_single_skill(
            screen, 
            key_text='1', 
            skill_icon_id='skill1', 
            skill_active=self.player.skill_1_active,
            cooldown_start_time=self.player.skill_1_cooldown_start_time,
            base_cooldown=self.player.base_skill_1_cooldown,
            cooldown_multiplier=self.player.skill_cooldown_multiplier,
            position_offset=-90 # 原為 -60
        )
        
        if save_manager.is_level_unlocked(2):
            self.draw_single_skill(
                screen, 
                key_text='2', 
                skill_icon_id='skill2', 
                skill_active=self.player.skill_2_active,
                cooldown_start_time=self.player.skill_2_cooldown_start_time,
                base_cooldown=self.player.base_skill_2_cooldown,
                cooldown_multiplier=self.player.skill_cooldown_multiplier,
                position_offset=0, # 原為 60
                active_color=(0, 255, 255)
            )
        
        # --- ↓↓↓ 【【【本次新增：繪製技能3的UI】】】 ↓↓↓ ---
        # 條件：完成第 2 關 (即解鎖第 3 關)
        if save_manager.is_level_unlocked(3):
            self.draw_single_skill(
                screen, 
                key_text='3', 
                skill_icon_id='skill3_icon', 
                skill_active=False, # 此技能為瞬發，沒有持續啟用狀態
                cooldown_start_time=self.player.skill_3_cooldown_start_time,
                base_cooldown=self.player.base_skill_3_cooldown,
                cooldown_multiplier=self.player.skill_cooldown_multiplier,
                position_offset=90, # 新增的位置
                active_color=(255, 100, 0) # 給個橘紅色
            )
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

    def draw_single_skill(self, screen, key_text, skill_icon_id, skill_active, cooldown_start_time, base_cooldown, cooldown_multiplier, position_offset, active_color=(255, 255, 0)):
        font = assets.get_font('ui')
        key_font = assets.get_font('weapon_ui')
        if not font or not key_font: return
        
        now = pygame.time.get_ticks()
        
        icon_image = assets.get_image(skill_icon_id)
        if not icon_image: return
        icon_image = pygame.transform.scale(icon_image, (50, 50))
        
        ui_base_x = SCREEN_WIDTH // 2 + position_offset
        ui_base_y = SCREEN_HEIGHT - 80
        icon_rect = icon_image.get_rect(center=(ui_base_x, ui_base_y))
        
        bg_rect = icon_rect.inflate(10, 10)
        pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
        
        border_color = UI_BORDER_COLOR
        if skill_active:
            border_color = active_color
        
        pygame.draw.rect(screen, border_color, bg_rect, width=2, border_radius=5)
        screen.blit(icon_image, icon_rect)
        
        key_surf = key_font.render(key_text, True, WHITE)
        key_rect = key_surf.get_rect(center=(icon_rect.centerx, icon_rect.top - 15))
        screen.blit(key_surf, key_rect)
        
        current_cooldown = base_cooldown * cooldown_multiplier
        is_on_cooldown = now - cooldown_start_time < current_cooldown
        
        if not skill_active and is_on_cooldown:
            cooldown_overlay = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            cooldown_overlay.fill((0, 0, 0, 180))
            screen.blit(cooldown_overlay, bg_rect.topleft)
            
            remaining_cd = (current_cooldown - (now - cooldown_start_time)) / 1000
            if remaining_cd > 0:
                cd_text = f"{remaining_cd:.1f}"
                cd_surf = font.render(cd_text, True, WHITE)
                cd_rect = cd_surf.get_rect(center=bg_rect.center)
                screen.blit(cd_surf, cd_rect)

    def draw(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((10, 20, 50))
        
        self.target_group.draw(screen)
        if self.monster_manager:
            self.monster_manager.draw(screen)
        self.projectile_group.draw(screen)
        # --- ↓↓↓ 【【【本次新增：繪製技能3】】】 ↓↓↓ ---
        # 繪製車輛本體
        self.rescue_skill_group.draw(screen)
        # 繪製火焰特效
        if self.rescue_skill_group.sprite:
            self.rescue_skill_group.sprite.draw_fire(screen)
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        self.player_group.draw(screen)

        if self.player:
            self.player.draw_ui(screen)
        
        if self.game_state == 'playing':
            self.draw_hud(screen)
            self.draw_skill_ui(screen)
        elif self.game_state == 'choosing_upgrade':
            self.draw_upgrade_ui(screen)
            
        self.draw_countdown_and_victory(screen)