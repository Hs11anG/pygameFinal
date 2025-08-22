# weapon.py
import pygame
from settings import *
from asset_manager import assets
# 引入所有可能的飛行物類別，為下面的對照表做準備
from projectile import BswordProjectile, BoardProjectile

# 建立一個"類別名稱"(字串) -> 實際類別 的對照表
PROJECTILE_CLASSES = {
    'BswordProjectile': BswordProjectile,
    'BoardProjectile': BoardProjectile,
    # 未來新增飛行物類別時，只需要加在這裡
}

class Weapon(pygame.sprite.Sprite):
    def __init__(self, position, weapon_type):
        # 呼叫 super().__init__() 時不應傳入任何參數
        super().__init__()
        
        self.data = WEAPON_DATA.get(weapon_type)
        if not self.data:
            self.kill()
            return
            
        self.weapon_type = weapon_type
        
        # 圖像設定
        original_image = assets.get_image(self.data['id'])
        self.image = pygame.transform.scale(original_image, self.data['size'])
        self.rect = self.image.get_rect(center=position)

        # 狀態管理
        self.state = 'idle' # 'idle', 'in_range', 'active'
        
        # 冷卻時間初始化，確保武器一開始就是可用的
        cooldown_ms = self.data['cooldown'] * 1000
        self.last_shot_time = pygame.time.get_ticks() - cooldown_ms

    def update(self, player):
        """每幀更新武器狀態，主要檢查與玩家的距離"""
        # 只有在不被玩家主動操作時，才根據距離更新狀態
        if self.state != 'active':
            distance_to_player = pygame.Vector2(self.rect.center).distance_to(player.rect.center)
            # 互動範圍可以根據需要調整
            if distance_to_player < 60:
                self.state = 'in_range'
            else:
                self.state = 'idle'

    def fire(self, target_pos, projectile_group):
        """根據設定檔動態創建對應的飛行物"""
        now = pygame.time.get_ticks()
        cooldown = self.data['cooldown'] * 1000
        
        if now - self.last_shot_time > cooldown:
            self.last_shot_time = now
            
            # 1. 從設定檔中讀取飛行物的"名字"(字串)
            class_name = self.data.get('projectile_class_name')
            
            # 2. 用這個名字去對照表裡找出真正的類別
            ProjectileClass = PROJECTILE_CLASSES.get(class_name)
            
            if ProjectileClass:
                # 3. 使用找到的類別來建立實例
                new_projectile = ProjectileClass(self.rect.center, target_pos, self.weapon_type)
                projectile_group.add(new_projectile)
            else:
                print(f"警告：在 PROJECTILE_CLASSES 中找不到名為 '{class_name}' 的類別！")
            
    def draw_ui(self, screen):
        """繪製武器自身的 UI，包含名稱、提示和冷卻時間"""
        font = assets.get_font('weapon_ui') 
        if not font: return

        text = ""
        color = WHITE
        
        now = pygame.time.get_ticks()
        cooldown = self.data['cooldown'] * 1000
        elapsed_since_last_shot = now - self.last_shot_time
        
        # 優先顯示冷卻時間
        if elapsed_since_last_shot < cooldown:
            remaining_cd = (cooldown - elapsed_since_last_shot) / 1000
            text = f"{remaining_cd:.1f}s"
        # 冷卻完畢後，再根據狀態顯示
        else:
            if self.state == 'active':
                text = "Ready"
            elif self.state == 'in_range':
                text = "按E裝備"
            elif self.state == 'idle':
                text = self.data['name']
                color = HOVER_COLOR
        
        # 如果有文字需要顯示，才繪製背景和文字
        if text:
            text_surf = font.render(text, True, color)
            bg_rect = text_surf.get_rect(midbottom=self.rect.midtop).inflate(20, 10) # 加上邊距
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
            pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=5)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))