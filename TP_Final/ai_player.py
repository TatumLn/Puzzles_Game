import numpy as np
import torch
import torch.nn as nn
import joblib
import random
import os
import math
from typing import Dict, List, Tuple
from game_logic import TicTacToeGame, MinimaxAI
from dataset_generator import TicTacToeNN

class HybridAI:
    def __init__(self, difficulty='hard'):
        self.difficulty = difficulty
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Enhanced AI parameters
        self.opening_book = self._create_opening_book()
        self.position_values = self._create_position_values()
        self.threat_patterns = self._create_threat_patterns()
        
        # Load trained models
        self.nn_model = None
        self.rf_model = None
        self.minimax_ai = MinimaxAI(depth=9)
        self.enhanced_minimax = EnhancedMinimaxAI(depth=12)  # Deeper search
        
        # Load neural network model
        try:
            self.nn_model = TicTacToeNN().to(self.device)
            self.nn_model.load_state_dict(torch.load('models/best_nn_model.pth', map_location=self.device))
            self.nn_model.eval()
            print("Neural network model loaded successfully")
        except Exception as e:
            print(f"Could not load neural network model: {e}")
        
        # Load random forest model
        try:
            self.rf_model = joblib.load('models/random_forest_model.joblib')
            print("Random forest model loaded successfully")
        except Exception as e:
            print(f"Could not load random forest model: {e}")
    
    def _create_opening_book(self) -> Dict[str, Tuple[int, int]]:
        """Create opening book with optimal first moves"""
        return {
            # Empty board - take center
            '000000000': (1, 1),
            # If center taken, take corner
            '000010000': (0, 0),
            '100010000': (2, 2),
            '010010000': (0, 2),
            '001010000': (2, 0),
            # Counter opponent corners
            '100000000': (1, 1),  # Opponent takes corner, take center
            '001000000': (1, 1),
            '000000100': (1, 1),
            '000000001': (1, 1),
        }
    
    def _create_position_values(self) -> np.ndarray:
        """Create position value matrix for strategic evaluation"""
        # Higher values for strategic positions
        return np.array([
            [3, 2, 3],  # Corners and edges
            [2, 4, 2],  # Center is most valuable
            [3, 2, 3]
        ])
    
    def _create_threat_patterns(self) -> List[List[Tuple[int, int]]]:
        """Create threat detection patterns"""
        return [
            # Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # Diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
    
    def get_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Get the best move using hybrid approach"""
        if self.difficulty == 'easy':
            return self._get_easy_move(game, player)
        elif self.difficulty == 'medium':
            return self._get_medium_move(game, player)
        else:  # hard
            return self._get_hard_move(game, player)
    
    def _get_easy_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Easy AI - mostly random with some basic strategy"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 30% chance to use minimax, 70% random
        if random.random() < 0.3:
            return self.minimax_ai.get_best_move(game, player)
        else:
            return random.choice(valid_moves)
    
    def _get_medium_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Medium AI - mix of ML models and minimax"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 40% ML models, 40% minimax, 20% random
        choice = random.random()
        
        if choice < 0.4 and (self.nn_model or self.rf_model):
            return self._get_ml_move(game, player)
        elif choice < 0.8:
            return self.minimax_ai.get_best_move(game, player)
        else:
            return random.choice(valid_moves)
    
    def _get_hard_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Hard AI - advanced strategic play with multiple algorithms"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 1. Check opening book for early game
        opening_move = self._get_opening_move(game, player)
        if opening_move:
            return opening_move
        
        # 2. Immediate win detection
        win_move = self._find_winning_move(game, player)
        if win_move:
            return win_move
        
        # 3. Block opponent wins
        block_move = self._find_blocking_move(game, player)
        if block_move:
            return block_move
        
        # 4. Advanced threat analysis
        threat_move = self._analyze_threats(game, player)
        if threat_move:
            return threat_move
        
        # 5. Use enhanced minimax with deeper search
        enhanced_move = self.enhanced_minimax.get_best_move(game, player)
        if enhanced_move and enhanced_move in valid_moves:
            return enhanced_move
        
        # 6. Try ML models for complex positions
        if self.nn_model or self.rf_model:
            ml_move = self._get_ml_move(game, player)
            if ml_move and ml_move in valid_moves:
                return ml_move
        
        # 7. Strategic positioning as fallback
        return self._get_strategic_move(game, player)
    
    def _get_ml_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Get move using machine learning models"""
        board_state = game.get_board_state().flatten()
        
        # Adjust board state for player perspective
        if player == -1:
            board_state = -board_state
        
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # Try neural network first
        if self.nn_model:
            try:
                with torch.no_grad():
                    input_tensor = torch.FloatTensor(board_state).unsqueeze(0).to(self.device)
                    outputs = self.nn_model(input_tensor)
                    probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
                    
                    # Sort moves by probability
                    move_probs = [(i, probabilities[i]) for i in range(9)]
                    move_probs.sort(key=lambda x: x[1], reverse=True)
                    
                    # Return first valid move
                    for move_idx, prob in move_probs:
                        row, col = move_idx // 3, move_idx % 3
                        if (row, col) in valid_moves:
                            return (row, col)
            except Exception as e:
                print(f"Error using neural network: {e}")
        
        # Try random forest as backup
        if self.rf_model:
            try:
                predicted_move = self.rf_model.predict([board_state])[0]
                row, col = predicted_move // 3, predicted_move % 3
                if (row, col) in valid_moves:
                    return (row, col)
                
                # If predicted move is invalid, try other predictions
                probabilities = self.rf_model.predict_proba([board_state])[0]
                move_probs = [(i, probabilities[i]) for i in range(9)]
                move_probs.sort(key=lambda x: x[1], reverse=True)
                
                for move_idx, prob in move_probs:
                    row, col = move_idx // 3, move_idx % 3
                    if (row, col) in valid_moves:
                        return (row, col)
            except Exception as e:
                print(f"Error using random forest: {e}")
        
        # Final fallback to random
        return random.choice(valid_moves)
    
    def _get_opening_move(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Get move from opening book"""
        board_state = ''.join(['1' if x == player else '2' if x == -player else '0' 
                              for x in game.get_board_state().flatten()])
        
        # Check if position is in opening book
        if board_state in self.opening_book:
            move = self.opening_book[board_state]
            if move in game.get_valid_moves():
                return move
        return None
    
    def _analyze_threats(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Advanced threat analysis for tactical play"""
        board = game.get_board_state()
        opponent = -player
        
        # Look for fork opportunities (creating two threats)
        for row, col in game.get_valid_moves():
            test_board = board.copy()
            test_board[row, col] = player
            
            # Count threats this move creates
            threats = self._count_threats(test_board, player)
            if threats >= 2:  # Fork opportunity
                return (row, col)
        
        # Block opponent forks
        for row, col in game.get_valid_moves():
            test_board = board.copy()
            test_board[row, col] = opponent
            
            threats = self._count_threats(test_board, opponent)
            if threats >= 2:  # Block opponent fork
                return (row, col)
        
        return None
    
    def _count_threats(self, board: np.ndarray, player: int) -> int:
        """Count number of threats (two in a row with empty third)"""
        threats = 0
        
        for pattern in self.threat_patterns:
            values = [board[pos[0], pos[1]] for pos in pattern]
            if values.count(player) == 2 and values.count(0) == 1:
                threats += 1
        
        return threats
    
    def _get_strategic_move(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Get move based on strategic position values"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # Calculate move scores based on position values
        move_scores = []
        for row, col in valid_moves:
            score = self.position_values[row, col]
            
            # Bonus for creating multiple potential lines
            test_game = TicTacToeGame()
            test_game.board = game.board.copy()
            test_game.make_move(row, col, player)
            
            # Add strategic bonuses
            if (row, col) == (1, 1):  # Center bonus
                score += 2
            elif (row, col) in [(0, 0), (0, 2), (2, 0), (2, 2)]:  # Corner bonus
                score += 1
            
            move_scores.append(((row, col), score))
        
        # Return move with highest score
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return move_scores[0][0]
    
    def _find_winning_move(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Find a move that wins the game immediately"""
        for row, col in game.get_valid_moves():
            test_game = TicTacToeGame()
            test_game.board = game.board.copy()
            test_game.make_move(row, col, player)
            if test_game.check_winner() == player:
                return (row, col)
        return None
    
    def _find_blocking_move(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Find a move that blocks opponent's win"""
        opponent = -player
        for row, col in game.get_valid_moves():
            test_game = TicTacToeGame()
            test_game.board = game.board.copy()
            test_game.make_move(row, col, opponent)
            if test_game.check_winner() == opponent:
                return (row, col)
        return None
    
    def get_move_explanation(self, game: TicTacToeGame, player: int) -> str:
        """Get explanation of the AI's decision"""
        if self.difficulty == 'easy':
            return "Playing casually with basic strategy"
        elif self.difficulty == 'medium':
            return "Using balanced mix of strategies"
        else:
            return "Analyzing position with advanced AI algorithms and deep search"

class EnhancedMinimaxAI:
    """Enhanced Minimax AI with deeper search and better evaluation"""
    
    def __init__(self, depth: int = 12):
        self.depth = depth
        self.nodes_evaluated = 0
        self.transposition_table = {}  # Cache for positions
        
    def get_best_move(self, game: TicTacToeGame, player: int) -> Tuple[int, int]:
        """Get the best move using enhanced minimax"""
        self.nodes_evaluated = 0
        self.transposition_table.clear()
        
        best_move = None
        best_score = -math.inf if player == 1 else math.inf
        
        for row, col in game.get_valid_moves():
            game.board[row, col] = player
            
            if player == 1:  # Maximizing player
                score = self._minimax_enhanced(game, self.depth - 1, False, -math.inf, math.inf, -player)
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
            else:  # Minimizing player
                score = self._minimax_enhanced(game, self.depth - 1, True, -math.inf, math.inf, -player)
                if score < best_score:
                    best_score = score
                    best_move = (row, col)
            
            game.board[row, col] = 0  # Undo move
        
        return best_move if best_move else game.get_valid_moves()[0]
    
    def _minimax_enhanced(self, game: TicTacToeGame, depth: int, is_maximizing: bool, 
                         alpha: float, beta: float, current_player: int) -> float:
        """Enhanced minimax with transposition table and better evaluation"""
        self.nodes_evaluated += 1
        
        # Generate position key for transposition table
        position_key = self._get_position_key(game.board, current_player, depth)
        if position_key in self.transposition_table:
            return self.transposition_table[position_key]
        
        # Terminal state check
        winner = game.check_winner()
        if winner is not None:
            score = self._evaluate_terminal(winner, depth)
            self.transposition_table[position_key] = score
            return score
        
        if depth == 0 or game.is_board_full():
            score = self._evaluate_position(game, current_player)
            self.transposition_table[position_key] = score
            return score
        
        if is_maximizing:
            max_eval = -math.inf
            for row, col in self._get_ordered_moves(game, current_player):
                game.board[row, col] = current_player
                eval_score = self._minimax_enhanced(game, depth - 1, False, alpha, beta, -current_player)
                game.board[row, col] = 0
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            self.transposition_table[position_key] = max_eval
            return max_eval
        else:
            min_eval = math.inf
            for row, col in self._get_ordered_moves(game, current_player):
                game.board[row, col] = current_player
                eval_score = self._minimax_enhanced(game, depth - 1, True, alpha, beta, -current_player)
                game.board[row, col] = 0
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            self.transposition_table[position_key] = min_eval
            return min_eval
    
    def _get_position_key(self, board: np.ndarray, player: int, depth: int) -> str:
        """Generate unique key for position caching"""
        return f"{board.tobytes()}_{player}_{depth}"
    
    def _evaluate_terminal(self, winner: int, depth: int) -> float:
        """Evaluate terminal positions with depth consideration"""
        if winner == 1:  # X wins
            return 1000 - (self.depth - depth)  # Prefer quicker wins
        elif winner == -1:  # O wins
            return -1000 + (self.depth - depth)  # Prefer to delay losses
        else:  # Draw
            return 0
    
    def _evaluate_position(self, game: TicTacToeGame, player: int) -> float:
        """Enhanced position evaluation function"""
        board = game.board
        score = 0
        
        # Position values matrix
        position_values = np.array([
            [3, 2, 3],
            [2, 4, 2], 
            [3, 2, 3]
        ])
        
        # Evaluate based on piece positions
        for i in range(3):
            for j in range(3):
                if board[i, j] == player:
                    score += position_values[i, j]
                elif board[i, j] == -player:
                    score -= position_values[i, j]
        
        # Evaluate potential lines
        lines = [
            # Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # Diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
        
        for line in lines:
            line_score = self._evaluate_line(board, line, player)
            score += line_score
        
        return score
    
    def _evaluate_line(self, board: np.ndarray, line: List[Tuple[int, int]], player: int) -> float:
        """Evaluate a single line (row, column, or diagonal)"""
        player_count = 0
        opponent_count = 0
        empty_count = 0
        
        for row, col in line:
            if board[row, col] == player:
                player_count += 1
            elif board[row, col] == -player:
                opponent_count += 1
            else:
                empty_count += 1
        
        # Can't use this line if opponent has pieces in it
        if player_count > 0 and opponent_count > 0:
            return 0
        
        # Score based on how many pieces we have in line
        if player_count == 2 and empty_count == 1:
            return 50  # One move to win
        elif player_count == 1 and empty_count == 2:
            return 10  # Potential line
        elif opponent_count == 2 and empty_count == 1:
            return -50  # Must block
        elif opponent_count == 1 and empty_count == 2:
            return -10  # Opponent potential
        
        return 0
    
    def _get_ordered_moves(self, game: TicTacToeGame, player: int) -> List[Tuple[int, int]]:
        """Get moves ordered by likely strength for better pruning"""
        moves = game.get_valid_moves()
        
        # Order moves by strategic value (center, corners, edges)
        move_priorities = []
        for row, col in moves:
            priority = 0
            
            # Center is highest priority
            if (row, col) == (1, 1):
                priority = 100
            # Corners are next
            elif (row, col) in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                priority = 50
            # Edges are lowest
            else:
                priority = 10
            
            # Check if move creates immediate threats
            test_game = TicTacToeGame()
            test_game.board = game.board.copy()
            test_game.make_move(row, col, player)
            
            if test_game.check_winner() == player:
                priority = 1000  # Winning move
            elif self._creates_threat(test_game.board, row, col, player):
                priority += 25  # Threat creation bonus
            
            move_priorities.append(((row, col), priority))
        
        # Sort by priority (highest first)
        move_priorities.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_priorities]
    
    def _creates_threat(self, board: np.ndarray, row: int, col: int, player: int) -> bool:
        """Check if a move creates a threat (two in a row)"""
        # Check all lines through this position
        lines_through_position = []
        
        # Row
        lines_through_position.append([(row, 0), (row, 1), (row, 2)])
        # Column  
        lines_through_position.append([(0, col), (1, col), (2, col)])
        # Diagonals
        if row == col:
            lines_through_position.append([(0, 0), (1, 1), (2, 2)])
        if row + col == 2:
            lines_through_position.append([(0, 2), (1, 1), (2, 0)])
        
        for line in lines_through_position:
            player_count = sum(1 for r, c in line if board[r, c] == player)
            empty_count = sum(1 for r, c in line if board[r, c] == 0)
            
            if player_count == 2 and empty_count == 1:
                return True  # This creates a threat
        
        return False

class SmartAI:
    """Alternative AI implementation focusing on strategic play"""
    
    def __init__(self):
        self.minimax_ai = MinimaxAI(depth=9)
    
    def get_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Get move using strategic priorities"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # Priority 1: Win if possible
        win_move = self._find_winning_move(game, player)
        if win_move:
            return win_move
        
        # Priority 2: Block opponent's winning move
        block_move = self._find_blocking_move(game, player)
        if block_move:
            return block_move
        
        # Priority 3: Take center if available
        if (1, 1) in valid_moves:
            return (1, 1)
        
        # Priority 4: Take corners
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [move for move in corners if move in valid_moves]
        if available_corners:
            return random.choice(available_corners)
        
        # Priority 5: Use minimax for complex positions
        return self.minimax_ai.get_best_move(game, player)
    
    def _find_winning_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Find a move that wins the game"""
        for row, col in game.get_valid_moves():
            test_game = TicTacToeGame()
            test_game.board = game.board.copy()
            test_game.make_move(row, col, player)
            if test_game.check_winner() == player:
                return (row, col)
        return None
    
    def _find_blocking_move(self, game: TicTacToeGame, player: int) -> tuple:
        """Find a move that blocks opponent's win"""
        opponent = -player
        for row, col in game.get_valid_moves():
            test_game = TicTacToeGame()
            test_game.board = game.board.copy()
            test_game.make_move(row, col, opponent)
            if test_game.check_winner() == opponent:
                return (row, col)
        return None
