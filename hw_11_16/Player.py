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
        self.cornor = (
            (0, 0),
            (0, 7),
            (7, 0),
            (7, 7)
        )
        self.start_level = 0
        self.search_levels = 3
        self.player_no = 1
        # self.weight = [[500,  5, 100, 50, 50, 100,  5, 500],
        #                [  5,  1,  10, 10, 10,  10,  1,   5],
        #                [100, 10,  30, 20, 20,  30, 10, 100],
        #                [ 50, 10,  20, 10, 10,  20, 10,  50],
        #                [ 50, 10,  20, 10, 10,  20, 10,  50],
        #                [100, 10,  30, 20, 20,  30, 10, 100],
        #                [  5,  1,  10, 10, 10,  10,  1,   5],
        #                [500,  5, 100, 50, 50, 100,  5, 500]]
        self.c = np.sqrt(2*np.log(2)/np.log(np.e))

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
        self.player_no = board_inf[2]
        valid_loc = []
        valid_moves = {1:[], -1:[]}
        for row, col in np.argwhere(board_inf[1] != 0):
            self.add_valid_loc(row, col, board_inf[1], valid_loc)
        self.update_valid_moves(board_inf[1], valid_loc, valid_moves)
        
        # if board_inf[3] < 40:
            # return choice(board_inf[0])
            # max_total = 50
        # else:
            # max_total = 100

        # return self.MCS(board_inf[1], self.player_no, valid_loc, valid_moves, max_total)
        # return self.MCS_UCB(board_inf[1], self.player_no, valid_loc, valid_moves, max_total)
        return self.find_max(board_inf[1], self.player_no, valid_loc, valid_moves, self.start_level)
        # return unique_valid_moves[max(score, key=score.get)]
    
    def isInside(self, row, col) -> bool:
        return True if 0 <= row < 8 and 0 <= col < 8 else False
        
    def check_who_wins(self, board_status):
        players, counts = np.unique(board_status, return_counts=True)
        result = {}
        for p, c in zip(players, counts):
            result[p] = c
        if result[1] == result[-1]:
            return 0
        else:
            return max(result, key=result.get)
            
    
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
                
    def MCS(self, board_state, current_player, valid_loc, valid_moves, max_total):
        score = {}
        unique_valid_moves = np.unique(np.array(valid_moves[current_player])[:, :2], axis=0)
        for idx, move in enumerate(unique_valid_moves):
            win = 0
            for i in range(max_total):
                win += self.simulate(board_state, current_player, move, valid_loc, valid_moves)
            score[idx] = win/max_total
        return unique_valid_moves[max(score, key=score.get)]
    
    def MCS_UCB(self, board_state, current_player, valid_loc, valid_moves, max_total):
        score = {}
        Wi = {}
        Ni = {}
        UCB = {}        
        unique_valid_moves = np.unique(np.array(valid_moves[current_player])[:, :2], axis=0)
        for idx, move in enumerate(unique_valid_moves):
            Wi[idx] = self.simulate(board_state, current_player, move, valid_loc, valid_moves)
            Ni[idx] = 1
        for N in range(1, max_total+1):
            UCB.clear()
            for idx in range(len(unique_valid_moves)):
                UCB[idx] = Wi[idx]/Ni[idx] + self.c*np.sqrt(np.log(N)/Ni[idx])
            move_id = max(UCB, key=UCB.get)
            Wi[move_id] += self.simulate(board_state, current_player, unique_valid_moves[move_id], valid_loc, valid_moves)
            Ni[move_id] += 1
        for idx in range(len(unique_valid_moves)):
            score[idx] = Wi[idx]/Ni[idx]
        return unique_valid_moves[max(score, key=score.get)]
    
    def get_value(self, board_state, current_player, valid_moves):
        unique_valid_moves = np.unique(np.array(valid_moves[current_player])[:, :2], axis=0)
        mobility = len(unique_valid_moves)
        disc_count = 0.01*len(np.argwhere(board_state == current_player))
        cornor_bonus = 0
        for cornor in self.cornor:
            if (unique_valid_moves == cornor).all(axis=1).any():
                cornor_bonus += 10
        return mobility + disc_count + cornor_bonus
    
    def get_endgame_value(self, board_state, current_player):
        winner = self.check_who_wins(board_state)
        if winner == current_player:
            return 100
        elif winner == 0:
            return 20
        else:
            return 0
    
    def find_max(self, board_state, current_player, valid_loc, valid_moves, level):
        if not (valid_moves[current_player] or valid_moves[-current_player]):
            return self.get_endgame_value(board_state, current_player)
        if level >= self.search_levels:
            return self.get_value(board_state, current_player, valid_moves)
        else:
            if not valid_moves[current_player]:
                return self.find_max(board_state, -current_player, valid_loc, valid_moves, level+1)
            else:
                value = {}
                unique_valid_moves = np.unique(np.array(valid_moves[current_player])[:, :2], axis=0)
                for idx, move in enumerate(unique_valid_moves):
                    board_cp = board_state.copy()
                    valid_loc_cp = valid_loc.copy()
                    valid_moves_cp = valid_moves.copy()
                    self.action(board_cp, current_player, move, valid_loc_cp, valid_moves_cp)
                    value[idx] = self.find_max(board_cp, -current_player, valid_loc_cp, valid_moves_cp, level+1)
                if not level:
                    return unique_valid_moves[max(value, key=value.get)]
                else:
                    return max(value, key=value.get)
        
    