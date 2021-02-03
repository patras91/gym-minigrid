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
        if self.achieved(*self.goalArgs):
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

    def pickupObj(env):
        return env.carrying and env.carrying in env.obj

    g_searchKey = GoalDescriptor('searchKey', (), (), 1/12, func=pickupObj)
    g_pickupKey = GoalDescriptor('pickupKey', (), (), 1/12, func=pickupObj)
    g_hasKey = GoalDescriptor('hasKey', (), (), 1/6, func=pickupObj, refinement=(g_searchKey, g_pickupKey))

    g_openDoor = GoalDescriptor('openDoor', (), (), 1/12, func=pickupObj)
    g_passDoor = GoalDescriptor('passDoor', (), (), 1/12, func=pickupObj)
    g_goToRoom = GoalDescriptor('goToRoom', (env.obj), (), 1/6, func=pickupObj, refinement=(g_openDoor, g_passDoor))

    g_getNear = GoalDescriptor('getNear', (env.obj), (), 1/3, func=pickupObj, refinement=(g_hasKey, g_goToRoom))

    g_pickupObj = GoalDescriptor('pickupObj', (env), (env.obj), 1/3, func=pickupObj)

    g_goToRoom = GoalDescriptor('GoToRoom', (), (), 1/6, func=pickupObj)
    g_putDown = GoalDescriptor('putDown', (env.obj), (), 1/6, func=pickupObj)
    g_deliver = GoalDescriptor('deliver', (env.obj), (), 1/3, func=pickupObj, refinement=(g_goToRoom, g_putDown))

    g_dropOff = GoalDescriptor('dropOff', (env.obj), (), 1, func=pickupObj, refinement=(g_getNear, g_pickupObj, g_deliver))

    return g_dropOff


# Unit Test

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










