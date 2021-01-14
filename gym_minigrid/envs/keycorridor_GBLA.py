from gym_minigrid.roomgrid import RoomGrid, Room
from gym_minigrid.register import register
from enum import IntEnum

from ..minigrid import *

class RoomGBLA(Room):
    def __init__(
        self,
        top,
        size
    ):
        # Top-left corner and size (tuples)
        self.top = top
        self.size = size

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
        """
        This is the initialization function for the RoomDescriptor object.

        @param taskD:
        """
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
            num_rows=taskD.envD.shape[0],
            num_cols=taskD.envD.shape[1],
            max_steps=30*taskD.roomSize**2, # may need to be updated
        )


        print("initialized GBLA Door Key Domain")

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
                roomType, doorLocs = self.parseDescriptor(self.taskD.envD[j, i])

                room = RoomGBLA(
                    (i * (self.room_size-1), j * (self.room_size-1)),
                    (self.room_size, self.room_size)
                )
                row.append(room)

                # Generate the walls for this room
                if roomType > 0:
                    self.grid.wall_rect(*room.top, *room.size)

            self.room_grid.append(row)

        # The agent starts in the middle, facing right
        self.agent_pos = (
            (self.num_cols // 2) * (self.room_size-1) + (self.room_size // 2),
            (self.num_rows // 2) * (self.room_size-1) + (self.room_size // 2)
        )
        self.agent_dir = 0

        # For each row of rooms
        for j in range(0, self.num_rows):
            # For each column of rooms
            for i in range(0, self.num_cols):
                roomType, (doorNorth, doorEast, doorSouth, doorWest) = \
                                    self.parseDescriptor(self.taskD.envD[j, i])
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
            self.add_object(self._rand_int(0, self.num_cols), self._rand_int(0, self.num_rows), 'key', doorColor)

    def _gen_grid_old(self, width, height):
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

        # Place the agent in the middle
        self.place_agent(0, self.num_rows // 2)

        # Add two object in the rooms
        self.obj = []
        #while(len(self.obj) < 3):
        if self.taskD.roomSize >= 3:
            loc = self._rand_int(0, 6)
            assert any(rd > 0 for rd in self.taskD.roomDescriptor)      # make sure that at least one room is open
            while self.taskD.roomDescriptor[loc] == 0:                  # while you have chosen a blocked room
                loc = self._rand_int(0,6)                               # reroll the room location
            obj, _ = self.add_object(self.roomLoc[loc][1], self.roomLoc[loc][0], kind=self.obj_type)
            self.obj.append(obj)

        else:
            obj, _ = self.add_object(self._rand_int(1, self.num_cols), 0, kind=self.obj_type)
            self.obj.append(obj)

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
