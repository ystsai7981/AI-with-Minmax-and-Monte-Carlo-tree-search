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
        self.search_levels = 1
        self.player_no = 1
        self.weight = np.array([[120,-20, 20,  5,  5, 20,-20,120],
                                [-20,-40, -5, -5, -5, -5,-40,-20],
                                [ 20, -5, 15,  3,  3, 15, -5, 20],
                                [  5, -5,  3,  3,  3,  3, -5,  5],
                                [  5, -5,  3,  3,  3,  3, -5,  5],
                                [ 20, -5, 15,  3,  3, 15, -5, 20],
                                [-20,-40, -5, -5, -5, -5,-40,-20],
                                [120,-20, 20,  5,  5, 20,-20,120]])
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
        if len(board_inf[0]) == 1:
            return board_inf[0][0]
        self.player_no = board_inf[2]
        valid_loc = []
        valid_moves = {1:[], -1:[]}
        for row, col in np.argwhere(board_inf[1] != 0):
            self.add_valid_loc(row, col, board_inf[1], valid_loc)
        self.update_valid_moves(board_inf[1], valid_loc, valid_moves)
        
        if board_inf[3] <= 49:
            self.search_levels = 1
            # return choice(board_inf[0])
            # max_total = 50
            # return self.find_max(board_inf[1], valid_loc, valid_moves, self.start_level)
        # elif board_inf[3] <=40:
            
        else:
            self.search_levels = 100
            # max_total = 5000
            # return self.MCS_UCB(board_inf[1], self.player_no, valid_loc, valid_moves, max_total)

        # return self.MCS(board_inf[1], self.player_no, valid_loc, valid_moves, max_total)
        # return self.MCS_UCB(board_inf[1], self.player_no, valid_loc, valid_moves, max_total)
        return self.find_max(board_inf[1], valid_loc, valid_moves, self.start_level, -float("inf"), float("inf"))

    
    def isInside(self, row, col) -> bool:
        return True if 0 <= row < 8 and 0 <= col < 8 else False
        
    def check_who_wins(self, board_status):
        players, counts = np.unique(board_status, return_counts=True)
        result = {}
        for p, c in zip(players, counts):
            result[p] = c
        if result.get(1) == result.get(-1):
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
        if valid_moves[current_player]:
            nplist = np.array(valid_moves[current_player])
            condition = (nplist[:, :2] == [row, col]).all(axis=1)
            for d in nplist[condition][:, -2:]:
                this_row, this_col = row + d[0], col + d[1]
                while (board_state[this_row, this_col] == -current_player):
                    board_state[this_row, this_col] = current_player
                    this_row, this_col = this_row + d[0], this_col + d[1]
            self.update_valid_moves(board_state, valid_loc, valid_moves)
        else:
            # print("valid move is empty!")
            return
    
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
        if not valid_moves[current_player]:
            mobility = 0
        else:
            unique_valid_moves = np.unique(np.array(valid_moves[current_player])[:, :2], axis=0)
            mobility = len(unique_valid_moves)
        disc_count = 0.01*len(np.argwhere(board_state == current_player))
        cornor_bonus = 0
        for cornor in self.cornor:
            if (np.argwhere(board_state == current_player) == cornor).all(axis=1).any():
                cornor_bonus += 10
        return mobility + disc_count + cornor_bonus
    
    def get_WPC(self, board_state):
        if self.player_no == 1:
            return np.sum(np.array(board_state)*self.weight)
        else:
            return -np.sum(np.array(board_state)*self.weight)
    
    def get_endgame_value(self, board_state):
        # winner = self.check_who_wins(board_state)
        # if winner == self.player_no:
        #     return 100
        # elif winner == 0:
        #     return 20
        # else:
        #     return 0
        # print(len(np.argwhere(board_state == self.player_no)))
        return len(np.argwhere(board_state == self.player_no))
    
    def find_max(self, board_state, valid_loc, valid_moves, level, alpha, beta):
        if not (valid_moves[self.player_no] or valid_moves[-self.player_no]):
            return self.get_endgame_value(board_state)
            # return self.get_WPC(board_state)
        if level >= self.search_levels:
            # return self.get_value(board_state, self.player_no, valid_moves) - self.get_value(board_state, -self.player_no, valid_moves)
            return self.get_WPC(board_state)
        else:
            if not valid_moves[self.player_no]:
                return self.find_min(board_state, valid_loc, valid_moves, level+1, alpha, beta)
            else:
                value = {}
                unique_valid_moves = np.unique(np.array(valid_moves[self.player_no])[:, :2], axis=0)
                for idx, move in enumerate(unique_valid_moves):
                    board_cp = board_state.copy()
                    valid_loc_cp = valid_loc.copy()
                    valid_moves_cp = valid_moves.copy()
                    self.action(board_cp, self.player_no, move, valid_loc_cp, valid_moves_cp)
                    value[idx] = self.find_min(board_cp, valid_loc_cp, valid_moves_cp, level+1, alpha, beta)
                    if value[idx] > alpha:
                        alpha = value[idx]
                    if alpha > beta:
                        return alpha
                if not level:
                    return unique_valid_moves[max(value, key=value.get)]
                else:
                    return max(value, key=value.get)
                
    def find_min(self, board_state, valid_loc, valid_moves, level, alpha, beta):
        if not (valid_moves[self.player_no] or valid_moves[-self.player_no]):
            return self.get_endgame_value(board_state)
            # return self.get_WPC(board_state)
        if level >= self.search_levels:
            # return self.get_value(board_state, self.player_no, valid_moves) - self.get_value(board_state, -self.player_no, valid_moves)
            return self.get_WPC(board_state)
        else:
            if not valid_moves[-self.player_no]:
                return self.find_max(board_state, valid_loc, valid_moves, level+1, alpha, beta)
            else:
                value = {}
                unique_valid_moves = np.unique(np.array(valid_moves[-self.player_no])[:, :2], axis=0)
                for idx, move in enumerate(unique_valid_moves):
                    board_cp = board_state.copy()
                    valid_loc_cp = valid_loc.copy()
                    valid_moves_cp = valid_moves.copy()
                    self.action(board_cp, -self.player_no, move, valid_loc_cp, valid_moves_cp)
                    value[idx] = self.find_max(board_cp, valid_loc_cp, valid_moves_cp, level+1, alpha, beta)
                    if value[idx] < beta:
                        beta = value[idx]
                    if alpha > beta:
                        return beta
                if not level:
                    return unique_valid_moves[min(value, key=value.get)]
                else:
                    return min(value, key=value.get)

                
