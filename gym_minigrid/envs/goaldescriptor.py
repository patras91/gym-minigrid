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
        if self.achieved(self.goalArgs):
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

    def placeHolder(env):
        print(env.agent_pos)
        return False

    def searchKey(env):
        # the position the agent is facing
        fwd_pos = env.front_pos

        # Get the contents of the cell in front of the agent
        fwd_cell = env.grid.get(*fwd_pos)

        return fwd_cell and fwd_cell.type == "key"

    def pickupKey(env):
        return env.carrying and env.carrying.type == "key" 

    g_searchKey = GoalDescriptor('searchKey', (env), (), 1/12, func=searchKey)
    g_pickupKey = GoalDescriptor('pickupKey', (env), (), 1/12, func=pickupKey)
    g_hasKey = GoalDescriptor('hasKey', (env), (), 1/6, func=pickupKey, refinement=(g_searchKey, g_pickupKey))


    def openDoor(env):
        pass

    def goToRoom(env):
        print(env.grid.get(*env.agent_pos))

    g_openDoor = GoalDescriptor('openDoor', (env), (), 1/12, func=openDoor)
    g_passDoor = GoalDescriptor('passDoor', (env), (), 1/12, func=placeHolder)
    g_goToRoom = GoalDescriptor('goToRoom', (env), (), 1/6, func=goToRoom, refinement=(g_openDoor, g_passDoor))

    g_getNear = GoalDescriptor('getNear', (env), (), 1/3, func=placeHolder, refinement=(g_hasKey, g_goToRoom))

    def pickupObj(env):
        return env.carrying and env.carrying in env.obj

    g_pickupObj = GoalDescriptor('pickupObj', (env), (), 1/3, func=pickupObj)

    def putDown(env): # should not get reward for putdown if it has never picked up anything
        return env.carrying == None

    g_goToRoom = GoalDescriptor('goToRoom', (env), (), 1/6, func=placeHolder)
    g_putDown = GoalDescriptor('putDown', (env), (), 1/6, func=putDown)
    g_deliver = GoalDescriptor('deliver', (env), (), 1/3, func=placeHolder, refinement=(g_goToRoom, g_putDown))

    g_dropOff = GoalDescriptor('dropOff', (env), (), 1, func=placeHolder, refinement=(g_getNear, g_pickupObj, g_deliver))

    return g_goToRoom


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










