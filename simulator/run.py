import numpy as np
import matplotlib.pyplot as plt
import copy
from tqdm import tqdm
from game import game_engine
from simple_snake import simple_snake
from time import perf_counter


rules = {'starting_length': 3, # for constrictor, just set this to something huge.
         'game_mode': 'duel', # or 'solo'
         'food_max': 20, # 
         'food_rate': 0.15, # chance that a new food item is added
         'food_min': 1
        }

my_example_board_state = {'height': 15, 'width': 15,
 'snakes': [{'name': 'tom', 'health': 100,
             'head': {'x': 1, 'y': 0},
             'body': [{'x': 1, 'y': 1},
                      {'x': 1, 'y': 1},
                      {'x': 1, 'y': 1}],
             'length': 3},
            {'name': 'molly', 'health': 100,
             'head': {'x': 1, 'y': 14},
             'body': [{'x': 1, 'y': 14},
                      {'x': 1, 'y': 14},
                      {'x': 1, 'y': 14}],
             'length': 3}],
 'food': [{'x': 0, 'y': 0},
          {'x': 2, 'y': 2},
          {'x': 9, 'y': 9},
          {'x': 6, 'y': 6},
          {'x': 5, 'y': 5}]}

my_game_engine = game_engine()
my_game_engine.initialize(board = (11,11),
                          snakes = [simple_snake('tom'),
                                    simple_snake('molly'),
                                    simple_snake('sam')],
                          rules = rules)


start_time = perf_counter()
game_state = 'running'
n_turns = 0
#np.random.seed(17) # fixes the randomness for repeatability (for now)

while (game_state == 'running'): # should take less than a couple seconds on a slow computer
    game_state = my_game_engine.step()
    n_turns+=1
    
end_time = perf_counter()
elapsed_time = end_time-start_time
print(f'time: {elapsed_time:.4}s, n turns {n_turns},\n     ({n_turns/elapsed_time:.3f} tps, {elapsed_time/n_turns:.3f} spt)')

