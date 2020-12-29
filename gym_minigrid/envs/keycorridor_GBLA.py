from gym_minigrid.roomgrid import RoomGrid
from gym_minigrid.register import register
from enum import IntEnum

class KeyCorridorGBLA(RoomGrid):
    """
    The door-key-object domain for Goal biased learning Agenda
    """
    class roomDescriptor(IntEnum):
        doesntExist = 0
        noDoor = 1
        unLockedDoor = 2
        lockedWithKeyInVaunt = 3
        lockedWithKeyInHallway = 4
        # Drop an object


    def __init__(
        self,
        taskD,
    ):
        self.taskD = taskD
        self.obj_type = "ball"

        self.roomID = {
            1: {
                1: 'delivery',
                2 : 0,
                3 : 1,
                4 : 2,
            },
            2: {
                1: 'keyVault',
                2: 3,
                3: 4,
                4: 5,
            }
        }

        self.roomLoc = {
            'delivery': (1, 1),
            'keyVault': (2, 1),
            0: (1,2),
            1: (1,3),
            2: (1,4),
            3: (2,2),
            4: (2,3),
            5: (2,4),
        }

        super().__init__(
            room_size=taskD.roomSize,
            num_rows=4,
            num_cols=6,
            max_steps=30*taskD.roomSize**2, # may need to be updated
        )


        print("initialized GBLA Door Key Domain")

    def add_passage(self, room):
        l = self.roomLoc[room]
        if room in ['delivery', 0, 1, 2]:
            self.remove_wall(l[1], l[0], 3)
        else:
            self.remove_wall(l[1], l[0], 1)

    def _gen_grid(self, width, height):
        super()._gen_grid(width, height)

        # Connect the outside rooms into a hallway by removing the walls
        for i in range(0, self.num_rows):
            for j in range(0, self.num_cols):
                if (i == 0 or i == self.num_rows - 1) and j < self.num_cols - 1:
                    self.remove_wall(j, i, 0)
                if (j == 0 or j == self.num_cols - 1) and i < self.num_rows - 1:
                    self.remove_wall(j, i, 1)


        for room in ['delivery', 'keyVault']:
            self.add_passage(room)

        # Add doors/passages to every room  
        # Add keys to locked doors
        for room in range(6):

            room_x = self.roomLoc[room][0]
            room_y = self.roomLoc[room][1]

            if self.roomLoc[room][0] == 1:
                door_idx = 3 # top wall
            else:
                door_idx = 1 # bottom wall

            addLock = self.taskD.roomDescriptor[room] >= 3
            addDoor =  self.taskD.roomDescriptor[room] >= 2

            if addDoor:
                door, _ = self.add_door(room_y, room_x, door_idx, locked=addLock)

                if addLock:
                    if self.taskD.roomDescriptor[room] == self.roomDescriptor.lockedWithKeyInHallway or self.taskD.roomSize == 3:
                        # Add a key in a random room on the left side
                        self.add_object(0, self._rand_int(0, self.num_rows), 'key', door.color)
                    else:
                        # place key in vault
                        self.add_object(1, 2, 'key', door.color)
            
            if self.taskD.roomDescriptor[room] == self.roomDescriptor.noDoor:
                self.add_passage(room)

        
        # Add two object in the rooms
        self.obj = []
        #while(len(self.obj) < 3):
        if self.taskD.roomSize > 3:
            loc = self._rand_int(0, 6)
            if self.taskD.roomDescriptor[loc] > 0:
                obj, _ = self.add_object(self.roomLoc[loc][1], self.roomLoc[loc][0], kind=self.obj_type)
                self.obj.append(obj)

        else:
            obj, _ = self.add_object(self._rand_int(1, self.num_cols), 0, kind=self.obj_type)
            self.obj.append(obj)

        # Place the agent in the middle
        self.place_agent(0, self.num_rows // 2)

        # Make sure all rooms are accessible
        #self.connect_all()
        self.mission = "" #"pick up the %s %s" % (obj.color, obj.type)

    def step(self, action):
        obs, reward, done, info = super().step(action)

        if action == self.actions.pickup:
            if self.carrying and self.carrying in self.obj:
                reward = self._reward()
                done = True

        return obs, reward, done, info

register(
    id='MiniGrid-KeyCorridorGBLA-v0',
    entry_point='gym_minigrid.envs:KeyCorridorGBLA'
    
)
