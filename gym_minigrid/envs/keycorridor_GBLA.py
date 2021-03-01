__authors__="sunandita, mark"
''' Last updated: 
        Sunandita: Feb 8, 2021
        Mark: Jan 31, 2021
'''

from gym_minigrid.roomgrid import RoomGrid, Room
from gym_minigrid.register import register
from enum import IntEnum
from random import choice
from gym_minigrid.envs.goaldescriptor import GetGoalDescriptor

from ..minigrid import *

from copy import deepcopy

class RoomGBLA(Room):
    def __init__(
        self,
        top,
        size,
        roomType
    ):
        # Top-left corner and size (tuples)
        self.top = top
        self.size = size
        self.type = roomType

        # List of door objects and door positions
        # Order of the doors is right, down, left, up

        self.doors = [None] * 4
        self.door_pos = [None] * 4


        # List of rooms adjacent to this one
        # Order of the neighbors is right, down, left, up
        self.neighbors = [None] * 4

        # Indicates if this room is behind a locked door
        self.locked = False

        # List of objects contained
        self.objs = []

    def __repr__(self):
        return "room: " + str(self.top) + str(self.size) + str(self.type)

class KeyCorridorGBLA(RoomGrid):
    """
    The door-key-object domain for Goal biased learning Agenda
    """
    class enumRoomDescriptor(IntEnum):
        doesntExist = 0
        noDoor = 1
        unLockedDoor = 2
        lockedWithKeyInVaunt = 3
        lockedWithKeyInHallway = 4
        # Drop an object


    def __init__(
        self,
        taskD,
        goal_id,
        goal_function,
        goal_value,
        goal_reward
    ):
        """
        This is the initialization function for the RoomDescriptor object.

        @param taskD:
        """
        self.envDescriptor = np.array(taskD.envDescriptor)
        self.roomSize = taskD.roomSize
        self.roomDescriptor = taskD.roomDescriptor
        self.obj_type = "ball"

        self.goal_id = goal_id
        self.goal_function = goal_function
        self.goal_value = goal_value
        self.goal_reward = goal_reward

        self.time = 0
        self.termination_set = []

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
            num_rows=taskD.envDescriptor.shape[0],
            num_cols=taskD.envDescriptor.shape[1],
            max_steps=30*taskD.roomSize**2, # may need to be updated
        )

        del(taskD)
        print("initialized GBLA Door Key Domain")

    def set_goal_info(self, goal_function, goal_value, goal):
        gd = GetGoalDescriptor(self)
        self.goalDescriptor = gd
 #       self.goalDescriptor = None
        return None

    def reset(self):
        obs = super().reset()
        self.time = 0
        print('env reset')
        return obs

    def add_passage(self, room):
        l = self.roomLoc[room]
        if room in ['delivery', 0, 1, 2]:
            self.remove_wall(l[1], l[0], 3)
        else:
            self.remove_wall(l[1], l[0], 1)

    def parseDescriptor(self, roomDesc):
        roomType = (roomDesc & int('0000000011', 2))
        doorNorth = (roomDesc & int('0000001100', 2))/4
        doorEast = (roomDesc & int('0000110000', 2))/16
        doorSouth = (roomDesc & int('0011000000', 2))/64
        doorWest = (roomDesc & int('1100000000', 2))/256

        return roomType, (doorNorth, doorEast, doorSouth, doorWest)

    def descriptorDistance(self, roomDesc1, roomDesc2):
        rType1, rDoors1 = self.parseDescriptor(roomDesc1)
        rType2, rDoors2 = self.parseDescriptor(roomDesc2)
        return None

    def _gen_grid(self, width, height):
        # Create the grid

        self.grid = Grid(width, height)
        self.grid.wall_rect(0, 0, width, height)

        self.room_grid = []

        # For each row of rooms
        for j in range(0, self.num_rows):
            row = []

            # For each column of rooms
            for i in range(0, self.num_cols):
                roomType, doorLocs = self.parseDescriptor(self.envDescriptor[j, i])

                room = RoomGBLA(
                    (i * (self.room_size-1), j * (self.room_size-1)),
                    (self.room_size, self.room_size),
                    roomType
                )
                row.append(room)

                # Generate the walls for this room
                if roomType > 0:
                    self.grid.wall_rect(*room.top, *room.size)

            self.room_grid.append(row)

        # Place the agent in the middle
        self.place_agent(0, self.num_rows // 2)

        self.agent_dir = 0

        # For each row of rooms
        for j in range(0, self.num_rows):
            # For each column of rooms
            for i in range(0, self.num_cols):
                roomType, (doorNorth, doorEast, doorSouth, doorWest) = \
                                    self.parseDescriptor(self.envDescriptor[j, i])
                room = self.room_grid[j][i]

                x_l, y_l = (room.top[0] + 1, room.top[1] + 1)
                x_m, y_m = (room.top[0] + room.size[0] - 1, room.top[1] + room.size[1] - 1)

                # Door positions, order is right, down, left, up
                if doorEast:
                    room.neighbors[0] = self.room_grid[j][i+1]
                    room.door_pos[0] = (x_m, self._rand_int(y_l, y_m))

                    self.set_door(doorEast, (i, j), room.door_pos[0])
                if doorSouth:
                    room.neighbors[1] = self.room_grid[j+1][i]
                    room.door_pos[1] = (self._rand_int(x_l, x_m), y_m)

                    self.set_door(doorSouth, (i, j), room.door_pos[1])
                if doorWest:
                    room.neighbors[2] = self.room_grid[j][i-1]
                    room.door_pos[2] = (x_l-1, self._rand_int(y_l, y_m))

                    self.set_door(doorWest, (i,j), room.door_pos[2])
                if doorNorth:
                    room.neighbors[3] = self.room_grid[j-1][i]
                    room.door_pos[3] = (self._rand_int(x_l, x_m), y_l-1)

                    self.set_door(doorNorth, (i,j), room.door_pos[3])


        # Add two object in the rooms
        self.obj = []
        n_obj = 1
        if self.roomSize >= 3:
            while(len(self.obj) < n_obj):
                locs = [(r,c) for r in range(self.num_rows) for c in range(self.num_cols)
                        if self.room_grid[r][c].type>0]
                loc = choice(locs)
                try:
                    obj, _ = self.add_object(loc[1], loc[0], kind=self.obj_type)
                    self.obj.append(obj)
                    # until we integrate with a planner, we need this info for the sub-goals in the goal descriptors
                    self.object_room = self.get_room(loc[1], loc[0])
                except:
                    pass

        else:
            obj, _ = self.add_object(self._rand_int(1, self.num_cols), 0, kind=self.obj_type)
            self.obj.append(obj)

        # Make sure all rooms are accessible
        self.mission = ""  # "pick up the %s %s" % (obj.color, obj.type)

    def set_door(self, doorType, roomLoc, doorLoc):
        if doorType == 0:
            pass
        elif doorType == 1:
            self.grid.set(*doorLoc, None)
        elif doorType == 2:
            self.add_door(*roomLoc, locked=False)
        elif doorType == 3:
            doorColor = self._rand_color()
            self.add_door(*roomLoc, locked=True, color=doorColor)

            n = 0
            while n<100:
                n+=1
                locs = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)
                        if self.room_grid[r][c].type == 0]
                loc = choice(locs)
                try:
                    self.add_object(*loc, 'key', doorColor)
                    n+=100
                except:
                    pass

    def step(self, action):
        obs, reward, done, info = super().step(action)

        self.time += 1

        if self.goal_function and \
                self.goal_function(self, self.goal_value):   # evaluate the goal function passing the env (self) as the
                                                        # arguments and the goal_value as the target value
                                                        # (value = unused at this point)
            reward = self.goal_reward
            done = True                                 # if we meet the reward, end the episode
            self.save_termination_set()
        elif self.goal_id == 'openDoor' and not (self.carrying and self.carrying.type == "key"):
            reward = 0
            done = True
        elif self.goal_id == 'putDown' and not (self.carrying and self.carrying.type == "ball"):
            # if we get here without the ball and the goal_function isn't satisfied
            # we have inadvertently dropped the ball
            reward = 0
            done = True

