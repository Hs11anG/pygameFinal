# save_manager.py
import json
import os
import glob
from datetime import datetime

SAVE_DIR = 'saves'
MAX_SAVES = 4

class SaveManager:
    def __init__(self):
        self.current_save_path = None
        self.current_save_data = {} # 用來存放當前活動存檔的內容
        self.ensure_save_dir_exists()

    def ensure_save_dir_exists(self):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    def get_all_saves(self):
        """讀取所有存檔檔案的資訊"""
        save_files = glob.glob(os.path.join(SAVE_DIR, '*.json'))
        saves_data = []
        for file_path in save_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filepath'] = file_path
                    saves_data.append(data)
            except (json.JSONDecodeError, IOError):
                print(f"警告：無法讀取或解析存檔 {file_path}")
        
        saves_data.sort(key=lambda s: s.get('last_saved', 0), reverse=True)
        return saves_data

    def create_new_save(self):
        """創建一個新的存檔檔案，並將其載入為當前存檔"""
        now = datetime.now()
        timestamp = now.strftime('%y_%m_%d_%H_%M')
        filename = f"{timestamp}_save.json"
        filepath = os.path.join(SAVE_DIR, filename)
        
        new_save_data = {
            'display_name': f"{now.strftime('%Y/%m/%d %H:%M')}",
            'last_saved': now.timestamp(),
            'unlocked_level': 1,
            'gold': 0,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(new_save_data, f, indent=4)
        
        # 創建後立刻載入
        self.load_save(filepath)
        print(f"已創建並載入新存檔: {filepath}")
        return new_save_data

    def load_save(self, filepath):
        """【修改】載入一個指定的存檔，讀取其內容並設為當前活動存檔"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.current_save_data = json.load(f)
                self.current_save_path = filepath
                print(f"已載入存檔: {self.current_save_path}")
                print(f"當前進度: {self.current_save_data}")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"警告：載入存檔 {filepath} 失敗")
            self.current_save_path = None
            self.current_save_data = {}

    # ↓↓↓ 【【【這就是補上的方法】】】 ↓↓↓
    def is_level_unlocked(self, level_number):
        """檢查傳入的關卡編號是否已經被解鎖"""
        # 這個方法會檢查當前載入的存檔資料
        return level_number <= self.current_save_data.get('unlocked_level', 0)

    def unlock_next_level(self, completed_level):
        """解鎖下一關並存檔"""
        if not self.current_save_path: return

        next_level = completed_level + 1
        # 只有在解鎖了更高關卡時才更新
        if next_level > self.current_save_data.get('unlocked_level', 1):
            self.current_save_data['unlocked_level'] = next_level
            self.update_current_save() # 呼叫通用更新方法

    def update_current_save(self):
        """使用 self.current_save_data 的內容更新當前存檔檔案"""
        if not self.current_save_path: return

        now = datetime.now()
        self.current_save_data['last_saved'] = now.timestamp()
        self.current_save_data['display_name'] = f"{now.strftime('%Y/%m/%d %H:%M')}"
        
        try:
            with open(self.current_save_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_save_data, f, indent=4)
            print(f"存檔已更新: {self.current_save_path}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"更新存檔失敗: {e}")

    def delete_save(self, filepath):
        """刪除指定的存檔檔案"""
        try:
            os.remove(filepath)
            print(f"存檔已刪除: {filepath}")
            return True
        except OSError as e:
            print(f"刪除存檔失敗: {e}")
            return False

# 建立全局唯一的存檔管理器實例
save_manager = SaveManager()