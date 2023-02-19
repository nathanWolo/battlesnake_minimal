import numpy as np
import copy
from simple_snake import simple_snake
class game_engine():
    
    def init_on_game_state(self, game_state: dict, rules: dict):
        self.width = game_state['width']
        self.height = game_state['height']
        self.snakes = list()
        for _snake in game_state['snakes']:
            self.snakes.append(simple_snake(_snake['name']))
        self.rules = rules
        self.board_state = game_state
        self.history = list()
        
    def initialize(self,
                   board: tuple[int,int],
                   snakes: list[simple_snake],
                   rules: dict,
                  ):
        
        self.width = board[0]
        self.height = board[1]
        self.snakes = snakes # list of classes, 1 per snake
        self.rules = rules
        self.rules['starting_points'] = [{'x':1,'y':1},
                                         {'x':1,'y':self.height-2},
                                         {'x':self.width-1,'y':1},
                                         {'x':self.width-1,'y':self.height-2}]
        
        # fill in the board state at initialization
        self.board_state = dict()
        self.board_state['height'] = self.height
        self.board_state['width'] = self.width
        self.board_state['snakes'] = list()
        self.history = list() # full game history (as stored in the game states)
        
        # fill with snakes
        for idx, _snake in enumerate(snakes):
            temp_dict = {}
            temp_dict['name'] = _snake.name
            temp_dict['health'] = 100
            
            # internal value 'age' is used to track which body segments to pop
            temp_dict['head'] = {'x':self.rules['starting_points'][idx]['x'],
                                 'y':self.rules['starting_points'][idx]['y']}
            
            temp_dict['body'] = list()
            for _ in range(self.rules['starting_length']):
                temp_dict['body'].append({'x':self.rules['starting_points'][idx]['x'],
                                          'y':self.rules['starting_points'][idx]['y']})

            temp_dict['length'] = self.rules['starting_length']
            temp_dict['desired'] = None

            # add snake dictionary
            self.board_state['snakes'].append(temp_dict)
            
        # add some starting food
        self.board_state['food'] = list()
        for _ in range(5):
            self._populate_food()
        
    def _is_occupied(self, state: dict) -> np.ndarray:
        # only 1 channel is needed
        state_matrix = np.zeros((state["height"], state["width"]))

        # -- fill --
        for _snake in state['snakes']:
            for _body_segment in _snake['body']:
                state_matrix[_body_segment['x'], _body_segment['y']] = 1

        for _food in state['food']:
            state_matrix[_food['x'],_food['y']] = 1
        
        return state_matrix-1
    
    
    def _select_empty_loc(self) -> dict:
        # make an array of possible locations

        _temp_indexes = np.array(np.nonzero(self._is_occupied(self.board_state))).T
        # shuffle
        _temp_indexes = _temp_indexes[np.random.permutation(len(_temp_indexes))]
        return {'x':_temp_indexes[0][0], 'y':_temp_indexes[0][1]}
    
    def _populate_food(self):
        try:
            self.board_state['food'].append(self._select_empty_loc())
        except(IndexError):
            #a snake just died this frame
            pass
    
    def get_state(self) -> dict:
        # return a dictionary of the current state of the game
        # (following similar to battlensake dictionary)
        reduced_board_state = copy.deepcopy(self.board_state)

        for _snake in reduced_board_state['snakes']:
            del _snake['desired']

        return reduced_board_state
    
    def _move_target(self, current_pos: dict, move_dir: int) -> dict:
        if move_dir == 0: current_pos['y'] += 1 # up
        if move_dir == 1: current_pos['y'] -= 1 # down
        if move_dir == 2: current_pos['x'] -= 1 # left
        if move_dir == 3: current_pos['x'] += 1 # right
        return current_pos
        
    def step(self) -> str: # returns either 'running' or 'complete'
        
        # --------- save the current game state into history -------------
        _temp_dict = copy.deepcopy(self.board_state)
        self.history.append(_temp_dict)

        # ----------- request updates from living snakes -------------

        for _snake_class in self.snakes: # for each snake class
            for _snake in self.board_state['snakes']: # loop over snakes in board (to select the instance)
                if _snake['name'] == _snake_class.name:
                    
                    # request move from snake
                    _temp_move = _snake_class.move(self.get_state())
                    
                    # store the move in this hidden key
                    _snake['desired'] = self._move_target(_snake['head'].copy(), _temp_move) # absolute position
                    
                    # instantly remove a snake if it moves into a wall (should this be done later?)
                    if _snake['desired']['x'] > self.width or _snake['desired']['x'] < 0 or _snake['desired']['y'] > self.height or _snake['desired']['y'] < 0:
                        self.board_state['snakes'].remove(_snake)
                        print(_snake['name'],'went out of bounds')


        # ----------------- face-off -----------------
        pseudo_dead_snakes = list()
        
        # iterate over all pairs of snakes
        for _temp_snake in self.board_state['snakes']:
            for _temp_snake2 in self.board_state['snakes']:
                if _temp_snake['name'] != _temp_snake2['name']:
                    if _temp_snake['desired'] == _temp_snake2['desired']:
                        # collision, fight it out!
                        if _temp_snake['length'] <= _temp_snake2['length']:
                            pseudo_dead_snakes.append(_temp_snake['name'])

        # remove based on collision results
        for _pseudo_snake in pseudo_dead_snakes:
            for _snake in self.board_state['snakes']:
                if _pseudo_snake == _snake['name']:
                    self.board_state['snakes'].remove(_snake)
                    print(_snake['name'],'faced off and lost')

        # ------------ remove tail ---------------
        # is snake eating?
        eating_snakes = list()
        
        for _snake in self.board_state['snakes']:
            for _food in self.board_state['food']:
                if _snake['desired'] == _food: # comparing dictionaries
                    eating_snakes.append(_snake['name'])
                    self.board_state['food'].remove(_food)

        # shrink snake (via aging body segments)
        for _snake in self.board_state['snakes']:
            # append body
            if _snake['name'] not in eating_snakes:
                _snake['body'].pop()
            else:
                _snake['health'] = 100 # eating!
                _snake['length'] += 1
                
        # ---------------- obstacle array -----------------
        # note: out of bounds is covered above
        temp_array = np.zeros((self.height, self.width))
        # fill array with snake bodies
        for _snake in self.board_state['snakes']:
            for _body_segment in _snake['body']:
                # this removes out of bounds 
                tempx = np.clip(_body_segment['x'], 0, self.width-1)
                tempy = np.clip(_body_segment['y'], 0, self.height-1)
                temp_array[tempx][tempy] = 1

        # possibility of additional arbitrary obstacles
        # for _obstacle in self.board_state['obstacles']:
        #     temp_array[_obstacle['x']][_obstacle['y']] = 1
        
        # get all indexes of obstacles into a list of dicitonaries with the keys, 'x', and 'y'.
        _temp_indexes = np.array(np.nonzero(temp_array)).T
        _temp_obs_dict = list()
        for _row in _temp_indexes:
            _temp_obs_dict.append({'x':_row[0], 'y':_row[1]})
        
        # check if the snake is moving into an obstacle
        pesudo_dead_snakes = list()
        for _snake in self.board_state['snakes']:
            if _snake['desired'] in _temp_obs_dict:
                pesudo_dead_snakes.append(_snake)

        # remove based on collision results
        for _pseudo_snake in pseudo_dead_snakes:
            for _snake in self.board_state['snakes']:
                if _pseudo_snake == _snake['name']:
                    self.board_state['snakes'].remove(_snake)
                    print(_snake['name'],'runs into another snake at',_snake['desired'])
                    

        # ----- move head ------
        for _snake in self.board_state['snakes']:
            _snake['body'].insert(0,_snake['desired'])
            _snake['head'] = _snake['desired']

        
        # --------------- starve --------------
        # decrease health
        for _snake in self.board_state['snakes']:
            _snake['health'] -= 1
            if _temp_snake['health'] <= 0: # remove if starved
                self.board_state['snakes'].remove(_snake)  
                print(_snake['name'],'starved')

        # --------------- internal stuff -----------
        
        # ---- add food -----
        n_food = len(self.board_state['food'])
        if (n_food < self.rules['food_max']):
            if np.random.rand() < self.rules['food_rate']:
                self._populate_food()
        
        if n_food < self.rules['food_min']:
            self._populate_food()
        
        
        # --- check game end ---- 
        if self.rules['game_mode'] == 'duel': # multiple snakes, over when only 1 remains
            if len(self.board_state['snakes']) == 1:
                print(self.board_state['snakes'][0]['name'],'wins')
                _temp_dict = copy.deepcopy(self.board_state)
                self.history.append(_temp_dict)
                return 'complete'
            elif len(self.board_state['snakes']) == 0:
                print('draw')
                _temp_dict = copy.deepcopy(self.board_state)
                self.history.append(_temp_dict)
                return 'complete'
            else:
                return 'running'
        elif self.rules['game_mode'] == 'solo':
            if len(self.board_state['snakes']) == 0:
                _temp_dict = copy.deepcopy(self.board_state)
                self.history.append(_temp_dict)
                return 'complete'

            else: return 'running'