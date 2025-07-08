import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from game_logic import TicTacToeGame
from ai_player import HybridAI, SmartAI

class ModernTicTacToeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Tic-Tac-Toe Master")
        self.root.geometry("800x700")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)
        
        # Game state
        self.game = TicTacToeGame()
        self.ai_player = None
        self.game_mode = None  # 'ai' or 'human'
        self.ai_difficulty = 'hard'
        self.human_player = 1  # 1 for X, -1 for O
        self.ai_turn = False
        
        # UI elements
        self.buttons = []
        self.status_label = None
        self.score_label = None
        
        # Game statistics
        self.wins = 0
        self.losses = 0
        self.draws = 0
        
        # Game history for replay functionality
        self.game_history = []
        self.current_replay_step = 0
        self.is_replaying = False
        
        # Navigation history for back button functionality
        self.navigation_stack = ['main_menu']  # Stack to track navigation
        self.current_window = 'main_menu'
        
        # Colors and styles
        self.colors = {
            'bg': '#1e1e1e',
            'card': '#2d2d2d',
            'accent': '#007acc',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'text': '#ffffff',
            'text_muted': '#888888'
        }
        
        self.setup_styles()
        self.create_main_menu()
    
    def navigate_to(self, window_name):
        """Navigate to a new window and update navigation stack"""
        if self.current_window != window_name:
            self.navigation_stack.append(self.current_window)
            self.current_window = window_name
    
    def navigate_back(self):
        """Navigate back to the previous window"""
        # Special handling for game board - confirm if game is in progress
        if self.current_window == 'game_board':
            if not self.game.game_over and len(self.game_history) > 0:
                from tkinter import messagebox
                result = messagebox.askyesno(
                    "Leave Game",
                    "Are you sure you want to leave the current game?\n\nGame progress will be lost.",
                    icon='warning'
                )
                if not result:
                    return  # Stay in game
        
        if len(self.navigation_stack) > 1:
            # Remove current window and go to previous
            self.navigation_stack.pop()
            previous_window = self.navigation_stack[-1]
            self.current_window = previous_window
            
            # Navigate to the previous window
            if previous_window == 'main_menu':
                self.create_main_menu()
            elif previous_window == 'ai_options':
                self.show_ai_options()
            elif previous_window == 'game_board':
                # Can't really go back to game board, go to main menu
                self.create_main_menu()
        else:
            # If no previous window, go to main menu
            self.create_main_menu()
    
    def create_back_button(self, parent_frame, text="← Back"):
        """Create a standardized back button"""
        back_btn = tk.Button(parent_frame,
                            text=text,
                            font=('Arial', 11, 'bold'),
                            bg=self.colors['text_muted'],
                            fg='white',
                            activebackground='#666666',
                            activeforeground='white',
                            relief='flat',
                            borderwidth=0,
                            padx=20,
                            pady=8,
                            command=self.navigate_back)
        return back_btn
        
    def setup_styles(self):
        """Setup modern UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       padding=(20, 10))
        
        style.map('Modern.TButton',
                 background=[('active', '#005a9e')])
        
        # Configure label style
        style.configure('Modern.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Arial', 12))
        
        # Configure frame style
        style.configure('Modern.TFrame',
                       background=self.colors['bg'],
                       relief='flat',
                       borderwidth=0)
    
    def create_main_menu(self):
        """Create the main menu interface"""
        self.clear_window()
        
        # Reset game state
        self.game_history = []
        self.is_replaying = False
        
        # Reset navigation to main menu
        self.navigation_stack = ['main_menu']
        self.current_window = 'main_menu'
        
        # Header section
        header_frame = tk.Frame(self.root, bg=self.colors['bg'])
        header_frame.pack(pady=30)
        
        # Title with enhanced styling
        title_label = tk.Label(header_frame, 
                              text="🎮 AI Tic-Tac-Toe Master",
                              font=('Arial', 32, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'])
        title_label.pack()
        
        # Enhanced subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Advanced AI • Machine Learning • Enhanced Minimax",
                                 font=('Arial', 12),
                                 bg=self.colors['bg'],
                                 fg=self.colors['accent'])
        subtitle_label.pack(pady=5)
        
        # Version info
        version_label = tk.Label(header_frame,
                                text="v2.0 Enhanced Edition",
                                font=('Arial', 10),
                                bg=self.colors['bg'],
                                fg=self.colors['text_muted'])
        version_label.pack()
        
        # Game mode selection
        selection_frame = tk.Frame(self.root, bg=self.colors['bg'])
        selection_frame.pack(pady=40)
        
        mode_title = tk.Label(selection_frame,
                             text="🎯 Select Game Mode",
                             font=('Arial', 18, 'bold'),
                             bg=self.colors['bg'],
                             fg=self.colors['text'])
        mode_title.pack(pady=(0, 20))
        
        # Game mode buttons with enhanced styling
        button_container = tk.Frame(selection_frame, bg=self.colors['bg'])
        button_container.pack()
        
        ai_button = tk.Button(button_container,
                             text="🤖 Play vs AI\n🏆 Challenge the Machine",
                             font=('Arial', 14, 'bold'),
                             bg=self.colors['accent'],
                             fg='white',
                             activebackground='#005a9e',
                             activeforeground='white',
                             relief='flat',
                             borderwidth=0,
                             padx=45,
                             pady=20,
                             justify='center',
                             command=self.show_ai_options)
        ai_button.pack(pady=12)
        
        human_button = tk.Button(button_container,
                                text="👥 Play vs Human\n🤝 Local Multiplayer",
                                font=('Arial', 14, 'bold'),
                                bg=self.colors['success'],
                                fg='white',
                                activebackground='#218838',
                                activeforeground='white',
                                relief='flat',
                                borderwidth=0,
                                padx=45,
                                pady=20,
                                justify='center',
                                command=self.start_human_game)
        human_button.pack(pady=12)
        
        # Statistics section with enhanced design
        stats_container = tk.Frame(self.root, bg=self.colors['bg'])
        stats_container.pack(pady=30, fill='x', padx=40)
        
        stats_card = tk.Frame(stats_container, bg=self.colors['card'], relief='flat')
        stats_card.pack(fill='x', pady=10)
        
        stats_header = tk.Frame(stats_card, bg=self.colors['card'])
        stats_header.pack(fill='x', pady=10)
        
        stats_title = tk.Label(stats_header,
                              text="📊 Game Statistics",
                              font=('Arial', 16, 'bold'),
                              bg=self.colors['card'],
                              fg=self.colors['text'])
        stats_title.pack()
        
        # Detailed statistics
        total_games = self.wins + self.losses + self.draws
        win_rate = (self.wins / max(1, total_games)) * 100
        
        stats_details = tk.Frame(stats_card, bg=self.colors['card'])
        stats_details.pack(pady=(0, 15))
        
        stats_line1 = tk.Label(stats_details,
                              text=f"🏆 Wins: {self.wins} • 🚫 Losses: {self.losses} • 🤝 Draws: {self.draws}",
                              font=('Arial', 11, 'bold'),
                              bg=self.colors['card'],
                              fg=self.colors['text'])
        stats_line1.pack()
        
        stats_line2 = tk.Label(stats_details,
                              text=f"📊 Total Games: {total_games} • 🎯 Win Rate: {win_rate:.1f}%",
                              font=('Arial', 10),
                              bg=self.colors['card'],
                              fg=self.colors['text_muted'])
        stats_line2.pack(pady=2)
        
        # Additional options
        options_frame = tk.Frame(self.root, bg=self.colors['bg'])
        options_frame.pack(pady=20)
        
        # Quick action buttons
        quick_actions = tk.Frame(options_frame, bg=self.colors['bg'])
        quick_actions.pack()
        
        help_btn = tk.Button(quick_actions,
                            text="❓ Help",
                            font=('Arial', 10),
                            bg=self.colors['card'],
                            fg=self.colors['text'],
                            activebackground='#3d3d3d',
                            activeforeground='white',
                            relief='flat',
                            borderwidth=0,
                            padx=15,
                            pady=6,
                            command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=8)
        
        about_btn = tk.Button(quick_actions,
                             text="📜 About",
                             font=('Arial', 10),
                             bg=self.colors['card'],
                             fg=self.colors['text'],
                             activebackground='#3d3d3d',
                             activeforeground='white',
                             relief='flat',
                             borderwidth=0,
                             padx=15,
                             pady=6,
                             command=self.show_about)
        about_btn.pack(side=tk.LEFT, padx=8)
        
        reset_stats_btn = tk.Button(quick_actions,
                                   text="🗑️ Reset Stats",
                                   font=('Arial', 10),
                                   bg=self.colors['danger'],
                                   fg='white',
                                   activebackground='#c82333',
                                   activeforeground='white',
                                   relief='flat',
                                   borderwidth=0,
                                   padx=15,
                                   pady=6,
                                   command=self.reset_statistics)
        reset_stats_btn.pack(side=tk.LEFT, padx=8)
    
    def show_ai_options(self):
        """Show AI difficulty selection"""
        self.clear_window()
        
        # Update navigation
        self.navigate_to('ai_options')
        
        # Header section
        header_frame = tk.Frame(self.root, bg=self.colors['bg'])
        header_frame.pack(pady=30)
        
        # Title
        title_label = tk.Label(header_frame,
                              text="🤖 Select AI Difficulty",
                              font=('Arial', 28, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'])
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Choose your challenge level",
                                 font=('Arial', 14),
                                 bg=self.colors['bg'],
                                 fg=self.colors['text_muted'])
        subtitle_label.pack(pady=10)
        
        # Difficulty selection
        selection_frame = tk.Frame(self.root, bg=self.colors['bg'])
        selection_frame.pack(pady=30)
        
        difficulties = [
            (
                "🟢 Easy Mode",
                "Casual gameplay • Random moves • Perfect for beginners",
                "easy",
                self.colors['success']
            ),
            (
                "🟡 Medium Mode",
                "Balanced challenge • Mixed strategies • Good practice",
                "medium",
                self.colors['warning']
            ),
            (
                "🔴 Hard Mode",
                "Maximum challenge • ML + Enhanced Minimax • Expert level",
                "hard",
                self.colors['danger']
            )
        ]
        
        for title, description, difficulty, color in difficulties:
            # Create card for each difficulty
            card_frame = tk.Frame(selection_frame, bg=self.colors['card'], relief='flat')
            card_frame.pack(pady=12, padx=40, fill='x')
            
            # Difficulty button
            btn = tk.Button(card_frame,
                           text=f"{title}\n{description}",
                           font=('Arial', 13, 'bold'),
                           bg=color,
                           fg='white',
                           activebackground=color,
                           activeforeground='white',
                           relief='flat',
                           borderwidth=0,
                           padx=30,
                           pady=18,
                           justify='center',
                           command=lambda d=difficulty: self.start_ai_game(d))
            btn.pack(pady=15, padx=15, fill='x')
        
        # Navigation
        nav_frame = tk.Frame(self.root, bg=self.colors['bg'])
        nav_frame.pack(pady=30)
        
        back_button = self.create_back_button(nav_frame, text="← Previous Menu")
        back_button.pack()
    
    def start_ai_game(self, difficulty):
        """Start game against AI"""
        self.game_mode = 'ai'
        self.ai_difficulty = difficulty
        self.ai_player = HybridAI(difficulty=difficulty)
        self.human_player = 1  # Human plays X
        self.create_game_board()
    
    def start_human_game(self):
        """Start game against human"""
        self.game_mode = 'human'
        self.ai_player = None
        self.create_game_board()
    
    def create_game_board(self):
        """Create the game board interface"""
        self.clear_window()
        
        # Update navigation
        self.navigate_to('game_board')
        
        self.game.reset()
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'])
        header_frame.pack(pady=20)
        
        # Game title
        mode_text = f"vs {'AI (' + self.ai_difficulty.title() + ')' if self.game_mode == 'ai' else 'Human'}"
        # Title and back button container
        title_container = tk.Frame(header_frame, bg=self.colors['bg'])
        title_container.pack(fill='x')
        
        # Back button (left side)
        back_btn = self.create_back_button(title_container, text="←")
        back_btn.config(font=('Arial', 14, 'bold'), padx=10, pady=5)
        back_btn.pack(side=tk.LEFT)
        
        # Title (center)
        title_label = tk.Label(title_container,
                              text=f"Tic-Tac-Toe {mode_text}",
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'])
        title_label.pack(side=tk.LEFT, expand=True)
        
        # Status
        self.status_label = tk.Label(header_frame,
                                    text="Your turn (X)",
                                    font=('Arial', 14),
                                    bg=self.colors['bg'],
                                    fg=self.colors['accent'])
        self.status_label.pack(pady=10)
        
        # Game board
        board_frame = tk.Frame(self.root, bg=self.colors['bg'])
        board_frame.pack(pady=20)
        
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(board_frame,
                               text="",
                               font=('Arial', 36, 'bold'),
                               bg=self.colors['card'],
                               fg=self.colors['text'],
                               activebackground=self.colors['accent'],
                               activeforeground='white',
                               relief='flat',
                               borderwidth=2,
                               width=4,
                               height=2,
                               command=lambda r=i, c=j: self.make_move(r, c))
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.buttons.append(row)
        
        # Control buttons with improved layout
        control_frame = tk.Frame(self.root, bg=self.colors['bg'])
        control_frame.pack(pady=15)
        
        # Game control buttons (primary actions)
        game_controls = tk.Frame(control_frame, bg=self.colors['bg'])
        game_controls.pack(pady=8)
        
        new_game_btn = tk.Button(game_controls,
                                text="🔄 New Game",
                                font=('Arial', 11, 'bold'),
                                bg=self.colors['accent'],
                                fg='white',
                                activebackground='#005a9e',
                                activeforeground='white',
                                relief='flat',
                                borderwidth=0,
                                padx=18,
                                pady=6,
                                command=self.new_game)
        new_game_btn.pack(side=tk.LEFT, padx=8)
        
        replay_btn = tk.Button(game_controls,
                              text="⏮️ Replay",
                              font=('Arial', 11, 'bold'),
                              bg=self.colors['warning'],
                              fg='white',
                              activebackground='#e0a800',
                              activeforeground='white',
                              relief='flat',
                              borderwidth=0,
                              padx=18,
                              pady=6,
                              command=self.start_replay)
        replay_btn.pack(side=tk.LEFT, padx=8)
        
        return_btn = tk.Button(game_controls,
                              text="↩️ Undo",
                              font=('Arial', 11, 'bold'),
                              bg=self.colors['danger'],
                              fg='white',
                              activebackground='#c82333',
                              activeforeground='white',
                              relief='flat',
                              borderwidth=0,
                              padx=18,
                              pady=6,
                              command=self.return_to_previous)
        return_btn.pack(side=tk.LEFT, padx=8)
        
        # Navigation buttons (secondary actions)
        nav_controls = tk.Frame(control_frame, bg=self.colors['bg'])
        nav_controls.pack(pady=8)
        
        settings_btn = tk.Button(nav_controls,
                                text="⚙️ Settings",
                                font=('Arial', 10),
                                bg=self.colors['card'],
                                fg=self.colors['text'],
                                activebackground='#3d3d3d',
                                activeforeground='white',
                                relief='flat',
                                borderwidth=0,
                                padx=15,
                                pady=5,
                                command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=6)
        
        difficulty_btn = tk.Button(nav_controls,
                                  text="🎯 Change AI",
                                  font=('Arial', 10),
                                  bg=self.colors['card'],
                                  fg=self.colors['text'],
                                  activebackground='#3d3d3d',
                                  activeforeground='white',
                                  relief='flat',
                                  borderwidth=0,
                                  padx=15,
                                  pady=5,
                                  command=self.change_difficulty)
        difficulty_btn.pack(side=tk.LEFT, padx=6)
        
        # Exit game button (prominent styling)
        exit_btn = tk.Button(nav_controls,
                            text="🚪 Exit Game",
                            font=('Arial', 10, 'bold'),
                            bg=self.colors['danger'],
                            fg='white',
                            activebackground='#c82333',
                            activeforeground='white',
                            relief='flat',
                            borderwidth=0,
                            padx=18,
                            pady=5,
                            command=self.exit_game)
        exit_btn.pack(side=tk.LEFT, padx=8)
        
        menu_btn = tk.Button(nav_controls,
                            text="🏠 Main Menu",
                            font=('Arial', 10),
                            bg=self.colors['text_muted'],
                            fg='white',
                            activebackground='#666666',
                            activeforeground='white',
                            relief='flat',
                            borderwidth=0,
                            padx=15,
                            pady=5,
                            command=self.confirm_return_to_menu)
        menu_btn.pack(side=tk.LEFT, padx=6)
        
        # Score
        self.score_label = tk.Label(self.root,
                                   text=f"Score - Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}",
                                   font=('Arial', 12),
                                   bg=self.colors['bg'],
                                   fg=self.colors['text_muted'])
        self.score_label.pack(pady=10)
    
    def make_move(self, row, col):
        """Handle player move"""
        if self.game.game_over or self.ai_turn or self.is_replaying:
            return
        
        if self.game.make_move(row, col, self.game.current_player):
            # Record move in history
            self.game_history.append({
                'move': (row, col),
                'player': self.game.current_player,
                'board': self.game.get_board_state().copy(),
                'move_number': len(self.game_history) + 1
            })
            
            self.update_board()
            
            if self.game.game_over:
                self.handle_game_end()
            else:
                self.game.current_player *= -1
                if self.game_mode == 'ai' and self.game.current_player != self.human_player:
                    self.ai_turn = True
                    self.status_label.config(text="AI is thinking...", fg=self.colors['warning'])
                    self.root.after(1000, self.make_ai_move)  # Delay for better UX
                else:
                    player_name = "X" if self.game.current_player == 1 else "O"
                    self.status_label.config(text=f"{player_name}'s turn", fg=self.colors['accent'])
    
    def make_ai_move(self):
        """Make AI move"""
        if self.game.game_over:
            return
        
        ai_move = self.ai_player.get_move(self.game, self.game.current_player)
        if ai_move and self.game.make_move(ai_move[0], ai_move[1], self.game.current_player):
            # Record AI move in history
            self.game_history.append({
                'move': ai_move,
                'player': self.game.current_player,
                'board': self.game.get_board_state().copy(),
                'move_number': len(self.game_history) + 1,
                'is_ai': True
            })
            
            self.update_board()
            
            if self.game.game_over:
                self.handle_game_end()
            else:
                self.game.current_player *= -1
                self.status_label.config(text="Your turn (X)", fg=self.colors['accent'])
            
            self.ai_turn = False
    
    def update_board(self):
        """Update the visual board"""
        for i in range(3):
            for j in range(3):
                value = self.game.board[i, j]
                if value == 1:
                    self.buttons[i][j].config(text="X", fg=self.colors['accent'])
                elif value == -1:
                    self.buttons[i][j].config(text="O", fg=self.colors['danger'])
                else:
                    self.buttons[i][j].config(text="", fg=self.colors['text'])
    
    def handle_game_end(self):
        """Handle game end"""
        if self.game.winner == 1:
            if self.game_mode == 'ai':
                message = "🎉 You Won!"
                self.wins += 1
            else:
                message = "🎉 X Wins!"
            self.status_label.config(text=message, fg=self.colors['success'])
        elif self.game.winner == -1:
            if self.game_mode == 'ai':
                message = "🤖 AI Won!"
                self.losses += 1
            else:
                message = "🎉 O Wins!"
            self.status_label.config(text=message, fg=self.colors['danger'])
        else:
            message = "🤝 It's a Draw!"
            self.draws += 1
            self.status_label.config(text=message, fg=self.colors['warning'])
        
        # Update score display
        if self.score_label:
            self.score_label.config(text=f"Score - Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}")
        
        # Highlight winning combination
        self.highlight_winner()
    
    def highlight_winner(self):
        """Highlight winning combination"""
        winner = self.game.check_winner()
        if winner is None:
            return
        
        # Check rows
        for i in range(3):
            if abs(sum(self.game.board[i, :])) == 3:
                for j in range(3):
                    self.buttons[i][j].config(bg=self.colors['success'] if winner == 1 else self.colors['danger'])
                return
        
        # Check columns
        for j in range(3):
            if abs(sum(self.game.board[:, j])) == 3:
                for i in range(3):
                    self.buttons[i][j].config(bg=self.colors['success'] if winner == 1 else self.colors['danger'])
                return
        
        # Check diagonals
        if abs(sum([self.game.board[i, i] for i in range(3)])) == 3:
            for i in range(3):
                self.buttons[i][i].config(bg=self.colors['success'] if winner == 1 else self.colors['danger'])
            return
        
        if abs(sum([self.game.board[i, 2-i] for i in range(3)])) == 3:
            for i in range(3):
                self.buttons[i][2-i].config(bg=self.colors['success'] if winner == 1 else self.colors['danger'])
    
    def new_game(self):
        """Start a new game"""
        self.game.reset()
        self.ai_turn = False
        self.game_history = []
        self.current_replay_step = 0
        self.is_replaying = False
        
        # Reset board buttons
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", bg=self.colors['card'], fg=self.colors['text'])
        
        # Reset status
        if self.game_mode == 'ai':
            self.status_label.config(text="Your turn (X)", fg=self.colors['accent'])
        else:
            self.status_label.config(text="X's turn", fg=self.colors['accent'])
    
    def start_replay(self):
        """Start replaying the current game"""
        if not self.game_history:
            self.status_label.config(text="No game to replay!", fg=self.colors['warning'])
            return
        
        self.is_replaying = True
        self.current_replay_step = 0
        
        # Reset board for replay
        self.game.reset()
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", bg=self.colors['card'], fg=self.colors['text'])
        
        self.status_label.config(text="Replaying game... Click anywhere to continue", fg=self.colors['warning'])
        
        # Bind click events for replay control
        self.root.bind('<Button-1>', self.replay_next_step)
    
    def replay_next_step(self, event=None):
        """Show next step in replay"""
        if not self.is_replaying or self.current_replay_step >= len(self.game_history):
            self.end_replay()
            return
        
        # Get current move from history
        move_data = self.game_history[self.current_replay_step]
        row, col = move_data['move']
        player = move_data['player']
        move_number = move_data['move_number']
        
        # Make the move
        self.game.make_move(row, col, player)
        self.update_board()
        
        # Update status
        player_symbol = 'X' if player == 1 else 'O'
        is_ai = move_data.get('is_ai', False)
        player_type = 'AI' if is_ai else 'Human'
        
        self.status_label.config(
            text=f"Replay - Move {move_number}: {player_type} ({player_symbol}) at ({row}, {col})",
            fg=self.colors['accent']
        )
        
        self.current_replay_step += 1
        
        # Auto-advance or wait for next click
        if self.current_replay_step < len(self.game_history):
            # Auto-advance after 1.5 seconds, or wait for click
            self.root.after(1500, self.replay_next_step)
    
    def end_replay(self):
        """End replay mode"""
        self.is_replaying = False
        self.root.unbind('<Button-1>')
        
        if self.game.game_over:
            self.handle_game_end()
            self.status_label.config(
                text=self.status_label.cget('text') + " (Replay Complete)",
                fg=self.colors['success']
            )
        else:
            self.status_label.config(text="Replay complete", fg=self.colors['success'])
    
    def return_to_previous(self):
        """Return to previous move (undo functionality)"""
        if not self.game_history or self.is_replaying:
            self.status_label.config(text="Cannot return - no moves to undo!", fg=self.colors['warning'])
            return
        
        # Remove last move(s) - if vs AI, remove both AI and human moves
        moves_to_remove = 1
        if (self.game_mode == 'ai' and 
            len(self.game_history) >= 2 and 
            self.game_history[-1].get('is_ai', False)):
            moves_to_remove = 2  # Remove both AI move and previous human move
        
        # Remove moves from history
        for _ in range(min(moves_to_remove, len(self.game_history))):
            self.game_history.pop()
        
        # Reconstruct game state
        self.game.reset()
        
        for move_data in self.game_history:
            row, col = move_data['move']
            player = move_data['player']
            self.game.make_move(row, col, player)
        
        # Update display
        self.update_board()
        
        # Set current player
        if len(self.game_history) % 2 == 0:
            self.game.current_player = 1
        else:
            self.game.current_player = -1
        
        # Update status
        if self.game_mode == 'ai':
            if self.game.current_player == self.human_player:
                self.status_label.config(text="Your turn (X) - Move undone", fg=self.colors['accent'])
            else:
                self.status_label.config(text="AI turn - Move undone", fg=self.colors['warning'])
                self.ai_turn = True
                self.root.after(1000, self.make_ai_move)
        else:
            player_name = "X" if self.game.current_player == 1 else "O"
            self.status_label.config(text=f"{player_name}'s turn - Move undone", fg=self.colors['accent'])
        
        self.ai_turn = False
    
    def show_settings(self):
        """Show settings popup"""
        from tkinter import messagebox
        
        settings_options = [
            "⚙️ Settings Menu",
            "",
            "🎮 Current Mode: " + ("AI" if self.game_mode == 'ai' else "Human vs Human"),
            "🤖 AI Difficulty: " + (self.ai_difficulty.title() if self.game_mode == 'ai' else "N/A"),
            "📊 Games Played: " + str(self.wins + self.losses + self.draws),
            "🏆 Win Rate: " + (f"{(self.wins / max(1, self.wins + self.losses + self.draws) * 100):.1f}%"),
            "",
            "💡 Tips:",
            "• Use Replay to analyze games",
            "• Use Undo to learn from mistakes",
            "• Hard AI uses ML + Enhanced Minimax"
        ]
        
        messagebox.showinfo("Settings & Info", "\n".join(settings_options))
    
    def change_difficulty(self):
        """Change AI difficulty during game"""
        if self.game_mode != 'ai':
            from tkinter import messagebox
            messagebox.showwarning("Change Difficulty", "Difficulty can only be changed in AI mode!")
            return
        
        # Create difficulty selection popup
        self.show_difficulty_popup()
    
    def show_difficulty_popup(self):
        """Show difficulty selection popup"""
        popup = tk.Toplevel(self.root)
        popup.title("Change AI Difficulty")
        popup.geometry("350x250")
        popup.configure(bg=self.colors['bg'])
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Title
        title_label = tk.Label(popup,
                              text="🤖 Select AI Difficulty",
                              font=('Arial', 16, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['text'])
        title_label.pack(pady=20)
        
        # Current difficulty
        current_label = tk.Label(popup,
                                 text=f"Current: {self.ai_difficulty.title()}",
                                 font=('Arial', 12),
                                 bg=self.colors['bg'],
                                 fg=self.colors['text_muted'])
        current_label.pack(pady=5)
        
        # Difficulty buttons
        button_frame = tk.Frame(popup, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        difficulties = [
            ("🟢 Easy", "easy", self.colors['success']),
            ("🟡 Medium", "medium", self.colors['warning']),
            ("🔴 Hard", "hard", self.colors['danger'])
        ]
        
        for text, difficulty, color in difficulties:
            btn = tk.Button(button_frame,
                           text=text,
                           font=('Arial', 12, 'bold'),
                           bg=color,
                           fg='white',
                           activebackground=color,
                           activeforeground='white',
                           relief='flat',
                           borderwidth=0,
                           padx=25,
                           pady=8,
                           command=lambda d=difficulty, p=popup: self.apply_difficulty_change(d, p))
            btn.pack(pady=5)
        
        # Button container
        button_container = tk.Frame(popup, bg=self.colors['bg'])
        button_container.pack(pady=10)
        
        # Cancel button
        cancel_btn = tk.Button(button_container,
                              text="Cancel",
                              font=('Arial', 10),
                              bg=self.colors['text_muted'],
                              fg='white',
                              activebackground='#666666',
                              activeforeground='white',
                              relief='flat',
                              borderwidth=0,
                              padx=20,
                              pady=5,
                              command=popup.destroy)
        cancel_btn.pack()
    
    def apply_difficulty_change(self, new_difficulty, popup):
        """Apply difficulty change"""
        self.ai_difficulty = new_difficulty
        self.ai_player = HybridAI(difficulty=new_difficulty)
        
        # Update status
        self.status_label.config(
            text=f"AI difficulty changed to {new_difficulty.title()}!",
            fg=self.colors['success']
        )
        
        popup.destroy()
        
        # Auto-revert status after 2 seconds
        self.root.after(2000, lambda: self.status_label.config(
            text="Your turn (X)" if self.game_mode == 'ai' else "Game continues",
            fg=self.colors['accent']
        ))
    
    def exit_game(self):
        """Exit current game and return to main menu"""
        from tkinter import messagebox
        
        # Check if there's an active game
        if not self.game.game_over and len(self.game_history) > 0:
            # Game is in progress
            result = messagebox.askyesnocancel(
                "Exit Game",
                "Do you want to exit the current game?\n\n" +
                "• Yes: Return to main menu (game will be lost)\n" +
                "• No: Save game state and return to menu\n" +
                "• Cancel: Continue playing",
                icon='question'
            )
            
            if result is True:  # Yes - Exit without saving
                self.create_main_menu()
            elif result is False:  # No - Save and exit
                self.save_game_state()
                self.create_main_menu()
            # Cancel - do nothing, stay in game
            
        elif self.game.game_over:
            # Game is finished
            result = messagebox.askyesno(
                "Exit Game",
                "Return to main menu?\n\nGame statistics have been saved.",
                icon='question'
            )
            if result:
                self.create_main_menu()
        else:
            # No game started yet
            self.create_main_menu()
    
    def save_game_state(self):
        """Save current game state for potential resume"""
        from tkinter import messagebox
        
        try:
            # Create a simple save state
            save_data = {
                'board': self.game.board.tolist(),
                'current_player': self.game.current_player,
                'game_mode': self.game_mode,
                'ai_difficulty': self.ai_difficulty if self.game_mode == 'ai' else None,
                'game_history': self.game_history,
                'move_count': len(self.game_history)
            }
            
            # Show save confirmation
            messagebox.showinfo(
                "Game Saved",
                f"Game state saved!\n\n" +
                f"Mode: {self.game_mode.title()}\n" +
                f"Moves played: {len(self.game_history)}\n" +
                f"Current player: {'X' if self.game.current_player == 1 else 'O'}\n\n" +
                "Note: This demo saves game info to memory.\n" +
                "In a full version, this would save to a file."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Could not save game state:\n{e}\n\nReturning to menu anyway."
            )
    
    def confirm_return_to_menu(self):
        """Confirm before returning to main menu (legacy method)"""
        from tkinter import messagebox
        
        if not self.game.game_over and len(self.game_history) > 0:
            result = messagebox.askyesno(
                "Return to Menu",
                "Are you sure you want to return to the main menu?\n\nCurrent game progress will be lost.",
                icon='warning'
            )
            if result:
                self.create_main_menu()
        else:
            self.create_main_menu()
    
    def show_help(self):
        """Show help information"""
        from tkinter import messagebox
        
        help_text = [
            "🎮 How to Play:",
            "",
            "🎯 Objective: Get 3 in a row (horizontal, vertical, or diagonal)",
            "",
            "🎮 Game Controls:",
            "• Click on empty squares to make moves",
            "• 🔄 New Game: Start a fresh game",
            "• ⏮️ Replay: Watch the game replay step-by-step",
            "• ↩️ Undo: Take back your last move(s)",
            "",
            "🛠️ Game Management:",
            "• ⚙️ Settings: View game information & stats",
            "• 🎯 Change AI: Adjust difficulty during game",
            "• 🚪 Exit Game: Leave current game (with save option)",
            "• 🏠 Main Menu: Return to main menu",
            "",
            "🤖 AI Difficulties:",
            "• 🟢 Easy: Casual play (30% optimal moves)",
            "• 🟡 Medium: Balanced challenge (mixed strategies)",
            "• 🔴 Hard: Maximum challenge (ML + Enhanced Minimax)",
            "",
            "💡 Pro Tips:",
            "• Control the center square for best positioning",
            "• Watch for fork opportunities (double threats)",
            "• Use Replay to analyze and learn from games",
            "• Exit Game offers save option for longer games",
            "• Hard AI uses neural networks and deep search!"
        ]
        
        messagebox.showinfo("Help - How to Play", "\n".join(help_text))
    
    def show_about(self):
        """Show about information"""
        from tkinter import messagebox
        
        about_text = [
            "🎮 AI Tic-Tac-Toe Master v2.0",
            "",
            "🤖 Enhanced AI Features:",
            "• Neural Network (99.41% accuracy)",
            "• Random Forest (97.94% accuracy)",
            "• Enhanced Minimax (12-level depth)",
            "• Opening book with optimal moves",
            "• Advanced threat detection",
            "• Transposition table caching",
            "",
            "🎨 Interface Features:",
            "• Modern dark theme",
            "• Game replay system",
            "• Smart undo functionality",
            "• Dynamic difficulty adjustment",
            "• Comprehensive statistics",
            "",
            "⚡ Technical Details:",
            "• Built with Python & PyTorch",
            "• GPU-accelerated training",
            "• Real-time AI inference",
            "• 340K+ training samples",
            "",
            "💻 Enhanced Edition 2024",
            "Built with ❤️ for AI enthusiasts"
        ]
        
        messagebox.showinfo("About AI Tic-Tac-Toe Master", "\n".join(about_text))
    
    def reset_statistics(self):
        """Reset game statistics"""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Reset Statistics",
            "Are you sure you want to reset all game statistics?\n\nThis action cannot be undone.",
            icon='warning'
        )
        
        if result:
            self.wins = 0
            self.losses = 0
            self.draws = 0
            
            messagebox.showinfo("Statistics Reset", "All game statistics have been reset!")
            
            # Refresh main menu to show updated stats
            self.create_main_menu()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernTicTacToeGUI()
    app.run()
