import gym_minigrid
from gym_minigrid.envs import RoomGrid
from gym_minigrid.minigrid import COLOR_NAMES

from .instrs import *

def room_from_loc(env, loc):
    """
    Get the room coordinates for a given location
    """

    if loc == 'north':
        return (1, 0)
    if loc == 'south':
        return (1, 2)
    if loc == 'west':
        return (0, 1)
    if loc == 'east':
        return (2, 1)

    if loc == 'left':
        return (1, 0)
    if loc == 'right':
        return (1, 2)
    if loc == 'front':
        return (2, 1)
    if loc == 'behind':
        return (0, 1)

    # By default, use the central room
    return (1, 1)

def door_from_loc(env, loc):
    """
    Get the door index for a given location
    The door indices correspond to: right, down, left, up
    """

    if loc == 'east' or loc == 'front':
        return (2, 1), 2
    if loc == 'south' or loc == 'right':
        return (1, 2), 3
    if loc == 'west' or loc == 'behind':
        return (0, 1), 0
    if loc == 'north' or loc == 'left':
        return (1, 0), 1

    return door_from_loc(env, env._randElem(['east', 'west', 'south', 'north']))

def gen_env(instrs, seed):
    """
    Generate an environment from a list of instructions (structured instruction).

    :param seed: seed to be used for the random number generator.
    """

    # Set of objects to be placed
    objs = set()

    # For each instruction
    for instr in instrs:
        # The pick, goto and open actions mean the referenced objects must exist
        if instr.action == 'pick' or instr.action == 'goto' or instr.action == 'open':
            obj = instr.object
            objs.add(obj)

    # Create the environment
    # Note: we must have at least 3x3 rooms to support absolute locations
    env = RoomGrid(room_size=7, num_cols=3)
    env.seed(seed)

    # Assign colors to objects that don't have one
    for obj in objs:
        if obj.color is None:
            objs.remove(obj)
            color = env._randElem(COLOR_NAMES)
            obj = Object(type=obj.type, loc=obj.loc, state=obj.state, color=color)
            objs.add(obj)

    # Make sure that locked doors have matching keys
    for obj in set(objs):
        if obj.type == 'door' and obj.state == 'locked':
            keys = filter(lambda o: o.type == 'key' and o.color == obj.color, objs)
            if len(list(keys)) == 0:
                objs.add(Object('key', obj.color, None, None))

    # For each object to be added
    for obj in objs:
        if obj.type == 'door':
            room, door = door_from_loc(env, obj.loc)
            env.add_door(*room, door, obj.color, obj.state == 'locked')
        else:
            room = room_from_loc(env, obj.loc)
            env.add_object(*room, obj.type, obj.color)

    # Make sure that all rooms are reachable by the agent
    env.connect_all()

    return env
