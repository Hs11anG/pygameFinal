# player.py
import pygame
from asset_manager import assets
from settings import *
from weapon import PROJECTILE_CLASSES
from projectile import BswordProjectile

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, level_number):
        super().__init__()
        
        original_image = assets.get_image('player')
        player_size = LEVELS[level_number]['playersize']
        self.image = pygame.transform.scale(original_image, player_size)
        self.rect = self.image.get_rect(midbottom=start_pos)
        
        self.base_speed = 5
        self.base_skill_1_duration = 5000
        self.base_skill_1_cooldown = 10000
        self.base_skill_2_duration = 3000
        self.base_skill_2_cooldown = 12000

        self.speed_multiplier = 1.0
        self.skill_duration_bonus = 0
        self.skill_cooldown_multiplier = 1.0
        self.global_cooldown_multiplier = 1.0
        
        self.weapon_data = {k: v.copy() for k, v in WEAPON_DATA.items()}
        self.speed = self.base_speed
        self.default_weapon_type = 1
        self.last_shot_time = {}
        
        self.skill_1_weapon_type = 2
        self.skill_1_active = False
        self.skill_1_activation_time = 0
        
        self.skill_2_active = False
        self.skill_2_activation_time = 0
        
        self.reset_cooldowns()
        self.can_move = True

    def reset_cooldowns(self):
        print("所有技能冷卻時間與狀態已重置！")
        now = pygame.time.get_ticks()
        
        self.skill_1_cooldown_start_time = now - (self.base_skill_1_cooldown * self.skill_cooldown_multiplier)
        self.skill_2_cooldown_start_time = now - (self.base_skill_2_cooldown * self.skill_cooldown_multiplier)
        self.last_shot_time = {}

        self.skill_1_active = False
        self.skill_1_activation_time = 0
        self.skill_2_active = False
        self.skill_2_activation_time = 0

    def adjust_timers_for_pause(self, pause_duration):
        if self.skill_1_activation_time > 0:
            self.skill_1_activation_time += pause_duration
        if self.skill_2_activation_time > 0:
            self.skill_2_activation_time += pause_duration
        
        if self.skill_1_cooldown_start_time != float('inf'):
             self.skill_1_cooldown_start_time += pause_duration
        if self.skill_2_cooldown_start_time != float('inf'):
             self.skill_2_cooldown_start_time += pause_duration

        for weapon_type in self.last_shot_time:
            self.last_shot_time[weapon_type] += pause_duration

    def to_dict(self):
        return {
            'speed_multiplier': self.speed_multiplier,
            'skill_duration_bonus': self.skill_duration_bonus,
            'skill_cooldown_multiplier': self.skill_cooldown_multiplier,
            'global_cooldown_multiplier': self.global_cooldown_multiplier,
            'weapon_data': self.weapon_data
        }

    def from_dict(self, data):
        self.speed_multiplier = data.get('speed_multiplier', 1.0)
        self.skill_duration_bonus = data.get('skill_duration_bonus', 0)
        self.skill_cooldown_multiplier = data.get('skill_cooldown_multiplier', 1.0)
        self.global_cooldown_multiplier = data.get('global_cooldown_multiplier', 1.0)
        
        weapon_data_from_json = data.get('weapon_data', {})
        self.weapon_data = {int(k): v for k, v in weapon_data_from_json.items()}
        
        if not self.weapon_data:
            self.weapon_data = {k: v.copy() for k, v in WEAPON_DATA.items()}

        self.speed = self.base_speed * self.speed_multiplier

    def apply_upgrade(self, upgrade_data):
        stat = upgrade_data['stat']
        upgrade_type = upgrade_data['type']
        value = upgrade_data['value']
        
        print(f"套用升級: {upgrade_data['name']}")

        if 'weapon_id' in upgrade_data:
            weapon_id = upgrade_data['weapon_id']
            if weapon_id in self.weapon_data:
                target_weapon = self.weapon_data[weapon_id]
                if upgrade_type == 'add':
                    target_weapon[stat] += value
                elif upgrade_type == 'multiply':
                    target_weapon[stat] *= value
        else:
            if stat == 'skill_1_duration':
                self.skill_duration_bonus += value
            elif stat == 'skill_1_cooldown':
                self.skill_cooldown_multiplier *= value
            elif stat == 'speed':
                self.speed_multiplier *= value
                self.speed = self.base_speed * self.speed_multiplier
            elif stat == 'global_cooldown':
                self.global_cooldown_multiplier *= value

    def move(self, keys, mask=None):
        if not self.can_move:
            return

        dx, dy = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += self.speed

        if mask:
            if dx != 0:
                self.rect.x += dx
                bottom_left = self.rect.bottomleft
                bottom_right = self.rect.bottomright
                if not (mask.get_at(bottom_left) > 0 and mask.get_at(bottom_right) > 0):
                    self.rect.x -= dx 

            if dy != 0:
                self.rect.y += dy
                bottom_left = self.rect.bottomleft
                bottom_right = self.rect.bottomright
                if not (mask.get_at(bottom_left) > 0 and mask.get_at(bottom_right) > 0):
                    self.rect.y -= dy
        else:
            self.rect.x += dx
            self.rect.y += dy
        
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def shoot(self, target_pos, projectile_group):
        now = pygame.time.get_ticks()
        current_weapon_type = self.skill_1_weapon_type if self.skill_1_active else self.default_weapon_type
        
        weapon_data = self.weapon_data.get(current_weapon_type)
        if not weapon_data: return
            
        cooldown = (weapon_data['cooldown'] * 1000) * self.global_cooldown_multiplier
        last_shot = self.last_shot_time.get(current_weapon_type, 0)

        if now - last_shot > cooldown:
            self.last_shot_time[current_weapon_type] = now
            class_name = weapon_data.get('projectile_class_name')
            ProjectileClass = PROJECTILE_CLASSES.get(class_name)
            if ProjectileClass:
                new_projectile = ProjectileClass(self.rect.center, target_pos, current_weapon_type)
                new_projectile.damage = weapon_data['damage']
                
                if self.skill_2_active and isinstance(new_projectile, BswordProjectile):
                    new_projectile.piercing = True

                projectile_group.add(new_projectile)
    
    def activate_skill_1(self):
        # --- ↓↓↓ 【【【本次新增：檢查另一個技能是否已啟用】】】 ↓↓↓ ---
        if self.skill_2_active:
            # print("技能 2 正在使用中，無法啟用技能 1！") # 可選：在控制台印出提示
            return
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        now = pygame.time.get_ticks()
        cooldown = self.base_skill_1_cooldown * self.skill_cooldown_multiplier
        if now - self.skill_1_cooldown_start_time >= cooldown:
            self.skill_1_active = True
            self.skill_1_activation_time = now
            self.skill_1_cooldown_start_time = float('inf') 
            print("技能 1 已啟用: 轉型正義！")

    def activate_skill_2(self):
        # --- ↓↓↓ 【【【本次新增：檢查另一個技能是否已啟用】】】 ↓↓↓ ---
        if self.skill_1_active:
            # print("技能 1 正在使用中，無法啟用技能 2！") # 可選：在控制台印出提示
            return
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        now = pygame.time.get_ticks()
        cooldown = self.base_skill_2_cooldown * self.skill_cooldown_multiplier
        if now - self.skill_2_cooldown_start_time >= cooldown:
            self.skill_2_active = True
            self.skill_2_activation_time = now
            self.skill_2_cooldown_start_time = float('inf') 
            print("技能 2 已啟用: 融會貫通！")

    def update_skills(self):
        now = pygame.time.get_ticks()
        if self.skill_1_active:
            duration = self.base_skill_1_duration + self.skill_duration_bonus
            if now - self.skill_1_activation_time > duration:
                self.skill_1_active = False
                self.skill_1_cooldown_start_time = now
                print("技能 1 持續時間結束，進入冷卻。")
        
        if self.skill_2_active:
            duration = self.base_skill_2_duration
            if now - self.skill_2_activation_time > duration:
                self.skill_2_active = False
                self.skill_2_cooldown_start_time = now
                print("技能 2 持續時間結束，進入冷卻。")

    def update(self, keys, events, projectile_group, mask=None):
        self.move(keys, mask)
        
        if keys[pygame.K_1]:
            self.activate_skill_1()
        if keys[pygame.K_2]:
            self.activate_skill_2()

        self.update_skills()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.shoot(pygame.mouse.get_pos(), projectile_group)

    def draw_ui(self, screen):
        if self.skill_1_active:
            font = assets.get_font('weapon_ui')
            if not font: return
            now = pygame.time.get_ticks()
            duration = self.base_skill_1_duration + self.skill_duration_bonus
            remaining_duration = (duration - (now - self.skill_1_activation_time)) / 1000
            if remaining_duration < 0: return
            
            text = f"{remaining_duration:.1f}s"
            color = (255, 255, 0) 
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(midbottom=self.rect.midtop, y=self.rect.top - 40, x=self.rect.centerx - 50)
            bg_rect = text_rect.inflate(8, 4)
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=3)
            pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=3)
            screen.blit(text_surf, text_rect)
            
        if self.skill_2_active:
            font = assets.get_font('weapon_ui')
            if not font: return
            now = pygame.time.get_ticks()
            duration = self.base_skill_2_duration
            remaining_duration = (duration - (now - self.skill_2_activation_time)) / 1000
            if remaining_duration < 0: return
            
            text = f"{remaining_duration:.1f}s"
            color = (0, 255, 255)
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(midbottom=self.rect.midtop, y=self.rect.top - 40, x=self.rect.centerx + 10)
            bg_rect = text_rect.inflate(8, 4)
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=3)
            pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=3)
            screen.blit(text_surf, text_rect)