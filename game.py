import pygame
import tmx
import os
import sys
import logging as log
from actors import *
from sprites import *
from events import *

def post_event(event_id, **attributes):
    e = pygame.event.Event(event_id, **attributes)
    pygame.event.post(e)    


class Level(object):
    def run(self, screen, mapname, score):
        clock = pygame.time.Clock()

        self.tilemap = tmx.load(os.path.join(mapname + '.tmx'), screen.get_size())

        log.debug("tilesets: %s", repr(self.tilemap.tilesets))
        #  Make tile with coins look like a regular block
        break_tile = self.tilemap.tilesets.match(hits=1)[0]
        coins_tile = self.tilemap.tilesets.match(coins=True)[0]
        coins_tile.surface = break_tile.surface

        self.tilemap.set_focus(300, 300)
        self.blocks = self.tilemap.layers['blocks']
        self.things = self.tilemap.layers['things']
        self.triggers = self.tilemap.layers['triggers']
        self.triggers.visible = False

        self.exhausted_tile = self.tilemap.tilesets.match(type='exhausted')[0]

        self.sprites = tmx.SpriteLayer(ignore_update=True)
        self.tilemap.layers.append(self.sprites)

        self.actors = ObjectGroup()

        start_cell = self.triggers.find('player')[0]
        #  TODO: preserve player's stats between levels
        self.player = Player(start_cell.topleft,
                             PlayerSprite(self.sprites),
                             self.actors)

        for cell in self.triggers.find('enemy'):
            EnemyCommon(cell.topleft,
                        EnemyCommonSprite(self.sprites),
                        self.actors)

        for cell in self.triggers.find('enemyshell'):
            EnemyShell(cell.topleft,
                       EnemyShellSprite(cell.topleft, self.sprites),
                       self.actors)

        self.blocks_under_enemies = list()

        while 1:
            #  TODO: low fps timing
            dt = clock.tick(30) / 1000.

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return {'reason': pygame.Quit}

                elif event.type == PLAYER_DIED:
                    return {'reason': event.type, 'score': score}

                elif event.type == EXIT_LEVEL:
                    return {'reason': event.type, 'score': score}

                elif event.type == pygame.QUIT:
                    return {'reason': event.type}

                elif event.type == COIN_PICKUP:
                    score += 10  # TODO: preserve score across levels

                elif event.type == BLOCK_BROKEN:
                    if event.byplayer:
                        for b, e in self.blocks_under_enemies:
                            if b == event.block: e.killit()
                    self.blocks.remove_cell(event.block)

                elif event.type == BLOCK_HIT:
                    for b, e in self.blocks_under_enemies:
                        if b == event.block: e.killit()

            self.blocks_under_enemies = list()

            self.actors.update(dt, self)     #  update all actors
            self.collide_actors()            #  resolve actor-with-actor collisions
            self.tilemap.tilesets.update(dt) #  update tiles

            self.tilemap.draw(screen)
            pygame.display.flip()

    def collide_actors(self):
        for actor in self.actors:
            for other in self.actors:
                if actor.rect.centery >= self.tilemap.px_height:
                    actor.kill()
                    if isinstance(actor, Player): post_event(PLAYER_DIED) 
                if actor == other: continue
                if actor.rect.colliderect(other.rect):
                    actor.on_collide_actor(other)

    def collide_blocks(self, actor, dx, dy):
        dx = int(dx)  # Avoid rounding error
        dy = int(dy)

        last = actor.rect.copy()
        new = actor.rect
 
        new.x += dx
        collided = self.blocks.collide(new, 'type')
        for block in collided:
            if dx > 0:
                new.right = block.left
            if dx < 0:
                new.left = block.right

            if isinstance(actor, Enemy):
                actor.direction *= -1

                if actor.state == actor.bSpin:
                    # spinning enemies break blocks
                    self.hit_block(block)

        new.y += dy
        actor.resting = False
        collided = self.blocks.collide(new, 'type')
        for block in collided:
            if dy > 0:
                new.bottom = block.top
                actor.resting = True
                actor.dy = 0
                if isinstance(actor, Enemy):
                    self.blocks_under_enemies.append((block.index, actor))
            if dy < 0:
                new.top = block.bottom
                actor.dy = 0

                if isinstance(actor, Player):
                    self.hit_block(block, True)

    def collide_coins(self, player):
        coins = self.things.collide(player.rect, 'coin')

        player.coins += len(coins)
        for cell in coins:
            post_event(COIN_PICKUP)
            self.things.remove_cell(cell.index)

    def hit_block(self, block, byplayer=False):
        if block['type'] == 'breakable':
            post_event(BLOCK_BROKEN, block=block.index, byplayer=byplayer)

        elif block['type'] == 'with_coins':
            post_event(BLOCK_HIT, block=block.index)
            block['hits'] -= 1
            self.player.coins += 1
            post_event(COIN_PICKUP)

            if block['hits'] <= 0:
                self.blocks[block.index] = self.exhausted_tile


def game(screen):
    levels = ['map', 'map1']
    score = 0
    for mapname in levels:
        log.info("Game: starting new level \'%s\'" % mapname)
        msg = Level().run(screen, mapname, score)
        if msg['reason'] == pygame.QUIT:
            return
        if msg['reason'] == PLAYER_DIED:
            print 'GAME OVER'
            print 'Your score: %d' % msg['score']
            return
        if msg['reason'] == EXIT_LEVEL:
            score = msg['score']
            continue
    print 'End of the game'
    print 'Your score: %d' % score


if __name__ == '__main__':
    level = log.INFO
    if len(sys.argv) > 1:
        level = getattr(log, sys.argv[1].upper())
    log.basicConfig(level=level, format='%(levelname)s:%(message)s')

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    game(screen)
