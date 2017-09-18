
GRAVITY = 50
MAXFALL = 400
class Actor(object):
    def __init__(self, sprite, group):
        self.group = group
        group.append(self)
        self.sprite = sprite

    def kill(self):
        self.group.del_obj(self)
        self.sprite.kill()

    def update(self):
        raise NotImplementedError

    def on_collide_actor(self):
        raise NotImplementedError


class Enemy(Actor):
    # behaviours
    bWalk = 0
    bHide = 1
    bSpin = 2
    
    def __init__(self, sprite, group):
        super(Enemy, self).__init__(sprite, group)
        self.dy = 0
        self.dx = 0
        self.resting = False
        self.direction = 1
        self.state = self.bWalk

    def stomp(self):
        self.kill()

    def killit(self):
        self.kill()
        