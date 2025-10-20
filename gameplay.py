import random
import copy

class Worker:
    def __init__(self, owner, worker_id, x=None, y=None):
        self.owner = owner  # 0 (human/red) or 1 (AI/blue)
        self.worker_id = worker_id  # 0 or 1 for each player
        self.x = x
        self.y = y

class AIPlayer:
    def __init__(self, player_id, depth=3):
        self.player_id = player_id
        self.depth = depth
    
    def evaluate(self, game):
        """Heuristic evaluation function"""
        my_workers = [w for w in game.workers if w.owner == self.player_id]
        opp_workers = [w for w in game.workers if w.owner != self.player_id]
        
        score = 0
        
        # Evaluate my workers
        for w in my_workers:
            if w.x is None:
                continue
            height = game.board[w.y][w.x]
            if height == 3:
                score += 1000  # Winning position
            elif height == 2:
                score += 30    # Very good position
            elif height == 1:
                score += 10    # Good position
            
            # Mobility bonus
            moves = len(game.possible_moves(w))
            score += moves * 2
        
        # Evaluate opponent workers
        for w in opp_workers:
            if w.x is None:
                continue
            height = game.board[w.y][w.x]
            if height == 3:
                score -= 1000  # Opponent winning
            elif height == 2:
                score -= 30    # Opponent in good position
            elif height == 1:
                score -= 10    # Opponent advancing
            
            # Opponent mobility penalty
            moves = len(game.possible_moves(w))
            score -= moves * 2
        
        return score + random.randint(-3, 3)  # Add randomness
    
    def minimax(self, game, depth, maximizing):
        """Minimax algorithm with alpha-beta pruning concept"""
        # Check for immediate win/loss
        for w in game.workers:
            if game.has_won(w):
                if w.owner == self.player_id:
                    return 10000, None  # AI wins
                else:
                    return -10000, None  # Human wins
        
        # Check for losing position (no moves available)
        if game.is_losing_position(game.turn):
            if game.turn == self.player_id:
                return -10000, None
            else:
                return 10000, None
        
        # Base case: depth limit reached
        if depth == 0:
            return self.evaluate(game), None
        
        # Get all possible actions
        actions = game.all_actions(game.turn)
        if not actions:
            return self.evaluate(game), None
        
        if maximizing:
            max_eval = float('-inf')
            best_action = None
            
            for action in actions:
                # Create game copy and simulate action
                game_clone = game.clone()
                game_clone.do_action(*action)
                game_clone.turn = 1 - game_clone.turn
                
                eval_score, _ = self.minimax(game_clone, depth - 1, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_action = action
            
            return max_eval, best_action
        else:
            min_eval = float('inf')
            best_action = None
            
            for action in actions:
                # Create game copy and simulate action
                game_clone = game.clone()
                game_clone.do_action(*action)
                game_clone.turn = 1 - game_clone.turn
                
                eval_score, _ = self.minimax(game_clone, depth - 1, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_action = action
            
            return min_eval, best_action
    
    def choose_action(self, game):
        """Choose best action using minimax"""
        _, action = self.minimax(game, self.depth, True)
        return action

class Santorini:
    def __init__(self):
        # Game board (5x5 grid, heights 0-4)
        self.board = [[0 for _ in range(5)] for _ in range(5)]
        
        # Worker tracking
        self.workers = []
        self.occupants = [[None for _ in range(5)] for _ in range(5)]
        
        # Create workers (2 per player)
        for player in [0, 1]:
            for worker_id in [0, 1]:
                self.workers.append(Worker(player, worker_id))
        
        # Game state
        self.turn = 0  # 0 = human (red), 1 = AI (blue)
        self.phase = 'placement'  # 'placement' or 'play'
        self.is_ai_turn = False
        self.game_over = False
        self.winner = None
        self.placed_workers = 0
        
        # AI player
        self.ai = AIPlayer(player_id=1, depth=3)
    
    def place_worker_at(self, worker_index, col, row):
        """Place a worker at the specified position during placement phase"""
        if self.phase != 'placement':
            return False
        
        # Check bounds and if cell is occupied
        if not (0 <= col < 5 and 0 <= row < 5):
            return False
        if self.occupants[row][col] is not None:
            return False
        
        # Get the worker to place
        if worker_index < len(self.workers):
            worker = self.workers[worker_index]
            worker.x = col
            worker.y = row
            
            # Update occupants grid
            self.occupants[row][col] = worker
            self.placed_workers += 1
            
            # Check if placement phase is complete
            if self.placed_workers == 4:
                self.phase = 'play'
                self.is_ai_turn = (self.turn == 1)
            
            return True
        
        return False
    
    def get_worker_at(self, col, row):
        """Get the worker at the specified position"""
        if 0 <= col < 5 and 0 <= row < 5:
            return self.occupants[row][col]
        return None
    
    def possible_moves(self, worker):
        """Get all valid move positions for a worker"""
        if worker.x is None or worker.y is None:
            return []
        
        moves = []
        current_height = self.board[worker.y][worker.x]
        
        # Check all 8 adjacent cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x = worker.x + dx
                new_y = worker.y + dy
                
                # Check bounds
                if not (0 <= new_x < 5 and 0 <= new_y < 5):
                    continue
                
                # Check if occupied
                if self.occupants[new_y][new_x] is not None:
                    continue
                
                # Check height constraint (can't move up more than 1 level)
                new_height = self.board[new_y][new_x]
                if new_height > current_height + 1:
                    continue
                
                # Check if there's a dome (height 4)
                if new_height >= 4:
                    continue
                
                moves.append((new_x, new_y))
        
        return moves
    
    def possible_builds(self, worker):
        """Get all valid build positions for a worker"""
        if worker.x is None or worker.y is None:
            return []
        
        builds = []
        
        # Check all 8 adjacent cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x = worker.x + dx
                new_y = worker.y + dy
                
                # Check bounds
                if not (0 <= new_x < 5 and 0 <= new_y < 5):
                    continue
                
                # Check if occupied
                if self.occupants[new_y][new_x] is not None:
                    continue
                
                # Check if already at max height (4 = dome)
                if self.board[new_y][new_x] >= 4:
                    continue
                
                builds.append((new_x, new_y))
        
        return builds
    
    def has_won(self, worker):
        """Check if a worker has won by reaching height 3"""
        if worker.x is None or worker.y is None:
            return False
        return self.board[worker.y][worker.x] == 3
    
    def get_player_workers(self, player):
        """Get all workers belonging to a player"""
        return [w for w in self.workers if w.owner == player]
    
    def is_losing_position(self, player):
        """Check if player has no valid moves (losing position)"""
        my_workers = self.get_player_workers(player)
        return not any(self.possible_moves(w) for w in my_workers if w.x is not None)
    
    def clone(self):
        """Create a deep copy of the current game state"""
        new_game = Santorini()
        new_game.board = copy.deepcopy(self.board)
        new_game.occupants = [[None for _ in range(5)] for _ in range(5)]
        new_game.workers = []
        
        # Copy workers and update occupants
        for worker in self.workers:
            new_worker = Worker(worker.owner, worker.worker_id, worker.x, worker.y)
            new_game.workers.append(new_worker)
            if worker.x is not None and worker.y is not None:
                new_game.occupants[worker.y][worker.x] = new_worker
        
        new_game.turn = self.turn
        new_game.phase = self.phase
        new_game.is_ai_turn = self.is_ai_turn
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.placed_workers = self.placed_workers
        
        return new_game
    
    def all_actions(self, player):
        """Generate all possible actions for a player"""
        actions = []
        my_workers = self.get_player_workers(player)
        
        for worker in my_workers:
            if worker.x is None:
                continue
            
            for move in self.possible_moves(worker):
                # Temporarily move worker to new position
                old_x, old_y = worker.x, worker.y
                worker.x, worker.y = move
                
                # Get possible builds from new position
                for build in self.possible_builds(worker):
                    actions.append((worker.worker_id, move, build))
                
                # Restore original position
                worker.x, worker.y = old_x, old_y
        
        return actions
    
    def do_action(self, worker_id, move, build):
        """Execute an action: move worker, then build"""
        my_workers = self.get_player_workers(self.turn)
        worker = next(w for w in my_workers if w.worker_id == worker_id)
        
        # Move worker
        self.occupants[worker.y][worker.x] = None
        worker.x, worker.y = move
        self.occupants[worker.y][worker.x] = worker
        
        # Check for win after move
        if self.has_won(worker):
            self.game_over = True
            self.winner = worker.owner
            return
        
        # Build
        build_x, build_y = build
        self.board[build_y][build_x] += 1
    
    def ai_get_best_move(self):
        """AI decision making using minimax"""
        if self.phase == 'placement':
            return self.ai_placement_move()
        else:
            return self.ai_play_move()
    
    def ai_placement_move(self):
        """AI placement strategy"""
        available_cells = []
        for row in range(5):
            for col in range(5):
                if self.occupants[row][col] is None:
                    available_cells.append((col, row))
        
        if not available_cells:
            return None
        
        # Priority: center > corners > edges
        center_cells = [(2, 2), (1, 2), (3, 2), (2, 1), (2, 3)]
        corner_cells = [(0, 0), (0, 4), (4, 0), (4, 4)]
        
        for priority_cells in [center_cells, corner_cells]:
            for cell in priority_cells:
                if cell in available_cells:
                    return cell
        
        return random.choice(available_cells)
    
    def ai_play_move(self):
        """AI play phase using minimax"""
        action = self.ai.choose_action(self)
        if not action:
            return None
        
        worker_id, move, build = action
        
        # Find the actual worker object
        my_workers = self.get_player_workers(1)  # AI is player 1
        worker = next(w for w in my_workers if w.worker_id == worker_id)
        
        return (worker, move, build)
    
    def execute_move(self, worker, move_pos, build_pos=None):
        """Execute a move (used by both human and AI)"""
        # Clear old position
        if worker.x is not None:
            self.occupants[worker.y][worker.x] = None
        
        # Make move
        worker.x, worker.y = move_pos
        self.occupants[move_pos[1]][move_pos[0]] = worker
        
        # Check for win after move
        if self.has_won(worker):
            self.game_over = True
            self.winner = worker.owner
            return True
        
        # If build position provided, execute build
        if build_pos is not None:
            self.board[build_pos[1]][build_pos[0]] += 1
            
            # Switch turns only if game hasn't ended
            if not self.game_over:
                self.turn = 1 - self.turn
                self.is_ai_turn = (self.turn == 1)
        
        return False  # Game continues
