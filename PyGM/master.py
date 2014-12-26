#Game Maker Object
from math import sqrt


class Entity(object):
    #all game classes inherit this class
    def __init__(self, x=0, y=0, myid=-1, type_id=-1):
        self.x = x
        self.y = y
        self.myid = myid
        self.type_id = type_id
        self.is_destroyed = False
        self.deactivated_id = -1

        self.alarm = {}

    def is_activated(self):
        return self.deactivated_id == -1

    def destroy(self):
        self.is_destroyed = True

    def event_step(self):

        #alarm stuff
        #usage: self.alarm_dictionary["MethodName"] = StepsToComplete
        #does not support arguments at this current time.
        if len(self.alarm) > 0:
            #make a list of alarms which ran out
            alarms_to_remove = []

            for method_alarm in self.alarm:
                #count down the timer
                self.alarm[method_alarm] -= 1

                #if the timer has run out
                if self.alarm[method_alarm] < 0:

                    #dynamic alarms. Alarms names are actually method names
                    if hasattr(self, method_alarm):
                        perform = getattr(self, method_alarm)
                        perform()
                    alarms_to_remove.append(method_alarm)
            for method_alarm in alarms_to_remove:
                self.alarm.pop(method_alarm)

    def event_draw(self):
        pass

class NewGameRoom:
    object_dictionary = {}
    object_type_dict = {}
    object_id_counter = 0

    def __init__(self):
        pass

    @staticmethod
    def room_step():
        for obj in NewGameRoom.object_dictionary.values():
            obj.event_step()

    #this method will create a type list when we actually need it
    #some classes will never get a type list.
    @staticmethod
    def add_object_type_list(name):
        if not name.__name__ in NewGameRoom.object_type_dict:
            #create the list
            NewGameRoom.object_type_dict[name.__name__] = []

            #iterate through all objects to add to the list
            for obj in NewGameRoom.object_dictionary.values():
                if obj.__class__.__name__ == name.__name__:
                    obj.type_id = len(NewGameRoom.object_type_dict[name.__name__])
                    NewGameRoom.object_type_dict[name.__name__].append(obj.myid)

    @staticmethod
    def add_object(x, y, obj):
        #find the id to assign to object
        assign_id = NewGameRoom.object_id_counter
        NewGameRoom.object_id_counter += 1
        assign_type_id = -1

        #we only will add our type if this object requires such a thing
        #this is for performance issues that may come later on.
        #a "tree" or "rock" may not need to be iterated through for calculations
        if obj.__name__ in NewGameRoom.object_type_dict:
            #we tell the type list where to find us in the object_list
            NewGameRoom.object_type_dict[obj.__name__].append(assign_id)

            #find the type id or sub id
            assign_type_id = len(NewGameRoom.object_type_dict[obj.__name__])

        #finally we create the object
        NewGameRoom.object_dictionary[assign_id] = obj(x=x, y=y, myid=assign_id, type_id=assign_type_id)

    @staticmethod
    def object_nearest(x, y):
        tracking_distance = -1
        object_id = -1
        for obj in NewGameRoom.object_dictionary.values():
            distance = sqrt((x-obj.x)**2+(y-obj.y)**2)
            if tracking_distance == -1 or distance < tracking_distance:
                tracking_distance = distance
                object_id = obj.myid
        return object_id

    @staticmethod
    def type_nearest(x, y, mtype):
        #if we have not iterated through this type
        #we must create the list for this type
        if not mtype.__name__ in NewGameRoom.object_type_dict:
            NewGameRoom.add_object_type_list(mtype)

        tracking_distance = -1
        object_id = -1
        for value in NewGameRoom.object_type_dict[mtype.__name__]:
            #remember object_index(id) references the object_list
            obj = NewGameRoom.object_index(value)
            distance = sqrt((x-obj.x)**2+(y-obj.y)**2)
            if tracking_distance == -1 or distance < tracking_distance:
                tracking_distance = distance
                object_id = obj.myid
        return object_id

    @staticmethod
    def object_index(position):
        #CAUTION! Should be used carefully.
        #if not used properly you could
        #leave an object in the room without
        #being freeing it when it should be
        #freed
        if position != -1:
            if position in NewGameRoom.object_dictionary:
                return NewGameRoom.object_dictionary[position]

    @staticmethod
    def instance_destroy(destroy_id):
        #if we are given an instance instead of an id
        #we will find the id to delete
        if isinstance(destroy_id, Entity):
            destroy_id = destroy_id.myid

        instance_to_destroy = NewGameRoom.object_dictionary[destroy_id]
        instance_to_destroy.destroy()

        if instance_to_destroy.__class__.__name__ in NewGameRoom.object_type_dict:
            #if killing this instance will delete the list
            if len(NewGameRoom.object_type_dict[instance_to_destroy.__class__.__name__]) <= 1:
                NewGameRoom.object_type_dict.pop(instance_to_destroy.__class__.__name__)
            else:
                #if there will be remaining objects we wont delete the list but remove the entry.
                NewGameRoom.object_type_dict[instance_to_destroy.__class__.__name__].pop(instance_to_destroy.type_id)

        NewGameRoom.object_dictionary.pop(destroy_id)