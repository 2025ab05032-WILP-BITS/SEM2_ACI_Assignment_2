import sys

"""
Two-Player Sudoku Solver using Minimax Algorithm
========================================================
This program reads a partially filled Sudoku puzzle and determines the optimal move
for the current player using the Minimax algorithm. Player 1 (MAX) tries to maximize
the net score (P1_score - P2_score), while Player 2 (MIN) tries to minimize it.
Both players play optimally.

Algorithm Overview:
- Uses game theory's Minimax approach to evaluate all possible moves
- P1 (Maximizing player) wants the highest net score
- P2 (Minimizing player) wants the lowest net score
- Memoization stores already evaluated board states to avoid redundant calculations
- Scoring: Each player earns points equal to the value they place (1-9)

Error Handling:
- Explicit 'FULL' message when board capacity is at maximum (all cells filled)
- Explicit 'EMPTY' message when no valid moves exist for current player
- File I/O validation with clear error messages
- Input validation for board structure and data integrity
"""  

def read_input(filename):
    """
    Reads and parses the input file containing player info and Sudoku board.
    
    Input file format:
    - First line: Current player (P1 or P2)
    - Next 9 lines: Sudoku board with space-separated values
      - '.' represents empty cells
      - '1'-'9' represent filled cells
    
    Returns:
        tuple: (player_name, board_2d_list)
    
    Exits if any validation fails.
    """
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # print(f"[ERROR] Input file '{filename}' not found.")
        # print(f"[ACTION] Please ensure input file exists at: {filename}")
        sys.exit(1)
    except IOError as e:
        # print(f"[ERROR] Unable to read input file '{filename}': {e}")
        sys.exit(1)

    if not lines:
        # print("[ERROR] Input file is EMPTY - no data to process.")
        # print("[ACTION] Input file must contain: player line (P1/P2) + 9 board rows")
        sys.exit(1)

    # Parse the player from the first line
    player = lines[0]
    if player not in ('P1', 'P2'):
        # print(f"[ERROR] Invalid player '{player}' in input file.")
        # print(f"[ACTION] Player must be either 'P1' or 'P2'.")
        sys.exit(1)

    # Validate that we have exactly 10 lines (1 player + 9 board rows)
    if len(lines) < 10:
        # print(f"[ERROR] Incomplete board data - expected 10 lines (1 player + 9 rows), got {len(lines)}.")
        # print(f"[ACTION] Please provide complete 9x9 Sudoku board.")
        sys.exit(1)

    # Parse the 9x9 Sudoku board
    board = []
    for i in range(1, 10):
        tokens = lines[i].split()
        if len(tokens) != 9:
            # print(f"[ERROR] Row {i} has invalid dimensions - expected 9 values, got {len(tokens)}.")
            # print(f"[ACTION] Each row must contain exactly 9 space-separated values.")
            sys.exit(1)
        row = []
        for j, t in enumerate(tokens):
            if t == '.':
                row.append(0)  # 0 represents empty cell
            elif t.isdigit() and 1 <= int(t) <= 9:
                row.append(int(t))
            else:
                # print(f"[ERROR] Invalid cell value '{t}' at row {i}, column {j+1}.")
                # print(f"[ACTION] Cell values must be '.' (empty) or '1'-'9' (filled).")
                sys.exit(1)
        board.append(row)

    return player, board


