import pygame
import os


def load_spritesheet(file, framesize):
    if type(framesize) == int:
        fw, fh = framesize, framesize
    else:
        fw, fh = framesize

    img = pygame.image.load(file)
    spritesheet = []
    width, height = img.get_size()
    rows = height / fh
    cols = width / fw
    for row in xrange(rows):
        for col in xrange(cols):
            r = (col * fw, row * fh, fw, fh)
            spritesheet.append(img.subsurface(r))
    return spritesheet


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super(AnimatedSprite, self).__init__(*groups)
        self._sheet = None
        self.image_index = 0
        self.interval = 0
        self._counter = 0

    @property
    def sheet(self):
        return self._sheet

    @sheet.setter
    def sheet(self, sh):
        try:
            iter(sh)
        except TypeError:
            print 'A spritesheet must by iterable'
        if sh == self._sheet: return
        self._sheet = sh
        self._counter = 0
        self.image_index = 0
        self.image = self._sheet[self.image_index]

    def update_animation(self, dt):
        self._counter += dt
        if self._counter >= self.interval:
            self.image_index = (self.image_index + 1) % len(self._sheet)
            self.image = self.sheet[self.image_index]
            self._counter -= self.interval


def test():
    load = pygame.image.load
    framenum = 9
    spritesheet = load_spritesheet(os.path.join('test', 'test-spritesheet.png'), 8)
    sprites = list((load(os.path.join('test', 'test-spritesheet_%d.png' % i)) 
                    for i in xrange(framenum)))
    for i in xrange(framenum):
        from_sheet = spritesheet[i].get_at((0, 0))
        from_sprites = sprites[i].get_at((0, 0))
        print repr(from_sprites) + ' -- ' + repr(from_sheet)
        assert from_sprites == from_sheet
    print "Passed"


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    test()
