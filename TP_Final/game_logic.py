import numpy as np
import math
from typing import List, Tuple, Optional

class TicTacToeGame:
    def __init__(self):
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1  # 1 for X, -1 for O
        self.game_over = False
        self.winner = None
        
    def reset(self):
        """Reset the game to initial state"""
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        
    def make_move(self, row: int, col: int, player: int) -> bool:
        """Make a move on the board"""
        if self.board[row, col] == 0 and not self.game_over:
            self.board[row, col] = player
            self.check_game_over()
            return True
        return False
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves on the board"""
        moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    moves.append((i, j))
        return moves
    
    def check_winner(self) -> Optional[int]:
        """Check if there's a winner"""
        # Check rows
        for i in range(3):
            if abs(sum(self.board[i, :])) == 3:
                return self.board[i, 0]
        
        # Check columns
        for j in range(3):
            if abs(sum(self.board[:, j])) == 3:
                return self.board[0, j]
        
        # Check diagonals
        if abs(sum([self.board[i, i] for i in range(3)])) == 3:
            return self.board[0, 0]
        
        if abs(sum([self.board[i, 2-i] for i in range(3)])) == 3:
            return self.board[0, 2]
        
        return None
    
    def is_board_full(self) -> bool:
        """Check if board is full"""
        return np.all(self.board != 0)
    
    def check_game_over(self):
        """Check if game is over"""
        winner = self.check_winner()
        if winner is not None:
            self.game_over = True
            self.winner = winner
        elif self.is_board_full():
            self.game_over = True
            self.winner = 0  # Draw
    
    def get_board_state(self) -> np.ndarray:
        """Get current board state"""
        return self.board.copy()
    
    def evaluate_position(self) -> int:
        """Evaluate current position for minimax"""
        winner = self.check_winner()
        if winner == 1:  # X wins
            return 10
        elif winner == -1:  # O wins
            return -10
        else:
            return 0  # Draw or ongoing


class MinimaxAI:
    def __init__(self, depth: int = 9):
        self.depth = depth
        self.nodes_evaluated = 0
        
    def minimax(self, game: TicTacToeGame, depth: int, is_maximizing: bool, 
                alpha: float = -math.inf, beta: float = math.inf) -> int:
        """Minimax algorithm with alpha-beta pruning"""
        self.nodes_evaluated += 1
        
        winner = game.check_winner()
        if winner is not None:
            if winner == 1:  # X wins
                return 10 - (self.depth - depth)
            elif winner == -1:  # O wins
                return -10 + (self.depth - depth)
            else:  # Draw
                return 0
        
        if depth == 0 or game.is_board_full():
            return 0
        
        if is_maximizing:
            max_eval = -math.inf
            for row, col in game.get_valid_moves():
                # Make move
                game.board[row, col] = 1
                eval_score = self.minimax(game, depth - 1, False, alpha, beta)
                # Undo move
                game.board[row, col] = 0
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
                    
            return max_eval
        else:
            min_eval = math.inf
            for row, col in game.get_valid_moves():
                # Make move
                game.board[row, col] = -1
                eval_score = self.minimax(game, depth - 1, True, alpha, beta)
                # Undo move
                game.board[row, col] = 0
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
                    
            return min_eval
    
    def get_best_move(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Get the best move using minimax with alpha-beta pruning"""
        self.nodes_evaluated = 0
        best_move = None
        
        if player == 1:  # Maximizing player
            best_score = -math.inf
            for row, col in game.get_valid_moves():
                game.board[row, col] = 1
                score = self.minimax(game, self.depth - 1, False)
                game.board[row, col] = 0
                
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
        else:  # Minimizing player
            best_score = math.inf
            for row, col in game.get_valid_moves():
                game.board[row, col] = -1
                score = self.minimax(game, self.depth - 1, True)
                game.board[row, col] = 0
                
                if score < best_score:
                    best_score = score
                    best_move = (row, col)
        
        return best_move if best_move else game.get_valid_moves()[0]