def get_valid_values(board, r, c):
    """
    Returns all valid Sudoku numbers (1-9) that can be placed at position (r, c).
    
    A number is valid if it doesn't already exist in:
    - The same row
    - The same column
    - The same 3x3 subgrid
    
    Args:
        board: 2D list representing the Sudoku board
        r: Row index (0-8)
        c: Column index (0-8)
    
    Returns:
        list: Sorted list of valid numbers (1-9 subset)
    
    Raises:
        ValueError: If cell position is invalid or already filled
    """
    # Validate cell position
    if not (0 <= r < 9 and 0 <= c < 9):
        # print(f"[ERROR] Invalid cell position ({r}, {c}) - must be within 0-8 range.")
        sys.exit(1)
    
    if board[r][c] != 0:
        # print(f"[ERROR] Cell at position ({r}, {c}) is already filled with value {board[r][c]}.")
        sys.exit(1)
    
    used = set()
    
    # Check all numbers in the same row
    for v in board[r]:
        if v:  # 0 represents empty cell
            used.add(v)
    
    # Check all numbers in the same column
    for i in range(9):
        if board[i][c]:
            used.add(board[i][c])
    
    # Check all numbers in the same 3x3 subgrid
    # Calculate the top-left corner of the subgrid containing (r, c)
    br, bc = (r // 3) * 3, (c // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j]:
                used.add(board[i][j])
    
    # Return sorted list of valid numbers (ensures consistent ordering for tie-breaking)
    return sorted(v for v in range(1, 10) if v not in used)


def is_board_full(board):
    """
    Checks if the Sudoku board is completely filled (FULL capacity reached).
    
    Args:
        board: 2D list representing the Sudoku board
    
    Returns:
        bool: True if all cells are filled, False if any empty cells exist
    """
    return not any(board[r][c] == 0 for r in range(9) for c in range(9))


def count_empty_cells(board):
    """
    Counts the number of empty cells in the Sudoku board.
    
    Args:
        board: 2D list representing the Sudoku board
    
    Returns:
        int: Number of empty cells (0-81)
    """
    return sum(1 for r in range(9) for c in range(9) if board[r][c] == 0)


def board_to_tuple(board):
    """
    Converts the 2D board list to an immutable tuple representation.
    
    This is necessary for using the board as a dictionary key in memoization.
    Lists are mutable and cannot be used as dictionary keys.
    
    Args:
        board: 2D list representation of the Sudoku board
    
    Returns:
        tuple: Immutable tuple of tuples
    
    Raises:
        ValueError: If board is not a valid 9x9 structure
    """
    if len(board) != 9 or any(len(row) != 9 for row in board):
        # print(f"[ERROR] Invalid board structure - board must be 9x9, got {len(board)}x{len(board[0]) if board else 0}.")
        sys.exit(1)
    
    return tuple(tuple(row) for row in board)


def minimax(board_tuple, player, memo):
    """
    Minimax algorithm that evaluates the optimal game outcome from the current position.
    
    The algorithm recursively explores all possible moves and returns the best
    future net score (P1_gains - P2_gains) assuming both players play optimally:
    - P1 (MAX player) wants to maximize the net score
    - P2 (MIN player) wants to minimize the net score
    
    Args:
        board_tuple: Immutable tuple representation of board state
        player: Current player ('P1' or 'P2')
        memo: Dictionary for memoization to avoid re-evaluating same board states
    
    Returns:
        int: The optimal net score (P1_score - P2_score) from this position forward
    """
    # Check if this state has already been evaluated (memoization)
    key = (board_tuple, player)
    if key in memo:
        return memo[key]

    # Convert immutable tuple back to mutable list for board manipulation
    board = [list(row) for row in board_tuple]
    next_player = 'P2' if player == 'P1' else 'P1'
    is_max = player == 'P1'  # True if P1's turn (maximizing), False if P2's turn (minimizing)
    best = None

    # Try all possible moves (iterate through all cells)
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:  # Found an empty cell
                # Try each valid number at this position
                for v in get_valid_values(board, r, c):
                    board[r][c] = v  # Place the number
                    
                    # Recursively evaluate the future game state
                    future = minimax(board_to_tuple(board), next_player, memo)
                    
                    board[r][c] = 0  # Undo the move for backtracking
                    
                    # Calculate the net score change if current player places value v
                    # P1 gains +v points, which increases net score
                    # P2 gains +v points, which decreases net score (so we subtract)
                    delta = v + future if is_max else -v + future
                    
                    # Update best move based on whether we're maximizing or minimizing
                    if best is None or (is_max and delta > best) or (not is_max and delta < best):
                        best = delta

    # Memoize the result: if no moves exist, return 0 (terminal state)
    memo[key] = 0 if best is None else best
    return memo[key]


def find_best_move(board, player):
    """
    Finds the optimal move for the current player using Minimax algorithm.
    
    Evaluates all possible moves and selects the one with the best outcome.
    In case of ties, the move with the smallest row is chosen, then smallest column.
    
    Args:
        board: 2D list representing the Sudoku board
        player: Current player ('P1' or 'P2')
    
    Returns:
        tuple: (best_row, best_column, best_value, p1_score, p2_score)
               where scores are points earned in this move only (not cumulative)
    
    Capacity Messages:
    - [FULL] Board is at maximum capacity (all 81 cells filled)
    - [EMPTY] No valid moves available for current player
    
    Exits if the board is FULL or has EMPTY move set.
    """
    # Validate player
    if player not in ('P1', 'P2'):
        # print(f"[ERROR] Invalid player '{player}' - must be 'P1' or 'P2'.")
        sys.exit(1)
    
    empty_count = count_empty_cells(board)
    
    # Check if board is already FULL
    if empty_count == 0:
        # print("[FULL] Board capacity FULL - all 81 cells are filled.")
        # print("[ACTION] No moves available. Game is complete.")
        sys.exit(1)

    memo = {}  # Dictionary to store evaluated board states
    next_player = 'P2' if player == 'P1' else 'P1'
    is_max = player == 'P1'
    best_delta = None
    best_r = best_c = best_v = None
    found_any = False

    # Try all possible moves in row-major order
    # This ensures tie-breaking works correctly (smallest row first, then smallest column)
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:  # Found an empty cell
                for v in get_valid_values(board, r, c):
                    found_any = True
                    board[r][c] = v  # Place the number
                    
                    # Evaluate this move using Minimax
                    future = minimax(board_to_tuple(board), next_player, memo)
                    
                    board[r][c] = 0  # Undo the move
                    
                    # Calculate the net score delta for this move
                    delta = v + future if is_max else -v + future
                    
                    # Keep track of the best move so far
                    # For P1 (MAX): choose move with highest delta
                    # For P2 (MIN): choose move with lowest delta
                    if best_delta is None or (is_max and delta > best_delta) or (not is_max and delta < best_delta):
                        best_delta = delta
                        best_r, best_c, best_v = r, c, v

    if not found_any:
        # print(f"[EMPTY] No valid moves available for {player}.")
        # print(f"[ACTION] {empty_count} empty cells exist, but no valid Sudoku values can be placed.")
        # print(f"[ACTION] This may indicate an invalid or unsolvable board state.")
        sys.exit(1)

    # Apply the best move to the board
    board[best_r][best_c] = best_v
    
    # Calculate the score for this move only (not cumulative)
    # P1 earns points if P1 placed the value, otherwise P1 earns 0
    # P2 earns points if P2 placed the value, otherwise P2 earns 0
    p1_score = best_v if player == 'P1' else 0
    p2_score = best_v if player == 'P2' else 0
    
    return best_r, best_c, best_v, p1_score, p2_score


def board_to_string(board):
    """
    Converts the 2D board array to a formatted string representation.
    
    Args:
        board: 2D list representing the Sudoku board
    
    Returns:
        str: Formatted board with spaces between numbers and newlines between rows
             Empty cells represented as '.'
    """
    return '\n'.join(
        ' '.join('.' if v == 0 else str(v) for v in row)
        for row in board
    )


def write_output(filename, r, c, v, p1_score, p2_score, board):
    """
    Writes the solution to the output file and prints it to console.
    
    Output format:
    - Best Move: Row, Column, Number (1-indexed)
    - Scores: Player 1 and Player 2 (current move points)
    - Updated Sudoku Board
    
    Args:
        filename: Output file name (e.g., 'outputPS1.txt')
        r: Best row index (0-8)
        c: Best column index (0-8)
        v: Best value to place (1-9)
        p1_score: Points earned by Player 1 in this move
        p2_score: Points earned by Player 2 in this move
        board: Updated board after applying the move
    
    Error Handling:
    - IOError/PermissionError: File write failures
    - ValueError: Invalid output parameters
    """
    # Validate output parameters
    if not (0 <= r < 9 and 0 <= c < 9):
        # print(f"[ERROR] Invalid move position ({r}, {c}) - must be within 0-8 range.")
        sys.exit(1)
    
    if not (1 <= v <= 9):
        # print(f"[ERROR] Invalid move value {v} - must be between 1-9.")
        sys.exit(1)
    
    if p1_score < 0 or p2_score < 0:
        # print(f"[ERROR] Invalid scores - P1: {p1_score}, P2: {p2_score}. Scores cannot be negative.")
        sys.exit(1)
    
    content = (
        f"Best Move:\n"
        f"Row = {r + 1}\n"  # Convert to 1-indexed for output
        f"Column = {c + 1}\n"  # Convert to 1-indexed for output
        f"Number = {v}\n"
        f"Player 1 Score = {p1_score}\n"
        f"Player 2 Score = {p2_score}\n"
        f"\n"
        f"Updated Sudoku Board\n"
        f"{board_to_string(board)}"
    )
    
    # Write to output file with error handling
    try:
        with open(filename, 'w') as f:
            f.write(content)
        # print(f"[SUCCESS] Output written to '{filename}'")
    except FileNotFoundError:
        # print(f"[ERROR] Output file path '{filename}' is invalid or directory does not exist.")
        # print(f"[ACTION] Ensure the directory exists before writing.")
        sys.exit(1)
    except PermissionError:
        # print(f"[ERROR] Permission denied - cannot write to '{filename}'.")
        # print(f"[ACTION] Check file permissions and try again.")
        sys.exit(1)
    except IOError as e:
        # print(f"[ERROR] Failed to write output file '{filename}': {e}")
        sys.exit(1)
    
    # Also print to console for immediate feedback
    # print("\n" + content)


def main():
    """
    Main entry point of the program.
    
    Usage:
        python solutionPS1.py <input_file> <output_file>
    
    Args:
        input_file: Path to input file containing player and board state
        output_file: Path to output file for writing the solution
    
    Workflow:
    1. Read input file with player and board state
    2. Find the optimal move using Minimax algorithm
    3. Write the solution to output file and console
    """
    try:
        # Parse command line arguments
        if len(sys.argv) < 3:
            print("[ERROR] Insufficient arguments provided.")
            print("[USAGE] python solutionPS1.py <input_file> <output_file>")
            print("[EXAMPLE] python solutionPS1.py inputPS1.txt outputPS1.txt")
            sys.exit(1)
        
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        # Step 1: Read input
        player, board = read_input(input_file)
        # print(f"[SUCCESS] Input loaded - Player: {player}, Empty cells: {count_empty_cells(board)}")
        
        # Step 2: Find best move
        r, c, v, p1_score, p2_score = find_best_move(board, player)
        # print(f"[SUCCESS] Optimal move calculated for {player}")
        
        # Step 3: Write output
        write_output(output_file, r, c, v, p1_score, p2_score, board)
        # print(f"[SUCCESS] Sudoku Solver completed successfully.")
        
    except KeyboardInterrupt:
        # print("\n[ERROR] Program interrupted by user.")
        sys.exit(1)
    except Exception as e:
        # print(f"[ERROR] Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
