__author__ = "patras"

class GoalDescriptor():
    def __init__(self, gid, params, r, func, refinement=None):
    	self.goalID = gid
    	self.goalParams = params # TODO: set parameter bindings later
    	self.reward = r
    	self.refinement = refinement
    	self.achieved = func

    def GetReward(self, s):
    	if self.achieved(s):
    		return self.reward
    	else:
    		# search recursively the refinement how further along you are and reward accordingly
    		if self.refinement == None:
    			return 0
    		
    		r = 0
    		for item in self.refinement:
    			r += item.GetReward(s)
    		return r

class KeyCorridor(): # Placeholder before merging with the KeyCorridorGBLA environment
	def __init__(self):
		self.loc = {'key': 'r1', 'r1': 'hallway', 'o': 'UNK'}
		self.pos = {'o': 'UNK'}

def hasKey(s):
	return s.loc['key'] == 'r1'

gGetKey = GoalDescriptor('getKey', ('k'), 3, func=hasKey) # no refinement

s = KeyCorridor() # a placeholder for Unit Testing
print("Reward for GetKey: ", gGetKey.GetReward(s))

def search(s):
	return s.loc['o'] != "UNK"

gSearch = GoalDescriptor('search', ('r', 'o'), 4, func=search) # no refinement
print("Reward for Search: ", gSearch.GetReward(s))

def collect(s):
	return s.pos['o'] == "r1"

gCollect = GoalDescriptor('search', ('r', 'o'), 4, func=collect) # no refinement
print("Reward for Collect: ", gSearch.GetReward(s))

gFindObj = GoalDescriptor('findObj', ('o'), 5, func=collect, refinement=(gSearch, gCollect)) 
print("Reward for Find: ", gFindObj.GetReward(s))

def dropOff(s):
	return s.loc['o'] == 'dropOffRoom'

gDeliver = GoalDescriptor('deliver', ('o'), 2, func=dropOff)  # no refinement
print("Reward for deliver: ", gDeliver.GetReward(s))

g = GoalDescriptor('dropOff', ('o'), 10, func=dropOff, refinement=(gGetKey, gFindObj, gDeliver))
print("Reward for DropOff: ", g.GetReward(s))