class Node:
    def __init__(self, player=None, move=None, parent=None):
        self.player = player
        self.move = move
        self.Ni = 0.
        self.Wi = 0.
        self.parent = parent
        self.children = []
        
    def get_move(self):
        return self.move
        
    def UCB(self, N, c=np.sqrt(2*np.log(2)/np.log(np.e))):
        if self.Ni == 0:
            return(float("inf"))
        elif N == 0:
            return self.Wi/self.Ni
        else:
            return self.Wi/self.Ni + c*np.sqrt(np.log(N)/self.Ni)
        
    def score(self):
        if self.Ni == 0:
            return 0
        else:
            return self.Wi/self.Ni
    
    def find_max_UCB_child(self):
        idx = 0
        max_UCB = -float("inf")
        for i, child in enumerate(self.children):
            UCB = child.UCB(self.Ni)
            if UCB > max_UCB:
                idx = i
                max_UCB = UCB
        return self.children[idx]
    
    def find_max_score_child(self):
        idx = 0
        max_score = -float("inf")
        for i, child in enumerate(self.children):
            score = child.score()
            if score > max_score:
                idx = i
                max_score = score
        return self.children[idx]
    
    def isLeaf(self):
        if not self.children:
            return True
        else:
            return False
        
    def inTree(self):
        if self.Ni != 0:
            return True
        else:
            return False
        
    def expand(self, valid_moves, next_player=None):
        # unique_valid_moves = np.unique(np.array(valid_moves[next_player])[:, :2], axis=0)
        # for i in unique_valid_moves:
        #     self.children.append(Node(next_player, i, self))
        
           
        # if next_player == 1:
            # next_valid_moves = np.array([[2,3],
            #                              [3,2],
            #                              [4,5],
            #                              [5,4]])
            # for i in next_valid_moves:
                # self.children.append(Node(next_player, i, self))
        # elif next_player == -1:
            # next_valid_moves = np.array([[2,4],
            #                              [4,2],
            #                              [3,5],
            #                              [5,3]])
            # for i in next_valid_moves:
                # self.children.append(Node(next_player, i, self))
        # else:
        if next_player == None:
            next_player = -self.player
        if len(valid_moves[next_player]) == 0:
            if len(valid_moves[-next_player]) == 0:
                return
            else:
                unique_valid_moves = np.unique(np.array(valid_moves[-next_player])[:, :2], axis=0)
                for i in unique_valid_moves:
                    self.children.append(Node(-next_player, i, self))
        else:
            unique_valid_moves = np.unique(np.array(valid_moves[next_player])[:, :2], axis=0)
            for i in unique_valid_moves:
                self.children.append(Node(next_player, i, self))
        
        
            
    def pick(self, mode="random"):
        if mode == "random":
            return choice(self.children)
        elif mode == "max":
            return choice(self.children)
    
    def update(self, winner):
        self.Ni += 1
        if winner == self.player:
            self.Wi += 1
            
        
