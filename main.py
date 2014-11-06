from math import *
import os
#from Constants import *
import pygame, time


pygame.display.init()
screen = pygame.display.set_mode((320, 240))
running = True
pygame.display.set_caption("PY-GM")
frame_id = 1

next_frame = time.time()


class Object(object):
    def __init__(self, x=0, y=0, myid=-1, type_id=-1):
        #self.create(x, y, myid, type_id)
        self.x = x
        self.y = y
        self.myid = myid
        self.type_id = type_id
        self.is_destroyed = False
        self.deactivated_id = -1

        self.alarm_dict = {}

    #def create(self, x=0, y=0, myid=-1, type_id=-1):
    def is_activated(self):
        return self.deactivated_id == -1

    def destroy(self):
        self.is_destroyed = True

    def event_step(self):

        #alarm stuff
        if len(self.alarm_dict) > 0:
            kill = []
            for alarm in self.alarm_dict:
                self.alarm_dict[alarm] -= 1
                if self.alarm_dict[alarm] < 0:
                    #dynamic alarms. Alarms names are actually method names
                    if hasattr(self, alarm):
                        perform = getattr(self, alarm)
                        perform()
                    kill.append(alarm)
            for alarm in kill:
                self.alarm_dict.pop(alarm)


    def event_draw(self):
        pass


class GameTimer(Object):
    def __init__(self, **kw):
        super(GameTimer, self).__init__(**kw)
        self.alarm_dict = {"print_complete": 100, "end_game": 500}

    def print_complete(self):
        print "Completed!"

    def end_game(self):
        global running
        running = False
        print "game ended"

    def event_step(self):
        super(GameTimer, self).event_step()
        print self.alarm_dict


class Tree(Object):
    def __init__(self, **kw):
        super(Tree, self).__init__(**kw)

    def sayhi(self):
        print "hi"


class PyMakerWorld:
    def __init__(self):
        self.object_list = []
        self.object_deactivated_list = []
        self.object_type_dict = {}

    def world_step(self):
        for obj in self.object_list:
            if obj is not None:
                obj.event_step()

    def deactivate_object(self, object_id):
        if not isinstance(object_id, Object):
            object_id = self.object_index(object_id)
            object_id.deactivated_id = len(self.object_deactivated_list)
            self.object_deactivated_list.append(object_id)

    def activate_object(self):
        pass

    def add_object_type_list(self, name):
        if not name.__name__ in self.object_type_dict:
            #create the list
            self.object_type_dict[name.__name__] = []

            #iterate through all objects to add to the list
            for obj in self.object_list:
                if obj.__class__.__name__ == name.__name__:
                    obj.type_id = len(self.object_type_dict[name.__name__])
                    self.object_type_dict[name.__name__].append(obj.myid)

    def add_object(self, x, y, obj):
        #find the id to assign to object
        assign_id = len(self.object_list)
        assign_type_id = -1

        #we only will add our type if this object requires such a thing
        #this is for performance issues that may come later on.
        #a "tree" or "rock" may not need to be iterated through for calculations
        if obj.__name__ in self.object_type_dict:
            #we tell the type list where to find us in the object_list
            self.object_type_dict[obj.__name__].append(assign_id)

            #find the type id or sub id
            assign_type_id = len(self.object_type_dict[obj.__name__])

        #finally we create the object
        self.object_list.append(obj(x=x, y=y, myid=assign_id, type_id=assign_type_id))

    def object_nearest(self, x, y):
        tracking_distance = -1
        object_id = -1
        for obj in self.object_list:
            if obj is not None:
                distance = sqrt((x-obj.x)**2+(y-obj.y)**2)
                if tracking_distance == -1 or distance < tracking_distance:
                    tracking_distance = distance
                    object_id = obj.myid
        return object_id

    def type_nearest(self, x, y, mtype):
        #if we have not iterated through this type
        #we must create the list for this type
        if not mtype.__name__ in self.object_type_dict:
            self.add_object_type_list(mtype)

        tracking_distance = -1
        object_id = -1
        for value in self.object_type_dict[mtype.__name__]:
            #remember object_index(id) references the object_list
            obj = self.object_index(value)
            distance = sqrt((x-obj.x)**2+(y-obj.y)**2)
            if tracking_distance == -1 or distance < tracking_distance:
                tracking_distance = distance
                object_id = obj.myid
        return object_id

    def object_index(self, position):
        #CAUTION! Should be used carefully.
        #if not used properly you could
        #leave an object in the room without
        #being freeing it when it should be
        #freed
        if position != -1:
            return self.object_list[position]

    def destroy(self, destroyid):
        #if we are given an instance instead of an id
        #we will find the id to delete
        if isinstance(destroyid, Object):
            destroyid = destroyid.myid

        kill = self.object_list[destroyid]
        kill.destroy()

        if kill.__class__.__name__ in self.object_type_dict:
            #if killing this instance will delete the list
            if len(self.object_type_dict[kill.__class__.__name__]) <= 1:
                self.object_type_dict.pop(kill.__class__.__name__)
            else:
                #if there will be remaining objects we wont delete the list but remove the entry.
                self.object_type_dict[kill.__class__.__name__].pop(kill.type_id-1)

        self.object_list[destroyid] = None


World = PyMakerWorld()
#World.add_object(0, 0, GameTimer)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    #make all objects in world preform step event
    World.world_step()



    pygame.display.flip()
#for key, value in dictt.iteritems():
#    if value == "Tree":
#        print key


##explanation
