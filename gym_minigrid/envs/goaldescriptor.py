__author__ = "patras"

import numpy as np

class GoalDescriptor():
    def __init__(self, gid, params, value, r, achieved_func=None, failure_func=None, refinement=None):
        self.goalId = gid
        self.goalArgs = params # params include arguments and values
        self.goalValue = value
        self.reward = r
        self.refinement = refinement
        self.achieved = achieved_func
        self.failure = failure_func

    def GetReward(self):
        if self.achieved == None:
            return 0
        if self.achieved(self.goalArgs, self.goalValue):
            return self.reward
        else:
            # search recursively the refinement how further along you are and reward accordingly
            if self.refinement == None:
                return 0
            
            r = 0
            for item in self.refinement:
                r += item.GetReward()
            return r

    def __repr__(self):             # modifying the __repr__ function so we know what goal it is from looking at it
        s = super().__repr__()      # get the standard __repr__ results
                                    # append the goalId to the beginning and return
        return '<' + self.goalId + ' ' + s[1:]

def GetGoalDescriptor(env): 
    '''
        Returns the goal hierarchy and rewards for the minigrid environment
    '''

    dropOff_room = env.get_room(0,0) # temporary

    g_searchKey = GoalDescriptor('searchKey', (env), (), 1, achieved_func=a_searchKey)
    g_pickupKey = GoalDescriptor('pickupKey', (env), (), 1, achieved_func=a_pickupKey, failure_func=f_pickupKey)
    g_hasKey = GoalDescriptor('hasKey', (env), (), 1, achieved_func=a_pickupKey, refinement=(g_searchKey, g_pickupKey))

    g_findDoor = GoalDescriptor('findDoor', (env), (env.object_room), 1, achieved_func=a_findDoor, failure_func=f_hasKey)
    g_passDoor = GoalDescriptor('passDoor', (env), (env.object_room), 1, achieved_func=a_goToRoom, failure_func=f_passDoor)
    g_goToRoom1 = GoalDescriptor('goToRoom', (env), (env.object_room), 1, achieved_func=a_goToRoom, refinement=(g_findDoor, g_passDoor))

    g_getNear = GoalDescriptor('getNear', (env), (env.object_room), 1, achieved_func=a_goToRoom, refinement=(g_hasKey, g_goToRoom1))

    g_pickupObj = GoalDescriptor('pickupObj', (env), (), 1, achieved_func=a_pickupObj, failure_func=f_pickupObj)

    g_goToRoom2 = GoalDescriptor('goToDropoff', (env), (dropOff_room), 1, achieved_func=a_goToDropoff, failure_func=f_hasBall)
    g_putDown = GoalDescriptor('putDown', (env), (), 1, achieved_func=a_putDown)
    g_deliver = GoalDescriptor('deliver', (env), (dropOff_room), 1, achieved_func=a_dropOff, refinement=(g_goToRoom2, g_putDown))

    g_dropOff = GoalDescriptor('dropOff', (env), (dropOff_room), 1, achieved_func=a_dropOff, refinement=(g_getNear, g_pickupObj, g_deliver))

    return g_dropOff

### NOTE: these functions have to be global in scope for multi-processing to work
###       multi-processing requires pickling and pickling needs to recreate the function from a global reference

##### searchKey goal #####

def a_searchKey(env, v):
    # the position the agent is facing
    fwd_pos = env.front_pos

    # Get the contents of the cell in front of the agent
    fwd_cell = env.grid.get(*fwd_pos)

    return fwd_cell and fwd_cell.type == "key"

##### pickupKey goal #####

def a_pickupKey(env, v):
    return env.carrying and env.carrying.type == "key"

def f_pickupKey(env):
    ds = [-1,0,1]
    obj_sur = [env.grid.get(env.agent_pos[0]+dx,env.agent_pos[1]+dy)
                            for dx in ds for dy in ds
                            if not (dx == 0 and dy == 0)]
    return all([o.type != "key" if o else True  for o in obj_sur])

##### passDoor goal #####

def f_passDoor(env):
    ds = [-1,0,1]
    obj_sur = [env.grid.get(env.agent_pos[0]+dx,env.agent_pos[1]+dy)
                            for dx in ds for dy in ds
                            if not (dx == 0 and dy == 0)]
    doors = [o for o in obj_sur if o and o.type == "door"]

    if doors:
        return doors[0].is_locked and not (env.carrying and env.carrying.type=="key")
    else:
        return True
    return

##### findDoor goal #####

def a_findDoor(env, v):
    for door in env.object_room.doors:
        if door:
            return sum(np.abs(np.array(door.cur_pos)-env.agent_pos))<=1
    return True

def f_hasKey(env):
    return not (env.carrying and env.carrying.type == "key")

##### goToRoom goal #####

def a_goToDropoff(env, v):
    return env.get_room(0,0).pos_inside(*env.agent_pos)

def f_hasBall(env):
    return not (env.carrying and env.carrying.type == "ball")

##### pickupObj goal #####

def a_pickupObj(env, v):
    return env.carrying and \
           any([(o.type == env.carrying.type) and
            (o.color == env.carrying.color) for o in env.obj])

def f_pickupObj(env):
    return not env.object_room.pos_inside(*env.agent_pos)

##### putDown goal #####

def a_putDown(env, v): # should not get reward for putdown if it has never picked up anything
    return env.carrying == None

##### dropOff goal #####

def a_dropOff(env, room):
    for item in env.obj:
        if not room.pos_inside(*item.cur_pos):
            return False
    return True



# Unit Tests

# g = GoalDescriptor('dropOff', ('o', 'l'), 10, achieved_func=dropOff, refinement=(gGetKey, gFindObj, gDeliver))

# print("Reward for DropOff: ", g.GetReward(s))

# class KeyCorridor(): # Placeholder before merging with the KeyCorridorGBLA environment
#     def __init__(self):
#         self.loc = {'key': 'r1', 'r1': 'hallway', 'o': 'UNK'}
#         self.pos = {'o': 'UNK'}

# def hasKey(s):
#     return s.loc['key'] == 'r1'

# gGetKey = GoalDescriptor('getKey', ('k'), 3, achieved_func=hasKey) # no refinement

# s = KeyCorridor() # a placeholder for Unit Testing
# print("Reward for GetKey: ", gGetKey.GetReward(s))

# def search(s):
#     return s.loc['o'] != "UNK"

# gSearch = GoalDescriptor('search', ('r', 'o'), 4, achieved_func=search) # no refinement
# print("Reward for Search: ", gSearch.GetReward(s))

# def collect(s):
#     return s.pos['o'] == "r1"

# gCollect = GoalDescriptor('search', ('r', 'o'), 4, achieved_func=collect) # no refinement
# print("Reward for Collect: ", gSearch.GetReward(s))

# gFindObj = GoalDescriptor('findObj', ('o'), 5, achieved_func=collect, refinement=(gSearch, gCollect))
# print("Reward for Find: ", gFindObj.GetReward(s))

# def dropOff(s):
#     return s.loc['o'] == 'dropOffRoom'

# gDeliver = GoalDescriptor('deliver', ('o'), 2, achieved_func=dropOff)  # no refinement
# print("Reward for deliver: ", gDeliver.GetReward(s))










