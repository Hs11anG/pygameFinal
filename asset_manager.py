# asset_manager.py
import pygame

class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # --- ↓↓↓ 【【【本次修改：初始化 Mixer 並新增 music 字典】】】 ↓↓↓ ---
        pygame.mixer.init()
        self.fonts = {}
        self.images = {}
        self.music = {} # 用來存放音樂路徑
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
        print("AssetManager initialized.")

    def load_font(self, name, path, size):
        try:
            self.fonts[name] = pygame.font.Font(path, size)
            print(f"Font '{name}' loaded from {path}")
        except pygame.error as e:
            print(f"Error loading font '{name}' from {path}: {e}")
            self.fonts[name] = pygame.font.Font(None, size)

    def get_font(self, name):
        font = self.fonts.get(name)
        if font is None:
            print(f"Warning: Font '{name}' not found!")
        return font

    def load_image(self, name, path):
        try:
            image = pygame.image.load(path)
            self.images[name] = image.convert_alpha()
            print(f"Image '{name}' loaded from {path}")
        except pygame.error as e:
            print(f"Error loading image '{name}' from {path}: {e}")

    def get_image(self, name):
        image = self.images.get(name)
        if image is None:
            print(f"Warning: Image '{name}' not found!")
        return image

    # --- ↓↓↓ 【【【本次新增：載入與播放音樂的函式】】】 ↓↓↓ ---
    def load_music(self, name, path):
        """僅記錄音樂的名稱和路徑，不實際載入到記憶體"""
        self.music[name] = path
        print(f"Music '{name}' path registered: {path}")

    def play_music(self, name, loops=-1, volume=0.5):
        """根據名稱播放音樂"""
        path = self.music.get(name)
        if path:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
                print(f"Playing music '{name}' from {path}")
            except pygame.error as e:
                print(f"Error playing music '{name}' from {path}: {e}")
        else:
            print(f"Warning: Music '{name}' not found!")
    # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

# 全局唯一的實例
assets = AssetManager()