class Tree(Player):
    def __init__(self):
        super().__init__()
        self.root = None
        self.current_node = self.root
        self.board_cp = None
        self.current_player = 0
        self.valid_loc_cp = None
        self.valid_moves_cp = None
        self.keep_board_state = np.array([[ 0, 0, 0, 0, 0, 0, 0, 0],
                                          [ 0, 0, 0, 0, 0, 0, 0, 0],
                                          [ 0, 0, 0, 0, 0, 0, 0, 0],
                                          [ 0, 0, 0,-1, 1, 0, 0, 0],
                                          [ 0, 0, 0, 1,-1, 0, 0, 0],
                                          [ 0, 0, 0, 0, 0, 0, 0, 0],
                                          [ 0, 0, 0, 0, 0, 0, 0, 0],
                                          [ 0, 0, 0, 0, 0, 0, 0, 0]])
        self.keep_valid_loc = []
        self.keep_valid_moves = {1:[], -1:[]}
        self.keep_current_player = 0
        for row, col in np.argwhere(self.keep_board_state != 0):
            self.add_valid_loc(row, col, self.keep_board_state, self.keep_valid_loc)
        self.update_valid_moves(self.keep_board_state, self.keep_valid_loc, self.keep_valid_moves)
        
    def initialize(self, board_state, current_player, valid_loc, valid_moves):
        self.current_node = self.root
        self.board_cp = board_state.copy()
        self.current_player = current_player
        self.valid_loc_cp = valid_loc.copy()
        self.valid_moves_cp = valid_moves.copy()
    
    def move(self, board_inf):
        # print("對手落子:", board_inf[4])
        self.player_no = board_inf[2]
        valid_loc = []
        valid_moves = {1:[], -1:[]}
        for row, col in np.argwhere(board_inf[1] != 0):
            self.add_valid_loc(row, col, board_inf[1], valid_loc)
        self.update_valid_moves(board_inf[1], valid_loc, valid_moves)
        self.initialize(board_inf[1], board_inf[2], valid_loc, valid_moves)
        
        if self.keep_current_player == 0:
            self.keep_board_state = np.array([[ 0, 0, 0, 0, 0, 0, 0, 0],
                                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                                              [ 0, 0, 0,-1, 1, 0, 0, 0],
                                              [ 0, 0, 0, 1,-1, 0, 0, 0],
                                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                                              [ 0, 0, 0, 0, 0, 0, 0, 0]])
            self.keep_valid_loc = []
            self.keep_valid_moves = {1:[], -1:[]}
            for row, col in np.argwhere(self.keep_board_state != 0):
                self.add_valid_loc(row, col, self.keep_board_state, self.keep_valid_loc)
            self.update_valid_moves(self.keep_board_state, self.keep_valid_loc, self.keep_valid_moves)
            self.keep_current_player = 1
            if board_inf[2] == -1:
                self.action(self.keep_board_state, self.keep_current_player, board_inf[4], self.keep_valid_loc, self.keep_valid_moves)
                self.keep_current_player *= -1
                # print("keep現在可以下的位置:", np.unique(np.array(self.keep_valid_moves[self.keep_current_player])[:, :2], axis=0))
                # print("keep現在可以下的位置:", self.keep_valid_moves[self.keep_current_player])
            # else:
                # print("keep現在可以下的位置:", np.unique(np.array(self.keep_valid_moves[self.keep_current_player])[:, :2], axis=0))
                # print("keep現在可以下的位置:", self.keep_valid_moves[self.keep_current_player])
        else:
            if (np.array(board_inf[4]) == [-1, -1]).all():
                self.keep_current_player *= -1
                # print("keep現在可以下的位置:", np.unique(np.array(self.keep_valid_moves[self.keep_current_player])[:, :2], axis=0))
                # print("keep現在可以下的位置:", self.keep_valid_moves[self.keep_current_player])
            else:
                self.action(self.keep_board_state, self.keep_current_player, board_inf[4], self.keep_valid_loc, self.keep_valid_moves)
                self.keep_current_player *= -1
                # print("keep現在可以下的位置:", np.unique(np.array(self.keep_valid_moves[self.keep_current_player])[:, :2], axis=0))
                # print("keep現在可以下的位置:", self.keep_valid_moves[self.keep_current_player])
        
        

        self.root = Node()
        self.initialize(board_inf[1], board_inf[2], valid_loc, valid_moves)
        self.root.expand(self.valid_moves_cp, self.player_no)

        printlist = []
        for i in self.root.children:
            printlist.append(i.get_move())
        # print("root 的 children:(未下)", printlist)


            
                    
        # if self.current_player == -self.player_no:
        #     if (np.array(board_inf[4]) == [-1, -1]).all():
        #         print("對手還沒下或者沒得下")
        #         self.current_player = self.player_no
        #     else:
        #         for i, child in enumerate(self.root.children):
        #             if (np.array(child.get_move()) == board_inf[4]).all():
        #                 self.root = child
        #                 self.root.parent = None
        #                 self.current_player = self.player_no
        #                 if not self.root.children:
        #                     self.root.expand(self.valid_moves_cp)
        #                 break
        # print("當前root move:", self.root.get_move())
        

        
        # self.initialize(board_inf[1], board_inf[2], valid_loc, valid_moves)
        next_node = self.MCTS(board_inf[1], board_inf[2], valid_loc, valid_moves, 100)
        
        # self.initialize(board_inf[1], board_inf[2], valid_loc, valid_moves)
        # self.root = next_node
        # self.root.parent = None
        # self.action(self.board_cp, self.current_player, self.root.get_move(), self.valid_loc_cp, self.valid_moves_cp)
        # self.current_player = -next_node.player
        # if not self.root.children:
        #     self.root.expand(self.valid_moves_cp)

        # return choice(board_inf[0])
        # print("最終決定下:", next_node.get_move())
        # printlist = []
        # for i in next_node.children:
        #     printlist.append(i.get_move())
        # print("對手的選擇有:", printlist)
        
        self.action(self.keep_board_state, self.keep_current_player, next_node.get_move(), self.keep_valid_loc, self.keep_valid_moves)
        self.keep_current_player *= -1
        # if self.keep_valid_moves[self.keep_current_player]:
            # print("keep對手現在可以下的位置:", np.unique(np.array(self.keep_valid_moves[self.keep_current_player])[:, :2], axis=0))
        # print(self.keep_board_state)
        if not self.keep_valid_moves[self.keep_current_player] and not self.keep_valid_moves[-self.keep_current_player]:
            self.keep_current_player = 0
        
        return next_node.get_move()
    
    def selection(self):
        if self.current_node.isLeaf():
            # print(self.current_node.get_move())
            return
        else:
            next_node = self.current_node.find_max_UCB_child()
            self.action(self.board_cp, self.current_player, next_node.get_move(), self.valid_loc_cp, self.valid_moves_cp)
            self.current_node = next_node
            self.current_player = -next_node.player
            self.selection()
    
    def expansion(self):
        self.current_node.expand(self.valid_moves_cp)
        if self.current_node.children:
            next_node = self.current_node.pick()
            self.action(self.board_cp, next_node.player, next_node.get_move(), self.valid_loc_cp, self.valid_moves_cp)
            self.current_node = next_node
            self.current_player = -next_node.player
        
    def simulation(self)->int:
        while self.valid_moves_cp[self.current_player] or self.valid_moves_cp[-self.current_player]:
            if not self.valid_moves_cp[self.current_player]:
                self.current_player *= -1
            else:
                next_move = choice(np.unique(np.array(self.valid_moves_cp[self.current_player])[:, :2], axis=0))
                self.action(self.board_cp, self.current_player, next_move, self.valid_loc_cp, self.valid_moves_cp)
                self.current_player *= -1
        return self.check_who_wins(self.board_cp)
        
    def backpropagation(self, winner):
        self.current_node.update(winner)
        if self.current_node.parent:
            self.current_node = self.current_node.parent
            self.backpropagation(winner)
            
    def MCTS(self, board_state, current_player, valid_loc, valid_moves, max_total)->Node:
        for i in range(max_total):
            self.initialize(board_state, current_player, valid_loc, valid_moves)
            self.selection()
            if self.current_node.inTree():
                self.expansion()
            winner = self.simulation()
            self.backpropagation(winner)
        return self.root.find_max_score_child()
        



        