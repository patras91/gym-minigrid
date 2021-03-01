#!/usr/bin/env python3

import time
import argparse
import numpy as np
import gym
import gym_minigrid
from gym_minigrid.wrappers import *
from gym_minigrid.window import Window
import gym_minigrid.envs.goaldescriptor

def redraw(img):
    if not args.agent_view:
        img = env.render('rgb_array', tile_size=args.tile_size)

    window.show_img(img)

def reset():
    if args.seed != -1:
        env.seed(args.seed)

    obs = env.reset()

    if hasattr(env, 'mission'):
        print('Mission: %s' % env.mission)
        window.set_caption(env.mission)

    redraw(obs)

def step(action):
    obs, reward, done, info = env.step(action)
    print('step=%s, reward=%.2f' % (env.step_count, reward))

    if done:
        print('done!')
        reset()
    else:
        redraw(obs)

def key_handler(event):
    print('pressed', event.key)

    if event.key == 'escape':
        window.close()
        return

    if event.key == 'backspace':
        reset()
        return

    if event.key == 'left':
        step(env.actions.left)
        return
    if event.key == 'right':
        step(env.actions.right)
        return
    if event.key == 'up':
        step(env.actions.forward)
        return

    # Spacebar
    if event.key == ' ':
        step(env.actions.toggle)
        return
    if event.key == 'pageup':
        step(env.actions.pickup)
        return
    if event.key == 'd':
        step(env.actions.drop)
        return

    if event.key == 'enter':
        step(env.actions.done)
        return

parser = argparse.ArgumentParser()
parser.add_argument(
    "--env",
    help="gym environment to load",
    default='MiniGrid-KeyCorridorGBLA-v0'
)
parser.add_argument(
    "--seed",
    type=int,
    help="random seed to generate the environment with",
    default=-1
)
parser.add_argument(
    "--tile_size",
    type=int,
    help="size at which to render tiles",
    default=32
)
parser.add_argument(
    '--agent_view',
    default=False,
    help="draw the agent sees (partially observable view)",
    action='store_true'
)

args = parser.parse_args()

class p():
    def __init__(self):
        pass

tD = p()
# 341, 681, and 1021
tD.envDescriptor = np.array([[0,0,0,0,0],
                    [0,341,0,0,0],
                    [0,0,681,0,0],
                    [0,0,0,1021,0],
                    [0,0,0,0,0]])

tD.envDescriptor = np.array([[0,0],[0,0]])

tD.envDescriptor = np.array([[0,0,0,0,0,0,0,0,0,0],
                    [0,5,5,5,5,5,5,5,5,0],
                    [0,65,65,65,65,65,65,65,65,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0, 9, 9, 9, 9, 9, 9, 9, 9, 0],
                    [0, 129, 129, 129, 129, 129, 129, 129, 129, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 13, 13, 13, 13, 13, 13, 13, 13, 0],
                    [0, 193, 193, 193, 193, 193, 193, 193, 193, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    ])

tD.envDescriptor = np.array([[0,0,0],[0,13,0],[0,0,0]])


tD.roomDescriptor = [1,0,4,3,1,2]
tD.roomDescriptor = [1,0,0,0,0,0]
tD.roomSize = 4 # can't be less than 3
tD.roomOrdering = [1,1,1,1,1,1] # to discuss
tD.observability = 1  # partially observable
tD.seed = np.random.randint(0,100)   # previously 11

env = gym.make(args.env, taskD=tD,
               goal_id=None, goal_function=None,
               goal_value=None, goal_reward=1)

gd = gym_minigrid.envs.goaldescriptor.GetGoalDescriptor(env)

g = gd.refinement[0].refinement[1].refinement[0]        # findRoom goal

env = gym.make(args.env, taskD=tD,
               goal_id=g.goalId, goal_function=g.achieved,
               goal_value=g.goalValue, goal_reward=1)


if args.agent_view:
    env = RGBImgPartialObsWrapper(env)
    env = ImgObsWrapper(env)

window = Window('gym_minigrid - ' + args.env)
window.reg_key_handler(key_handler)

reset()

#print("setting goal des")
#tD.goalDescriptor = GetGoalDescriptor(env) 

# Blocking event loop
window.show(block=True)