#        bad_states = [len([k for k in s['grid'].grid + [s['carrying']] if k and k.type == "key"])!=1
#                for s in self.termination_set]
#        if any(bad_states):
#            print('wtf')

#        if len([k for k in self.grid.grid + [self.carrying] if k and k.type == "key"])!=1:
#            print('wtf')

        return obs, reward, done, info

    def save_termination_set(self):
        s = self.get_state()
        self.termination_set.append(s)
        print('reward - termination set size = {}'
              .format(len(self.termination_set)))

    def get_state(self):
        s = {}
        s['carrying'] = deepcopy(self.carrying)
        s['agent_pos'] = deepcopy(self.agent_pos)
        s['agent_dir'] = deepcopy(self.agent_dir)

        s['grid'] = deepcopy(self.grid)
        s['room_grid'] = deepcopy(self.room_grid)
        s['obj'] = deepcopy(self.obj)

#        if len([k for k in s['grid'].grid + [s['carrying']] if k and k.type == "key"])!=1:
#            print('wtf')

        return s

    def set_state(self, s):
        self.carrying = s['carrying']
        self.agent_pos = s['agent_pos']
        self.agent_dir = s['agent_dir']

        self.grid = s['grid']
        self.room_grid = s['room_grid']
        self.obj = s['obj']

#        if len([k for k in self.grid.grid + [self.carrying] if k and k.type == "key"])!=1:
#            print('wtf')

register(
    id='MiniGrid-KeyCorridorGBLA-v0',
    entry_point='gym_minigrid.envs:KeyCorridorGBLA'
    
)

