#!/usr/bin/env python3
"""
Quick test script to verify GUI functionality
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def test_gui_import():
    """Test if GUI imports work correctly"""
    try:
        from gui import ModernTicTacToeGUI
        print("✅ GUI imports successful")
        return True
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        return False

def test_ai_import():
    """Test if AI modules import correctly"""
    try:
        from ai_player import HybridAI
        from game_logic import TicTacToeGame, MinimaxAI
        print("✅ AI modules import successful")
        return True
    except Exception as e:
        print(f"❌ AI import failed: {e}")
        return False

def test_models_exist():
    """Test if trained models exist"""
    nn_exists = os.path.exists('models/best_nn_model.pth')
    rf_exists = os.path.exists('models/random_forest_model.joblib')
    
    if nn_exists and rf_exists:
        print("✅ Both trained models found")
        return True
    elif nn_exists or rf_exists:
        print("⚠️  Some models found, game will work with reduced AI capabilities")
        return True
    else:
        print("⚠️  No trained models found, game will use minimax only")
        return True

def quick_ai_test():
    """Quick test of AI functionality"""
    try:
        from game_logic import TicTacToeGame
        from ai_player import HybridAI
        
        game = TicTacToeGame()
        ai = HybridAI(difficulty='hard')
        
        # Test AI move
        move = ai.get_move(game, 1)
        if move and len(move) == 2:
            print("✅ AI move generation works")
            return True
        else:
            print("❌ AI move generation failed")
            return False
    except Exception as e:
        print(f"❌ AI test failed: {e}")
        return False

def test_tkinter():
    """Test if tkinter works"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide window
        root.destroy()
        print("✅ Tkinter works correctly")
        return True
    except Exception as e:
        print(f"❌ Tkinter test failed: {e}")
        return False

def main():
    print("🧪 Testing AI Tic-Tac-Toe Components")
    print("=" * 40)
    
    tests = [
        ("Tkinter availability", test_tkinter),
        ("GUI imports", test_gui_import),
        ("AI imports", test_ai_import),
        ("Model files", test_models_exist),
        ("AI functionality", quick_ai_test),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The game should work perfectly.")
        print("\n🚀 Run 'python main.py' to start the game!")
    elif passed >= total - 1:
        print("✅ Most tests passed! The game should work well.")
        print("\n🚀 Run 'python main.py' to start the game!")
    else:
        print("⚠️  Some issues detected. The game may have limited functionality.")
        print("\n💡 Try running 'python main.py --train' first if models are missing.")

if __name__ == "__main__":
    main()
