from gym_minigrid.roomgrid import RoomGrid
from gym_minigrid.register import register

class KeyCorridorGBLA(RoomGrid):
    """
    The door-key-object domain for Goal biased learning Agenda
    """

    def __init__(
        self,
        taskD,
    ):

        super().__init__(
            room_size=6,
            num_rows=4,
            num_cols=6,
            max_steps=30*6**2, # may need to be updated
            seed=taskD.seed,
        )

        self.taskD = taskD
        self.seed = taskD.seed

        print("initialized GBLA Door Key Object")

    def _gen_grid(self, width, height):
        super()._gen_grid(width, height)

        # Connect the outside rooms into a hallway by removing the walls
        for i in range(0, self.num_rows):
            for j in range(0, self.num_cols):
                if (i == 0 or i == self.num_rows - 1) and j < self.num_cols - 1:
                    self.remove_wall(j, i, 0)
                if (j == 0 or j == self.num_cols - 1) and i < self.num_rows - 1:
                    self.remove_wall(j, i, 1)

        # Add doors to every room
        for room_i in range(1, self.num_rows - 1):
            for room_j in range(1, self.num_cols - 1):
                if room_i == 1:
                    door_idx = 3
                else:
                    door_idx = 1
                door, _ = self.add_door(room_j, room_i, door_idx, locked=True)
                # Add a key in a random room on the left side
                self.add_object(0, self._rand_int(0, self.num_rows), 'key', door.color)

        # Add an object behind the locked door
        #obj, _ = self.add_object(2, room_idx, kind=self.obj_type)

        
        
        # Place the agent in the middle
        self.place_agent(0, self.num_rows // 2)

        # Make sure all rooms are accessible
        #self.connect_all()

        #self.obj = obj
        self.mission = "" #"pick up the %s %s" % (obj.color, obj.type)

    def step(self, action):
        obs, reward, done, info = super().step(action)

        if action == self.actions.pickup:
            if self.carrying and self.carrying == self.obj:
                reward = self._reward()
                done = True

        return obs, reward, done, info

register(
    id='MiniGrid-KeyCorridorGBLA-v0',
    entry_point='gym_minigrid.envs:KeyCorridorGBLA'
    
)
