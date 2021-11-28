from random import choice
import numpy as np
import Board


class Player:
    def __init__(self):
        self.name = "Player"
        self.directions = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1)
        )
        self.player_no = 1
        self.valid_loc = []
        self.valid_moves = {1:[], -1:[]}
        self.score = {}
        self.weight = [[500,  5, 100, 50, 50, 100,  5, 500],
                       [  5,  1,  10, 10, 10,  10,  1,   5],
                       [100, 10,  30, 20, 20,  30, 10, 100],
                       [ 50, 10,  20, 10, 10,  20, 10,  50],
                       [ 50, 10,  20, 10, 10,  20, 10,  50],
                       [100, 10,  30, 20, 20,  30, 10, 100],
                       [  5,  1,  10, 10, 10,  10,  1,   5],
                       [500,  5, 100, 50, 50, 100,  5, 500]]

    def move(self, board_inf):
        """
        Args:
            board_inf:
                 [0] - valid_moves: 可以下的地方，它會是一個二維的 list ex:[[1,2],[2,2]]
                 [1] - board_state: 當前棋盤狀況
                 [2] - player_no  : 你先攻的話就是 1(O),反之 -1(X)
                 [3] - total_step : 現在下到第幾步 (Hint: 對於黑白棋而言，解尾盤比較重要)
        return:
            your moves: 你要下哪裡，它會是一個一維的 list ex:[1,2]
        """
        if board_inf[3] < 40:
            # return choice(board_inf[0])
            max_total = 10
        # elif board_inf[3] < 40:
            # max_total = 20
        else:
            max_total = 20
        # max_total = 100
        self.player_no = board_inf[2]
        self.valid_loc.clear()
        self.valid_moves.clear()
        self.score.clear()
        # print(board_inf[1])
        for row, col in np.argwhere(board_inf[1] != 0):
            self.add_valid_loc(row, col, board_inf[1], self.valid_loc)
        self.update_valid_moves(board_inf[1], self.valid_loc, self.valid_moves)
        unique_valid_moves = np.unique(np.array(self.valid_moves[self.player_no])[:, :2], axis=0)
        for idx, move in enumerate(unique_valid_moves):
            win = 0
            for i in range(max_total):
                win += self.simulate(board_inf[1], self.player_no, move, self.valid_loc, self.valid_moves)
            self.score[idx] = win/max_total
        # self.find_best()
            
        return unique_valid_moves[max(self.score, key=self.score.get)]
    
    def isInside(self, row, col) -> bool:
        return True if 0 <= row < 8 and 0 <= col < 8 else False
        
    def check_who_wins(self, board_status):
        players, counts = np.unique(board_status, return_counts=True)
        # print("players counts:", players, counts)
        # print("winner:", players[np.argmax(counts)])
        return players[np.argmax(counts)]
    
    def add_valid_loc(self, row, col, board_state, valid_loc):
        if [row, col] in valid_loc:
            valid_loc.remove([row, col])
        for d in self.directions:
            this_row, this_col = row + d[0], col + d[1]
            if (
                self.isInside(this_row, this_col)
                and board_state[this_row, this_col] == 0
                and [this_row, this_col] not in valid_loc
            ):
                valid_loc.append([this_row, this_col])
    
    def update_valid_moves(self, board_state, valid_loc, valid_moves):
        valid_moves.clear()
        valid_moves[1] = []
        valid_moves[-1] = []
        for row, col in valid_loc:
            for d in self.directions:
                this_row, this_col = row + d[0], col + d[1]
                if self.isInside(this_row, this_col) and board_state[this_row, this_col] != 0:
                    player = -board_state[this_row, this_col]
                    this_row, this_col = this_row + d[0], this_col + d[1]
                    while self.isInside(this_row, this_col):
                        if board_state[this_row, this_col] == player:
                            valid_moves[player].append([row, col, d[0], d[1]])
                            break
                        elif board_state[this_row, this_col] == -player:
                            this_row, this_col = this_row + d[0], this_col + d[1]
                        else:
                            break

    def action(self, board_state, current_player, move, valid_loc, valid_moves):
        row, col = move
        board_state[row, col] = current_player
        self.add_valid_loc(row, col, board_state, valid_loc)
        nplist = np.array(valid_moves[current_player])
        condition = (nplist[:, :2] == [row, col]).all(axis=1)
        for d in nplist[condition][:, -2:]:
            this_row, this_col = row + d[0], col + d[1]
            while (board_state[this_row, this_col] != current_player):
                board_state[this_row, this_col] = current_player
        self.update_valid_moves(board_state, valid_loc, valid_moves)
    
    def simulate(self, board_state, current_player, move, valid_loc, valid_moves):
        board_cp = board_state.copy()
        valid_loc_cp = valid_loc.copy()
        valid_moves_cp = valid_moves.copy()
        self.action(board_cp, current_player, move, valid_loc_cp, valid_moves_cp)
        current_player *= -1
        while valid_moves_cp[current_player] or valid_moves_cp[-current_player]:
            if not valid_moves_cp[current_player]:
                current_player *= -1
            else:
                next_move = choice(np.unique(np.array(valid_moves_cp[current_player])[:, :2], axis=0))
                self.action(board_cp, current_player, next_move, valid_loc_cp, valid_moves_cp)
                current_player *= -1
        if self.check_who_wins(board_cp) == self.player_no:
            return 1
        else:
            return 0
                
    def find_best():
        pass
        
    

        
        