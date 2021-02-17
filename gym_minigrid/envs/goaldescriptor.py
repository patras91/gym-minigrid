__author__ = "patras"

class GoalDescriptor():
    def __init__(self, gid, params, value, r, func=None, refinement=None):
        self.goalId = gid
        self.goalArgs = params # params include arguments and values
        self.goalValue = value
        self.reward = r
        self.refinement = refinement
        self.achieved = func

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

def GetGoalDescriptor(env): 
    '''
        Returns the goal hierarchy and rewards for the minigrid environment
    '''

    dropOff_room = env.get_room(0,0) # temporary

    g_searchKey = GoalDescriptor('searchKey', (env), (), 1/12, func=searchKey)
    g_pickupKey = GoalDescriptor('pickupKey', (env), (), 1/12, func=pickupKey)
    g_hasKey = GoalDescriptor('hasKey', (env), (), 1/6, func=pickupKey, refinement=(g_searchKey, g_pickupKey))

    g_openDoor = GoalDescriptor('openDoor', (env), (env.object_room), 1/12, func=openDoor)
    g_passDoor = GoalDescriptor('passDoor', (env), (env.object_room), 1/12, func=goToRoom)
    g_goToRoom1 = GoalDescriptor('goToRoom', (env), (env.object_room), 1/6, func=goToRoom, refinement=(g_openDoor, g_passDoor))

    g_getNear = GoalDescriptor('getNear', (env), (env.object_room), 1/3, func=goToRoom, refinement=(g_hasKey, g_goToRoom1))

    g_pickupObj = GoalDescriptor('pickupObj', (env), (), 1/3, func=pickupObj)

    g_goToRoom2 = GoalDescriptor('goToRoom', (env), (dropOff_room), 1/6, func=goToRoom)
    g_putDown = GoalDescriptor('putDown', (env), (), 1/6, func=putDown)
    g_deliver = GoalDescriptor('deliver', (env), (dropOff_room), 1/3, func=dropOff, refinement=(g_goToRoom2, g_putDown))

    g_dropOff = GoalDescriptor('dropOff', (env), (dropOff_room), 1, func=dropOff, refinement=(g_getNear, g_pickupObj, g_deliver))

    return g_passDoor

### NOTE: these functions have to be global in scope for multi-processing to work
###       multi-processing requires pickling and pickling needs to recreate the function from a global reference

def searchKey(env, v):
    # the position the agent is facing
    fwd_pos = env.front_pos

    # Get the contents of the cell in front of the agent
    fwd_cell = env.grid.get(*fwd_pos)

    return fwd_cell and fwd_cell.type == "key"

def pickupKey(env, v):
    return env.carrying and env.carrying.type == "key"

def openDoor(env, room):
    for door in room.doors:
        if door:
            return door.is_open
    return True

def goToRoom(env, room):
    return room.pos_inside(*env.agent_pos)

def pickupObj(env, v):
    return env.carrying and env.carrying in env.obj

def putDown(env, v): # should not get reward for putdown if it has never picked up anything
    return env.carrying == None

def dropOff(env, room):
    for item in env.obj:
        if not room.pos_inside(*item.cur_pos):
            return False
    return True



# Unit Tests

# g = GoalDescriptor('dropOff', ('o', 'l'), 10, func=dropOff, refinement=(gGetKey, gFindObj, gDeliver))

# print("Reward for DropOff: ", g.GetReward(s))

# class KeyCorridor(): # Placeholder before merging with the KeyCorridorGBLA environment
#     def __init__(self):
#         self.loc = {'key': 'r1', 'r1': 'hallway', 'o': 'UNK'}
#         self.pos = {'o': 'UNK'}

# def hasKey(s):
#     return s.loc['key'] == 'r1'

# gGetKey = GoalDescriptor('getKey', ('k'), 3, func=hasKey) # no refinement

# s = KeyCorridor() # a placeholder for Unit Testing
# print("Reward for GetKey: ", gGetKey.GetReward(s))

# def search(s):
#     return s.loc['o'] != "UNK"

# gSearch = GoalDescriptor('search', ('r', 'o'), 4, func=search) # no refinement
# print("Reward for Search: ", gSearch.GetReward(s))

# def collect(s):
#     return s.pos['o'] == "r1"

# gCollect = GoalDescriptor('search', ('r', 'o'), 4, func=collect) # no refinement
# print("Reward for Collect: ", gSearch.GetReward(s))

# gFindObj = GoalDescriptor('findObj', ('o'), 5, func=collect, refinement=(gSearch, gCollect)) 
# print("Reward for Find: ", gFindObj.GetReward(s))

# def dropOff(s):
#     return s.loc['o'] == 'dropOffRoom'

# gDeliver = GoalDescriptor('deliver', ('o'), 2, func=dropOff)  # no refinement
# print("Reward for deliver: ", gDeliver.GetReward(s))










