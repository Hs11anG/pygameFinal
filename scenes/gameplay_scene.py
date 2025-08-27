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
from skill_effects import RescueSkill

class GameplayScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.game_state = 'inactive'
        self.player_group = pygame.sprite.GroupSingle()
        self.target_group = pygame.sprite.GroupSingle()
        self.projectile_group = pygame.sprite.Group()
        self.monster_manager = None
        self.rescue_skill_group = pygame.sprite.GroupSingle()
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
        
        # --- 訊息與教學相關 ---
        self.show_start_message = False
        self.start_message_surf = None
        self.start_message_end_time = 0
        self.start_message_duration = 3500
        self.show_tutorial = False
        self.tutorial_text = [
            "教學：移動與攻擊", "使用 [W][A][S][D] 或方向鍵來移動角色。",
            "滑鼠左鍵點擊來朝游標方向發射竹簡劍。", "注意左上角的目標生命值與剩餘時間。",
            "教學：技能", "按下 [1] 或 [2] 可施放技能，技能圖示會顯示在畫面下方。",
            "技能施放後會進入冷卻，冷卻完成才能再次使用。", "擊殺怪物累積能量，集滿可獲得三選一的強化。",
            "那麼，祝你好運！", "（按下 [空白鍵] 關閉教學）"
        ]

    def load_level(self, level_number):
        self.current_level = level_number
        level_data = LEVELS.get(level_number)
        if not level_data: return
        
        self.player_group.empty(); self.target_group.empty(); self.projectile_group.empty(); self.rescue_skill_group.empty()
        
        self.player = self.manager.get_player()
        if not self.player:
            self.manager.start_new_run()
            self.player = self.manager.get_player()

        self.player.can_move = False
        self.player.reset_cooldowns(); self.player.reset_tactical_bonuses()
        self.player.rect.midbottom = level_data['player_spawn_point']
        self.player_group.add(self.player)

        self.background_image = assets.get_image(f"{level_data['id']}_bg")
        self.protection_target = ProtectionTarget(level_data['protection_point'], level_number)
        self.target_group.add(self.protection_target)
        self.monster_manager = MonsterManager(level_data, self)

        self.level_duration = level_data.get('duration', 60) * 1000
        self.level_start_time = pygame.time.get_ticks()
        self.kill_count = 0; self.level_total_kills = 0
        self.current_upgrade_choices = []; self.upgrade_choice_rects = []
        self.show_victory_message = False; self.show_start_message = False; self.show_tutorial = False

        if self.current_level == 1 and not save_manager.tutorial_completed:
            self.game_state = 'tutorial' 
        else:
            self.trigger_level_start_message()

    def trigger_level_start_message(self):
        self.game_state = 'level_start'
        now = pygame.time.get_ticks()
        level_data = LEVELS.get(self.current_level)
        
        message_text = level_data.get('start_message', "關卡開始！")

        font = assets.get_font('title')
        if font: self.start_message_surf = font.render(message_text, True, HOVER_COLOR)
        
        self.level_start_time = now
        self.start_message_end_time = self.level_start_time + self.start_message_duration

    def handle_events(self, events):
        self.events = events
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')
            
            if self.game_state == 'tutorial':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    save_manager.mark_tutorial_as_completed(self.player)
                    self.trigger_level_start_message()
                continue 

            if self.game_state == 'choosing_upgrade':
                if event.type == pygame.KEYDOWN:
                    chosen_index = -1
                    if event.key == pygame.K_q and len(self.current_upgrade_choices) > 0: chosen_index = 0
                    elif event.key == pygame.K_w and len(self.current_upgrade_choices) > 1: chosen_index = 1
                    elif event.key == pygame.K_e and len(self.current_upgrade_choices) > 2: chosen_index = 2

                    if chosen_index != -1:
                        pause_duration = pygame.time.get_ticks() - self.pause_start_time
                        self.player.adjust_timers_for_pause(pause_duration)
                        self.level_start_time += pause_duration
                        self.player.apply_upgrade(self.current_upgrade_choices[chosen_index])
                        self.game_state = 'playing'

    def update(self):
        now = pygame.time.get_ticks()

        if self.game_state == 'level_start':
            if now >= self.start_message_end_time:
                self.game_state = 'playing'
                self.level_start_time = now
        
        elif self.game_state == 'playing':
            keys = pygame.key.get_pressed()
            if self.player: self.player.update(keys, self.events, self, self.projectile_group)
            
            if self.monster_manager: self.monster_manager.update()
            self.projectile_group.update()
            self.rescue_skill_group.update()
            
            self.check_collisions()
            self.check_game_over()
            if self.kill_count >= self.kills_for_upgrade:
                self.trigger_upgrade_choice()

        elif self.game_state == 'victory_countdown':
            if now >= self.victory_message_start_time + self.victory_message_duration:
                save_manager.unlock_next_level(self.current_level)
                save_manager.save_game(self.player)
                end_scene = self.manager.scenes['end_level']
                end_scene.setup('victory', self.current_level, self.level_total_kills, self.background_image)
                self.manager.switch_to_scene('end_level')

    def check_game_over(self):
        if self.game_state != 'playing': return

        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        time_over = elapsed_time >= self.level_duration
        target_destroyed = self.protection_target and self.protection_target.current_health <= 0

        if target_destroyed:
            # --- ↓↓↓ 【【【本次修改：在失敗時也存檔】】】 ↓↓↓ ---
            print("挑戰失敗，但永久加成已儲存。")
            save_manager.save_game(self.player) # 在切換場景前，儲存玩家狀態
            # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
            
            end_scene = self.manager.scenes['end_level']
            end_scene.setup('defeat', self.current_level, self.level_total_kills, self.background_image)
            self.manager.switch_to_scene('end_level')
        elif time_over:
            self.game_state = 'victory_countdown'
            self.show_victory_message = True
            self.victory_message_start_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))
        self.target_group.draw(screen)
        if self.monster_manager: self.monster_manager.draw(screen)
        self.projectile_group.draw(screen)
        self.rescue_skill_group.draw(screen)
        if self.rescue_skill_group.sprite: self.rescue_skill_group.sprite.draw_fire(screen)
        self.player_group.draw(screen)
        if self.player: self.player.draw_ui(screen)
        
        if self.game_state in ['level_start', 'playing', 'victory_countdown']:
            self.draw_hud(screen)
            self.draw_skill_ui(screen)
        elif self.game_state == 'choosing_upgrade':
            self.draw_upgrade_ui(screen)
        elif self.game_state == 'tutorial':
            self.draw_tutorial(screen)
        
        if self.game_state == 'level_start':
            self.draw_start_message(screen)
        elif self.game_state == 'victory_countdown':
            self.draw_countdown_and_victory(screen)
        
        if self.game_state == 'playing':
             self.draw_countdown_and_victory(screen)
    
    # ... 以下的其他函式 (spawn_rescue_skill, etc.) 維持不變 ...
    def spawn_rescue_skill(self):
        if not self.rescue_skill_group.sprite:
            y_pos = self.protection_target.rect.centery
            new_skill_effect = RescueSkill(y_pos, self.player)
            self.rescue_skill_group.add(new_skill_effect)
            return True
        return False
        
    def check_collisions(self):
        if not self.monster_manager: return
        if self.rescue_skill_group.sprite:
            rescue_skill = self.rescue_skill_group.sprite
            if rescue_skill.phase == 'approaching' and pygame.sprite.collide_rect(rescue_skill, self.protection_target):
                rescue_skill.switch_to_departing_phase()
            def check_fire_collision(skill_sprite, monster_sprite):
                offset = (monster_sprite.rect.x - skill_sprite.fire_rect.x, monster_sprite.rect.y - skill_sprite.fire_rect.y)
                return skill_sprite.fire_mask.overlap(pygame.mask.from_surface(monster_sprite.image), offset)
            monsters_hit = pygame.sprite.spritecollide(rescue_skill, self.monster_manager.monsters, False, check_fire_collision)
            for monster in monsters_hit:
                if monster.state == 'alive' and monster.take_damage(monster.max_health):
                    self.kill_count += 1; self.level_total_kills += 1
        possible_hits = pygame.sprite.groupcollide(self.projectile_group, self.monster_manager.monsters, False, False)
        for projectile, monsters_hit in possible_hits.items():
            for monster in monsters_hit:
                if projectile.alive() and pygame.sprite.collide_mask(projectile, monster) and monster not in projectile.hit_monsters:
                    if monster.take_damage(projectile.damage):
                        self.kill_count += 1; self.level_total_kills += 1
                    projectile.hit_monsters.add(monster)
                    is_piercing = getattr(projectile, 'piercing', False)
                    is_board_projectile = isinstance(projectile, BoardProjectile)
                    if not is_piercing and not is_board_projectile:
                        projectile.kill(); break 
        if self.protection_target:
            hits = pygame.sprite.spritecollide(self.protection_target, self.monster_manager.monsters, False, pygame.sprite.collide_mask)
            for monster in hits:
                if monster.state == 'alive': 
                    self.protection_target.take_damage(monster.damage)
                    monster.knockback()

    def trigger_upgrade_choice(self):
        self.game_state = 'choosing_upgrade'
        self.kill_count -= self.kills_for_upgrade
        self.pause_start_time = pygame.time.get_ticks()
        upgrade_pool = {}
        for level in range(1, self.current_level + 1):
            if level in UPGRADE_DATA: upgrade_pool.update(UPGRADE_DATA[level])
        now = pygame.time.get_ticks()
        available_upgrades = []
        for key, data in upgrade_pool.items():
            is_available = True
            if data['type'] == 'reset_cooldown':
                skill_id = data['skill_id']
                s1_on_cd = not self.player.skill_1_active and (now - self.player.skill_1_cooldown_start_time) < (self.player.base_skill_1_cooldown * self.player.skill_cooldown_multipliers[1])
                s2_on_cd = not self.player.skill_2_active and (now - self.player.skill_2_cooldown_start_time) < (self.player.base_skill_2_cooldown * self.player.skill_cooldown_multipliers[2])
                s3_on_cd = (now - self.player.skill_3_cooldown_start_time) < (self.player.base_skill_3_cooldown * self.player.skill_cooldown_multipliers[3])
                if skill_id == 1 and not s1_on_cd: is_available = False
                elif skill_id == 2 and not s2_on_cd: is_available = False
                elif skill_id == 3 and not s3_on_cd: is_available = False
                elif skill_id == 'all' and not (s1_on_cd or s2_on_cd or s3_on_cd): is_available = False
            elif data['type'] == 'add_duration':
                skill_id = data['skill_id']
                if skill_id == 1 and not self.player.skill_1_active: is_available = False
                if skill_id == 2 and not self.player.skill_2_active: is_available = False
            if is_available: available_upgrades.append(data)
        k = min(3, len(available_upgrades))
        if k > 0: self.current_upgrade_choices = random.sample(available_upgrades, k=k)
        else: self.game_state = 'playing'; self.current_upgrade_choices = []

    def draw_hud(self, screen):
        font = assets.get_font('ui')
        remaining_time = max(0, self.level_duration - (pygame.time.get_ticks() - self.level_start_time))
        if self.game_state == 'level_start':
             remaining_time = self.level_duration
        time_surf = font.render(f"Time: {remaining_time / 1000:.1f}", True, WHITE)
        kills_surf = font.render(f"Kills: {self.level_total_kills}", True, WHITE)
        screen.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 20, 20))
        screen.blit(kills_surf, (SCREEN_WIDTH - kills_surf.get_width() - 20, 60))
        if self.protection_target:
            target_health_surf = font.render(f"Target HP: {self.protection_target.current_health}", True, (0, 255, 255))
            screen.blit(target_health_surf, (20, 20))

    def draw_upgrade_ui(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        key_font = assets.get_font('weapon_ui')
        title_font, desc_font = assets.get_font('ui'), assets.get_font('des')
        title_surf = title_font.render("選擇一項強化", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH / 2, 150)))
        card_width, card_height = 350, 250
        keys = ['Q', 'W', 'E']
        num_cards = len(self.current_upgrade_choices)
        total_width = num_cards * card_width + (num_cards - 1) * 50
        start_x = (SCREEN_WIDTH - total_width) / 2
        card_y = SCREEN_HEIGHT / 2 - card_height / 2
        for i, upgrade in enumerate(self.current_upgrade_choices):
            card_x = start_x + i * (card_width + 50)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, UI_BG_COLOR, card_rect, border_radius=10)
            pygame.draw.rect(screen, UI_BORDER_COLOR, card_rect, width=2, border_radius=10)
            color = (100, 255, 100) if upgrade['category'] == 'tactical' else (100, 200, 255)
            key_surf = key_font.render(f"[{keys[i]}]", True, WHITE)
            name_surf = title_font.render(upgrade['name'], True, color)
            desc_surf = desc_font.render(upgrade['description'], True, WHITE)
            screen.blit(key_surf, key_surf.get_rect(center=(card_rect.centerx, card_rect.top + 40)))
            screen.blit(name_surf, name_surf.get_rect(center=(card_rect.centerx, card_rect.top + 100)))
            screen.blit(desc_surf, desc_surf.get_rect(center=(card_rect.centerx, card_rect.top + 180)))

    def draw_countdown_and_victory(self, screen):
        now = pygame.time.get_ticks()
        if self.game_state == 'victory_countdown' and self.show_victory_message:
            progress = min(1.0, (now - self.victory_message_start_time) / self.victory_message_duration)
            font_size = int(80 + (180 - 80) * progress)
            font = pygame.font.Font('BoutiqueBitmap9x9_Bold_1.9.ttf', font_size)
            text_surf = font.render("! 成 功 守 護 !", True, HOVER_COLOR)
            screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
            return

        remaining_time_ms = max(0, self.level_duration - (now - self.level_start_time))
        if self.game_state == 'playing' and remaining_time_ms <= 5000:
            scale = 1.0 + ((1000 - (remaining_time_ms % 1000)) / 1000) * 0.5 
            font = pygame.font.Font('BoutiqueBitmap9x9_Bold_1.9.ttf', int(150 * scale))
            text_surf = font.render(str(math.ceil(remaining_time_ms / 1000)), True, WHITE)
            screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

    def draw_skill_ui(self, screen):
        if not self.player: return
        self.draw_single_skill(screen, '1', 'skill1', self.player.skill_1_active, self.player.skill_1_cooldown_start_time, self.player.base_skill_1_cooldown, self.player.skill_cooldown_multipliers[1], -90)
        if save_manager.is_level_unlocked(2):
            self.draw_single_skill(screen, '2', 'skill2', self.player.skill_2_active, self.player.skill_2_cooldown_start_time, self.player.base_skill_2_cooldown, self.player.skill_cooldown_multipliers[2], 0, (0, 255, 255))
        if save_manager.is_level_unlocked(3):
            self.draw_single_skill(screen, '3', 'skill3_icon', False, self.player.skill_3_cooldown_start_time, self.player.base_skill_3_cooldown, self.player.skill_cooldown_multipliers[3], 90, (255, 100, 0))

    def draw_single_skill(self, screen, key_text, icon_id, active, cd_start, base_cd, cd_multi, offset, active_color=(255, 255, 0)):
        font, key_font = assets.get_font('ui'), assets.get_font('weapon_ui')
        if not font or not key_font: return
        icon_image = assets.get_image(icon_id)
        if not icon_image: return
        icon_rect = pygame.transform.scale(icon_image, (50, 50)).get_rect(center=(SCREEN_WIDTH//2 + offset, SCREEN_HEIGHT - 80))
        bg_rect = icon_rect.inflate(10, 10)
        pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
        pygame.draw.rect(screen, active_color if active else UI_BORDER_COLOR, bg_rect, width=2, border_radius=5)
        screen.blit(pygame.transform.scale(icon_image, (50, 50)), icon_rect)
        key_surf = key_font.render(key_text, True, WHITE)
        screen.blit(key_surf, key_surf.get_rect(center=(icon_rect.centerx, icon_rect.top - 15)))
        now = pygame.time.get_ticks()
        remaining_cd = (base_cd * cd_multi - (now - cd_start)) / 1000
        if not active and remaining_cd > 0:
            overlay = pygame.Surface(bg_rect.size, pygame.SRCALPHA); overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, bg_rect.topleft)
            cd_surf = font.render(f"{remaining_cd:.1f}", True, WHITE)
            screen.blit(cd_surf, cd_surf.get_rect(center=bg_rect.center))

    def draw_start_message(self, screen):
        if not self.start_message_surf: return
        now = pygame.time.get_ticks()
        elapsed_time = now - self.level_start_time
        progress = elapsed_time / self.start_message_duration
        if progress < 0 or progress > 1.0: return
        
        scale_progress = -4 * (progress - 0.5)**2 + 1
        original_width, original_height = self.start_message_surf.get_size()
        current_scale = 0.8 + 0.2 * scale_progress 
        new_width, new_height = int(original_width * current_scale), int(original_height * current_scale)
        scaled_surf = pygame.transform.smoothscale(self.start_message_surf, (new_width, new_height))
        alpha = 255 * scale_progress
        scaled_surf.set_alpha(alpha)
        rect = scaled_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100))
        screen.blit(scaled_surf, rect)

    def draw_tutorial(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)) 
        screen.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(0, 0, 800, 600); panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.draw.rect(screen, UI_BG_COLOR, panel_rect, border_radius=10)
        pygame.draw.rect(screen, UI_BORDER_COLOR, panel_rect, width=2, border_radius=10)
        title_font, text_font = assets.get_font('ui'), assets.get_font('des')
        line_y = panel_rect.top + 50
        for i, line in enumerate(self.tutorial_text):
            is_title = "教學：" in line
            font = title_font if is_title else text_font
            color = HOVER_COLOR if is_title else WHITE
            if is_title and i > 0: line_y += 30
            text_surf = font.render(line, True, color)
            text_rect = text_surf.get_rect(centerx=panel_rect.centerx, top=line_y)
            screen.blit(text_surf, text_rect)
            line_y += text_surf.get_height() + 15