#!/usr/bin/env python3
"""
AI Tic-Tac-Toe Master
A comprehensive tic-tac-toe game with AI using machine learning and minimax algorithm.

Features:
- Modern GUI interface
- AI with multiple difficulty levels
- Machine learning trained on GPU
- Minimax algorithm with alpha-beta pruning
- Human vs Human and Human vs AI modes
- Game statistics tracking
"""

import os
import sys
import argparse
from pathlib import Path

def setup_environment():
    """Setup the project environment"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    print("🎮 AI Tic-Tac-Toe Master")
    print("=" * 50)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'numpy', 'pandas', 'torch', 'sklearn', 
        'joblib', 'tqdm', 'matplotlib', 'seaborn'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def train_models():
    """Train the AI models"""
    print("\n🤖 Training AI models...")
    try:
        from dataset_generator import main as train_main
        train_main()
        print("✅ Model training completed successfully!")
    except Exception as e:
        print(f"❌ Error during training: {e}")
        print("You can still play the game using the minimax algorithm.")

def run_gui():
    """Run the graphical user interface"""
    print("\n🚀 Starting GUI application...")
    try:
        from gui import ModernTicTacToeGUI
        app = ModernTicTacToeGUI()
        app.run()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        sys.exit(1)

def run_console_demo():
    """Run a console demo of the game"""
    print("\n🎲 Running console demo...")
    try:
        from game_logic import TicTacToeGame, MinimaxAI
        from ai_player import HybridAI
        
        game = TicTacToeGame()
        ai = HybridAI(difficulty='hard')
        
        print("\nDemo: AI vs AI")
        print("-" * 20)
        
        move_count = 0
        while not game.game_over and move_count < 9:
            print(f"\nMove {move_count + 1}:")
            print_board(game.board)
            
            # AI makes move
            move = ai.get_move(game, game.current_player)
            if move:
                game.make_move(move[0], move[1], game.current_player)
                player_symbol = 'X' if game.current_player == 1 else 'O'
                print(f"Player {player_symbol} plays at ({move[0]}, {move[1]})")
                game.current_player *= -1
            
            move_count += 1
        
        print("\nFinal board:")
        print_board(game.board)
        
        if game.winner == 1:
            print("🎉 X wins!")
        elif game.winner == -1:
            print("🎉 O wins!")
        else:
            print("🤝 It's a draw!")
            
    except Exception as e:
        print(f"❌ Error in console demo: {e}")

def print_board(board):
    """Print the game board to console"""
    symbols = {1: 'X', -1: 'O', 0: ' '}
    print("  0   1   2")
    for i in range(3):
        row = f"{i} "
        for j in range(3):
            row += f"{symbols[board[i,j]]}{'|' if j < 2 else ''}"
        print(row)
        if i < 2:
            print("  --|---|--")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='AI Tic-Tac-Toe Master')
    parser.add_argument('--train', action='store_true', 
                       help='Train AI models (requires GPU for optimal performance)')
    parser.add_argument('--demo', action='store_true',
                       help='Run console demo')
    parser.add_argument('--no-gui', action='store_true',
                       help='Skip GUI and run console demo')
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Tip: Install dependencies with:")
        print("pip install -r requirements.txt")
        return
    
    # Train models if requested
    if args.train:
        train_models()
        return
    
    # Run demo if requested
    if args.demo or args.no_gui:
        run_console_demo()
        return
    
    # Check if models exist, if not offer to train them
    if not os.path.exists('models/best_nn_model.pth') and not os.path.exists('models/random_forest_model.joblib'):
        print("\n⚠️  No trained models found.")
        print("The game will use the minimax algorithm, which is still very challenging!")
        print("\n💡 To train AI models, run: python main.py --train")
        print("(Training requires a GPU for optimal performance)")
        
        user_input = input("\nDo you want to train models now? (y/n): ").lower().strip()
        if user_input == 'y':
            train_models()
    
    # Run GUI
    run_gui()

if __name__ == "__main__":
    main()
