import pygame
import os
from animated_sprite import load_spritesheet, AnimatedSprite
from actors.base_classes import Enemy

def append_path(func):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    def func_with_path(filename, *args):
        return func(os.path.join(dir_path, filename), *args)
    return func_with_path

load_image = append_path(pygame.image.load)
load_spritesheet = append_path(load_spritesheet)


class EnemyCommonSprite(AnimatedSprite):
    enemy_walk = load_spritesheet('onion-walk.png', (32, 39))

    def __init__(self, *groups):
        super(EnemyCommonSprite, self).__init__(*groups)
        self.sheet = self.enemy_walk
        self.interval = 0.3
        self.rect = pygame.rect.Rect((0, 0), (32, 39))

    def update(self, dt, enemy_rect):
        self.rect.midbottom = enemy_rect.midbottom
        self.update_animation(dt)


class EnemyShellSprite(pygame.sprite.Sprite):
    enemy_image = load_image('enemyshell.png')
    shell_image = load_image('shell.png')

    def __init__(self, pos, *groups):
        super(EnemyShellSprite, self).__init__(*groups)
        self.image = self.enemy_image
        self.walk_rect = self.enemy_image.get_rect()
        self.hide_rect = self.shell_image.get_rect()
        self.rect = self.walk_rect
        self.rect.topleft = pos

    def update(self, enemy_rect, state):
        if state == Enemy.bWalk:
            self.image = self.enemy_image
            self.rect.size = self.walk_rect.size
        elif state == Enemy.bHide:
            self.image = self.shell_image
            self.rect.size = self.hide_rect.size

        self.rect.midbottom = enemy_rect.midbottom


class PlayerSprite(AnimatedSprite):
    walk_right  = load_spritesheet('player-walk-right.png', 32)
    walk_left   = load_spritesheet('player-walk-left.png', 32)
    stand_right = load_spritesheet('player-right.png', 32)
    stand_left  = load_spritesheet('player-left.png', 32)
    jump_right  = load_spritesheet('player-jump-right.png', 32)
    jump_left   = load_spritesheet('player-jump-left.png', 32)

    def __init__(self, *groups):
        super(PlayerSprite, self).__init__(*groups)
        self.sheet = self.walk_right
        self.interval = 0.4
        self.rect = pygame.rect.Rect((0, 0), (32, 32))

    def update(self, dt, player_rect, resting, direction, dx):
        self.rect.midbottom = player_rect.midbottom

        if not resting:
            if direction == 1:
                self.sheet = self.jump_right
            else:
                self.sheet = self.jump_left
        else:
            if dx > 0:
                self.sheet = self.walk_right
            elif dx < 0:
                self.sheet = self.walk_left
            elif direction == 1:
                self.sheet = self.stand_right
            elif direction == -1:
                self.sheet = self.stand_left

        self.update_animation(dt)
