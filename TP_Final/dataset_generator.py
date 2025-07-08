import numpy as np
import pandas as pd
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from tqdm import tqdm
import os
from game_logic import TicTacToeGame, MinimaxAI

class TicTacToeDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class TicTacToeNN(nn.Module):
    def __init__(self, input_size=9, hidden_size=128, num_classes=9):
        super(TicTacToeNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc4 = nn.Linear(hidden_size // 2, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.fc4(x)
        return x

class DatasetGenerator:
    def __init__(self):
        self.game = TicTacToeGame()
        self.minimax_ai = MinimaxAI(depth=9)
        self.data = []
        self.labels = []
        
    def generate_game_data(self, num_games: int = 10000):
        """Generate training data from games using minimax algorithm"""
        print(f"Generating {num_games} games for training data...")
        
        for game_idx in tqdm(range(num_games), desc="Generating games"):
            self.game.reset()
            game_positions = []
            
            while not self.game.game_over:
                current_state = self.game.get_board_state().flatten()
                
                # Get best move using minimax
                best_move = self.minimax_ai.get_best_move(self.game, self.game.current_player)
                
                # Convert move to position index (0-8)
                move_index = best_move[0] * 3 + best_move[1]
                
                # Store state and best move
                game_positions.append((current_state.copy(), move_index))
                
                # Make the move
                self.game.make_move(best_move[0], best_move[1], self.game.current_player)
                self.game.current_player *= -1
            
            # Add positions from this game to dataset
            for state, move in game_positions:
                self.data.append(state)
                self.labels.append(move)
            
            # Generate some random games for diversity
            if game_idx % 100 == 0:
                self.generate_random_game()
    
    def generate_random_game(self):
        """Generate a random game for data diversity"""
        self.game.reset()
        
        while not self.game.game_over:
            current_state = self.game.get_board_state().flatten()
            valid_moves = self.game.get_valid_moves()
            
            if valid_moves:
                # 70% chance to use minimax, 30% random
                if random.random() < 0.7:
                    best_move = self.minimax_ai.get_best_move(self.game, self.game.current_player)
                else:
                    best_move = random.choice(valid_moves)
                
                move_index = best_move[0] * 3 + best_move[1]
                
                self.data.append(current_state.copy())
                self.labels.append(move_index)
                
                self.game.make_move(best_move[0], best_move[1], self.game.current_player)
                self.game.current_player *= -1
    
    def generate_all_positions(self):
        """Generate all possible game positions systematically"""
        print("Generating all possible positions...")
        
        def generate_positions(board, player, depth=0):
            if depth > 8:  # Max 9 moves
                return
            
            current_game = TicTacToeGame()
            current_game.board = board.copy()
            current_game.current_player = player
            current_game.check_game_over()
            
            if current_game.game_over:
                return
            
            valid_moves = current_game.get_valid_moves()
            if not valid_moves:
                return
            
            # Get best move for current position
            best_move = self.minimax_ai.get_best_move(current_game, player)
            move_index = best_move[0] * 3 + best_move[1]
            
            # Store position and best move
            self.data.append(board.flatten().copy())
            self.labels.append(move_index)
            
            # Recursively generate positions for each possible move
            for row, col in valid_moves:
                new_board = board.copy()
                new_board[row, col] = player
                generate_positions(new_board, -player, depth + 1)
        
        # Start with empty board
        empty_board = np.zeros((3, 3), dtype=int)
        generate_positions(empty_board, 1)
    
    def save_dataset(self, filename: str = "tic_tac_toe_dataset.csv"):
        """Save dataset to CSV file"""
        if not self.data:
            print("No data to save. Generate data first.")
            return
        
        df = pd.DataFrame(self.data, columns=[f'pos_{i}' for i in range(9)])
        df['best_move'] = self.labels
        
        os.makedirs('data', exist_ok=True)
        df.to_csv(f'data/{filename}', index=False)
        print(f"Dataset saved to data/{filename}")
        print(f"Dataset size: {len(df)} samples")
    
    def load_dataset(self, filename: str = "tic_tac_toe_dataset.csv"):
        """Load dataset from CSV file"""
        try:
            df = pd.read_csv(f'data/{filename}')
            self.data = df.iloc[:, :9].values.tolist()
            self.labels = df['best_move'].values.tolist()
            print(f"Dataset loaded from data/{filename}")
            print(f"Dataset size: {len(self.data)} samples")
        except FileNotFoundError:
            print(f"Dataset file data/{filename} not found. Generate dataset first.")

class AITrainer:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    def train_neural_network(self, X_train, y_train, X_val, y_val):
        """Train neural network model on GPU"""
        print("Training Neural Network on GPU...")
        
        # Create datasets
        train_dataset = TicTacToeDataset(X_train, y_train)
        val_dataset = TicTacToeDataset(X_val, y_val)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=512, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=512, shuffle=False)
        
        # Initialize model
        model = TicTacToeNN().to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.1)
        
        # Training loop
        num_epochs = 200
        best_val_accuracy = 0
        
        for epoch in range(num_epochs):
            model.train()
            train_loss = 0.0
            train_correct = 0
            
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_correct += (predicted == batch_y).sum().item()
            
            # Validation
            model.eval()
            val_loss = 0.0
            val_correct = 0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    val_correct += (predicted == batch_y).sum().item()
            
            train_accuracy = train_correct / len(train_dataset)
            val_accuracy = val_correct / len(val_dataset)
            
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                os.makedirs('models', exist_ok=True)
                torch.save(model.state_dict(), 'models/best_nn_model.pth')
            
            scheduler.step()
            
            if epoch % 20 == 0:
                print(f'Epoch [{epoch}/{num_epochs}], Train Acc: {train_accuracy:.4f}, Val Acc: {val_accuracy:.4f}')
        
        print(f"Best validation accuracy: {best_val_accuracy:.4f}")
        return model
    
    def train_random_forest(self, X_train, y_train, X_val, y_val):
        """Train Random Forest model"""
        print("Training Random Forest...")
        
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = rf_model.predict(X_train)
        val_pred = rf_model.predict(X_val)
        
        train_accuracy = accuracy_score(y_train, train_pred)
        val_accuracy = accuracy_score(y_val, val_pred)
        
        print(f"Random Forest - Train Accuracy: {train_accuracy:.4f}")
        print(f"Random Forest - Validation Accuracy: {val_accuracy:.4f}")
        
        # Save model
        os.makedirs('models', exist_ok=True)
        joblib.dump(rf_model, 'models/random_forest_model.joblib')
        
        return rf_model

def main():
    # Generate dataset
    generator = DatasetGenerator()
    
    # Generate comprehensive training data
    generator.generate_game_data(num_games=5000)
    generator.generate_all_positions()
    
    # Save dataset
    generator.save_dataset()
    
    # Prepare data for training
    X = np.array(generator.data)
    y = np.array(generator.labels)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Validation set size: {len(X_val)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train models
    trainer = AITrainer()
    
    # Train Neural Network
    nn_model = trainer.train_neural_network(X_train, y_train, X_val, y_val)
    
    # Train Random Forest
    rf_model = trainer.train_random_forest(X_train, y_train, X_val, y_val)
    
    print("Training completed!")

if __name__ == "__main__":
    main()
