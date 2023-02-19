import numpy as np
class simple_snake():
    # can add other functions, but needs to have 'move' and the property 'name' at very least
    # this snake won't run into obstacles, but nothing more than that.
    
    def __init__(self, name):
        self.name = name
        self.health = 100
        
    def move(self, board_state: dict) -> int:
        
        # open up the board_state and select a move that doesn't instantly kill the snake

        # the actual engine has the whole dictionary nested in another dictionary and needs the next line uncommented: (I think?)
        # board_state = board_state['board']
        
        # ---------------- obstacle array -----------------
        temp_array = np.zeros((board_state['height'], board_state['width'])) # not sure order is right
        # fill array with bodies of all snakes
        for _snake in board_state['snakes']:
            for _body_segment in _snake['body']:
                # this removes out of bounds 
                tempx = np.clip(_body_segment['x'],0,board_state['width']-1)
                tempy = np.clip(_body_segment['y'],0,board_state['height']-1)
                temp_array[tempx][tempy] = 1

        # get all indexes
        _temp_indexes = np.array(np.nonzero(temp_array)).T
        _temp_obs_dict = list()
        for _row in _temp_indexes:
            _temp_obs_dict.append({'x':_row[0], 'y':_row[1]})

        # add board edges to _temp_obs_dict
        for _width in range(board_state['width']):
            _temp_obs_dict.append({'x':_width, 'y':-1})
            _temp_obs_dict.append({'x':_width, 'y':board_state['height']})
        for _height in range(board_state['height']):
            _temp_obs_dict.append({'x':-1, 'y':_height})
            _temp_obs_dict.append({'x':board_state['width'], 'y':_height})

        # ------- create list of possible moves ----------
        for _snake in board_state['snakes']:
            if _snake['name'] == self.name:
                head_position = _snake['head'] # hold onto current location

        # these are 4 places this snake can move to right now.
        possible_moves = [{'x':head_position['x'],'y':head_position['y']+1},
                          {'x':head_position['x'],'y':head_position['y']-1},
                          {'x':head_position['x']-1,'y':head_position['y']},
                          {'x':head_position['x']+1,'y':head_position['y']}]
        
        # -------- determine which of the possible moves are safe --------
        safe_moves = list()
        for idx, _move in enumerate(possible_moves):
            if _move not in _temp_obs_dict:
                safe_moves.append(idx)
        
        # --------- pick a random safe move ---------
        if len(safe_moves)>0:
            return np.random.choice(safe_moves)
        
        else: 
            # ------- try to move to a tail of a snake --------
            # (this was an afterthought)
            for idx, _move in enumerate(possible_moves):
                for _snake in board_state['snakes']:
                    if _snake['body'][-1] == _move:
                        return idx 
            
            # ----- this snake is going to crash, but it needs to return some direction ------
            return np.random.choice([0,1,2,3])

