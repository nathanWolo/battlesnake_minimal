import numpy as np
import matplotlib.pyplot as plt
import copy
from tqdm import tqdm
from game import game_engine
from simple_snake import simple_snake
from time import perf_counter
from matplotlib.colors import LinearSegmentedColormap
import os
import glob


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
                                    simple_snake('jerry'),
                                    simple_snake('sally')
                                    ],
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

''' plot the match (if you want) '''

def checkerboard(shape):
    # from https://stackoverflow.com/questions/2169478/how-to-make-a-checkerboard-in-numpy
    return np.indices(shape).sum(axis=0) % 2

def plot_match(game_history, save_folder):

    # define colour space for background tiles
    cmap = LinearSegmentedColormap.from_list('mycmap', ['lightgrey', 'white'])

    # match snake colours to name, so that snake colours are constant when a snake is eliminated. 
    snake_cmaps = ['Greens','Blues','Purples','Oranges']
    snake_cmap_matched = {}
    for idx, _snake in enumerate(game_history[0]['snakes']): # starting snapshot
        snake_cmap_matched[_snake['name']] = snake_cmaps[idx]


    # loop through each step, save figure
    for idx, (_temp_history) in tqdm(enumerate(game_history)):

        # prepare board layers
        board_size = (_temp_history["height"], _temp_history["width"])

        #food
        food_layer = np.zeros(board_size)
        for _food in _temp_history['food']:
            food_layer[_food['x']][_food['y']] = 1

        # snakes
        snake_layers = {}
        for _snake in _temp_history['snakes']:
            temp_layer = np.zeros(board_size)
            shader = 0
            for _body in _snake['body']:
                try:
                    temp_layer[_body['x']][_body['y']] = 1 + shader
                    shader += 1
                except:
                    #snake out of bounds
                    pass
            snake_layers[_snake['name']] = temp_layer


        # ---------- start figure -----------
        plt.figure()

        # plot background
        plt.imshow(checkerboard(board_size),cmap=cmap)

        # plot food
        plt.scatter(*np.nonzero(food_layer),c='tab:orange',marker='s',s=100,edgecolors='k')

        # plot snakes (room for improvement here)
        for _snake in _temp_history['snakes']:

            plt.scatter(*np.nonzero(snake_layers[_snake['name']]),
                        c = snake_layers[_snake['name']][np.nonzero(snake_layers[_snake['name']])],
                        cmap = snake_cmap_matched[_snake['name']],
                        marker='s',
                        s=100,
                        edgecolors='k')

        plt.xticks([])
        plt.yticks([])
        plt.savefig(f'{save_folder}frame{idx:04}.png')
        plt.close()
        
        
# actually call this function
plot_match(game_history = my_game_engine.history,
           save_folder = './saved/test_game1/')

''' make gif from a folder '''
import imageio
from glob import glob

def make_gif(folder, save_path): 
    # load all .pngs in that folder as still images, then slap them together.

    if folder[-5:] != '*.png':
        folder += '*.png'
        
    # get paths to all files
    image_paths = glob(folder)
    image_paths.sort()

    # load each still
    stills_list=list()
    for _path in tqdm(image_paths):
        stills_list.append(imageio.imread(_path))

    # convert list of stills into a gif
    imageio.mimsave(save_path, stills_list, duration=0.1)
    print('gif saved')
    files = glob('./saved/test_game1/*.png')
    for f in files:
        os.remove(f)

make_gif(folder='./saved/test_game1/',
        save_path = './gifs/match.gif')