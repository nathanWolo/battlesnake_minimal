from game import game_engine
from simple_snake import simple_snake
from random import sample
import random
import copy
rules = {'starting_length': 3, # for constrictor, just set this to something huge.
         'game_mode': 'duel', # or 'solo'
         'food_max': 20, # 
         'food_rate': 0.15, # chance that a new food item is added
         'food_min': 1
        }

my_example_board_state = {'height': 15, 'width': 15,
 'snakes': [{'name': 'tom', 'health': 100,
             'head': {'x': 1, 'y': 0},
             'body': [{'x': 1, 'y': 0},
                      {'x': 1, 'y': 1},
                      {'x': 1, 'y': 1}],
             'length': 3},
            {'name': 'molly', 'health': 100,
             'head': {'x': 1, 'y': 8},
             'body': [{'x': 1, 'y': 8},
                      {'x': 1, 'y': 7},
                      {'x': 1, 'y': 7}],
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
                                    simple_snake('jerry'),
                                    simple_snake('sally')
                                    ],
                          rules = rules)

cur_snake = 'tom'
test_result = copy.deepcopy(my_example_board_state)
turns = 0
while len(test_result['snakes']) > 1:
    if cur_snake == 'tom':
        cur_snake = 'molly'
    else:
        cur_snake = 'tom'
        turns+=1
    print("safe moves ", my_game_engine.mcts_get_safe_moves(test_result, cur_snake), " for ", cur_snake)
    if len(my_game_engine.mcts_get_safe_moves(test_result, cur_snake)) == 0:
        print("no safe moves for ", cur_snake)
        m = random.randint(0,3)
    else:
        m = sample(my_game_engine.mcts_get_safe_moves(test_result, cur_snake),1)[0]
        print("move ", m)
    test_result = my_game_engine.mcts_sim_step(test_result, cur_snake, m)
    print(test_result)

print("turns ", turns)