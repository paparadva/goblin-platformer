import pygame
from base_classes import Enemy, Actor, MAXFALL, GRAVITY
from game import post_event
from events import *

#  TODO: shrink actors' rects a little so that they will fit into 1 tile wide holes easier

class EnemyCommon(Enemy):
    def __init__(self, pos, sprite, group):
        super(EnemyCommon, self).__init__(sprite, group)
        self.rect = pygame.rect.Rect(pos, (32, 32))

    def update(self, dt, game):
        move_x = 0
        move_y = 0

        move_x = 100 * self.direction * dt

        self.dy = min(MAXFALL, self.dy + GRAVITY)
        move_y = self.dy * dt

        game.collide_blocks(self, move_x, move_y)
        if game.triggers.collide(self.rect, 'reverse'):
            self.direction *= -1

        self.sprite.update(dt, self.rect)

    def on_collide_actor(self, other):
        pass


class EnemyShell(Enemy):
    def __init__(self, pos, sprite, group):
        super(EnemyShell, self).__init__(sprite, group)
        self.walk_rect = pygame.rect.Rect(pos, (32, 32))
        self.hide_rect = pygame.rect.Rect(pos, (32, 16))
        self.rect = self.walk_rect

        self.hiding = False
        self.speed = 100

    def update(self, dt, game):
        move_x = 0
        move_y = 0

        move_x = self.speed * self.direction * dt

        self.dy = min(MAXFALL, self.dy + GRAVITY)
        move_y = self.dy * dt

        game.collide_blocks(self, move_x, move_y)

        if self.state == self.bWalk and game.triggers.collide(self.rect, 'reverse'):
            self.direction *= -1

        self.sprite.update(self.rect, self.state)

    def stomp(self):
        if self.state == self.bWalk:
            self.state = self.bHide

            old = self.rect.copy()
            
            self.rect.size = self.hide_rect.size
            self.rect.midbottom = old.midbottom

            self.speed = 0

        elif self.state == self.bSpin:
            self.state = self.bHide
            self.speed = 0

        elif self.state == self.bHide:
            self.killit()

    def push(self, pusher):
        self.state = self.bSpin
        self.speed = 400
        if pusher.rect.centerx >= self.rect.centerx:
            self.direction = -1
            self.rect.right = pusher.rect.left
        else:
            self.direction = 1
            self.rect.left = pusher.rect.right

    def on_collide_actor(self, other):
        if self.state == self.bSpin:
            if isinstance(other, Enemy):
                if other.state == other.bSpin:
                    other.push(self)
                    self.push(other)
                else:
                    other.killit()


class Player(Actor):
    JUMP_SPD = 500
    JUMPTIME = 0.2

    def __init__(self, pos, sprite, group):
        super(Player, self).__init__(sprite, group)

        self.rect = pygame.rect.Rect(pos, (32, 32))
        self.sprite.interval = 0.2

        self.dy = 0
        self.resting = False
        self.jumping_time = -1
        self.direction = 1

        self.coins = 0

    def update(self, dt, game):
        self.last = self.rect.copy()
        move_x = 0
        move_y = 0

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            move_x = -300 * dt
            self.direction = -1
        if key[pygame.K_RIGHT]:
            move_x = 300 * dt
            self.direction = 1

        if self.jumping_time >= self.JUMPTIME:
            self.jumping_time = -1

        if self.jumping_time > -1:
            if not key[pygame.K_UP]:
                self.jumping_time = -1
            elif self.dy < 0:
                self.jump(-self.JUMP_SPD)
                self.jumping_time += dt        

        if self.resting and key[pygame.K_UP]:
            self.start_jump(-self.JUMP_SPD)

        self.dy = min(MAXFALL, self.dy + GRAVITY)
        move_y = self.dy * dt

        game.collide_blocks(self, move_x, move_y)
        game.collide_coins(self)
        if game.triggers.collide(self.rect, 'exit'):
            post_event(EXIT_LEVEL)

        game.tilemap.set_focus(self.rect.x, self.rect.y)

        self.sprite.update(dt,
                           self.rect, 
                           self.resting,
                           self.direction,
                           self.rect.x - self.last.x)

    def deal_damage(self):
        post_event(PLAYER_DIED)

    def start_jump(self, yforce):
        self.jumping_time = 0
        self.jump(yforce)

    def jump(self, yforce):
        self.dy = yforce
        self.resting = False

    def on_collide_actor(self, other):
        if self.last.bottom <= other.rect.top + 5:
            other.stomp()
            self.rect.bottom = other.rect.top
            self.start_jump(-200)

        elif other.state == other.bHide:
            other.push(self)

        elif other.state in (other.bWalk, other.bSpin):
            self.deal_damage()

