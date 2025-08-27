# weapon.py
import pygame
from settings import *
from asset_manager import assets
from projectile import BswordProjectile, BoardProjectile

PROJECTILE_CLASSES = {
    'BswordProjectile': BswordProjectile,
    'BoardProjectile': BoardProjectile,
}
