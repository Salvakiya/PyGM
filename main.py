import pygame
import sys, time
from PyGM.master import *


def load_image(name):
    image = pygame.image.load(name)
    return image

class Sprite(pygame.sprite.Sprite):
    def __init__(self):
        super(Sprite, self).__init__()
        self.images = []
        self.images.append(load_image('assets/stand1_0.png'))
        self.images.append(load_image('assets/stand1_1.png'))
        self.images.append(load_image('assets/stand1_2.png'))
        self.images.append(load_image('assets/stand1_3.png'))

        self.index = 0
        self.image = self.images[self.index]
        self.rect = pygame.Rect(5, 5, 62, 75)

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

pygame.display.init()
screen = pygame.display.set_mode((320, 240))

sprite = Sprite()
group = pygame.sprite.Group(sprite)

FPS = 60
frames = FPS / 12
clock = pygame.time.Clock()

running = True
pygame.display.set_caption("PY-GM")
frame_id = 1

next_frame = time.time()


class GameTimer(Entity):
    def __init__(self, **kw):
        super(GameTimer, self).__init__(**kw)
        self.alarm = {"print_complete": 200, "end_game": 20000}

    def print_complete(self):
        print "Completed!"

    def end_game(self):
        global running
        running = False
        print "game ended"

    def event_step(self):
        super(GameTimer, self).event_step()
        print self.alarm


class Tree(Entity):
    def __init__(self, **kw):
        super(Tree, self).__init__(**kw)
        self.alarm = {"sayhi" : 500}

    def sayhi(self):
        print "hi"

    def event_step(self):
        super(Tree, self).event_step()


NewGameRoom()
NewGameRoom.add_object(0, 0, GameTimer)
NewGameRoom.add_object(0, 0, Tree)

obj = NewGameRoom.object_index(1)

#NewGameRoom.instance_destroy(NewGameRoom.type_nearest(100, 0, Tree))

while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (keys[pygame.K_ESCAPE]):
            running = False
        if keys[pygame.K_UP]:
            obj.sayhi()

    #make all objects in world preform step event
    NewGameRoom.room_step()

    clock.tick(frames)

    group.update()
    group.draw(screen)

    pygame.display.flip()

