"""
Automated Testing Framework for PS1 - Two-Player Sudoku Completion using Minimax

This module implements an independent Minimax solver and comprehensive test framework
to validate student solutions against ground truth answers.

No external dependencies beyond Python stdlib.
"""

import subprocess
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional
from copy import deepcopy
import random
import itertools


# ============================================================================
# SUDOKU BOARD UTILITIES
# ============================================================================

class SudokuValidator:
    """Validates Sudoku boards and moves."""

    @staticmethod
    def is_valid_placement(board: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if placing num at (row, col) is valid.
        
        Args:
            board: 9x9 Sudoku board (0-indexed)
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)
            
        Returns:
            True if placement is valid, False otherwise
        """
        # Check if cell is empty
        if board[row][col] != 0:
            return False

        # Check row
        if num in board[row]:
            return False

        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False

        return True

    @staticmethod
    def get_valid_moves(board: List[List[int]]) -> List[Tuple[int, int, int]]:
        """
        Get all valid moves for current board state.
        
        Returns:
            List of (row, col, num) tuples, sorted by (row, col, num)
        """
        moves = []
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:  # Empty cell
                    for num in range(1, 10):
                        if SudokuValidator.is_valid_placement(board, row, col, num):
                            moves.append((row, col, num))
        
        # Sort by row, then col, then num for consistency
        moves.sort()
        return moves

    @staticmethod
    def is_board_complete(board: List[List[int]]) -> bool:
        """Check if board is completely filled."""
        for row in board:
            if 0 in row:
                return False
        return True


# ============================================================================
# TEST CASE GENERATION
# ============================================================================

class SudokuBoardGenerator:
    """Generates valid Sudoku boards for testing."""

    @staticmethod
    def generate_completed_board() -> List[List[int]]:
        """Generate a valid completed 9x9 Sudoku board."""
        board = [[0] * 9 for _ in range(9)]

        def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
            """Check if placing num at (row, col) is valid."""
            # Check row
            if num in board[row]:
                return False

            # Check column
            if num in [board[i][col] for i in range(9)]:
                return False

            # Check 3x3 box
            box_row, box_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(box_row, box_row + 3):
                for j in range(box_col, box_col + 3):
                    if board[i][j] == num:
                        return False
            return True

        def solve(board: List[List[int]]) -> bool:
            """Solve Sudoku using backtracking."""
            for row in range(9):
                for col in range(9):
                    if board[row][col] == 0:
                        for num in range(1, 10):
                            if is_safe(board, row, col, num):
                                board[row][col] = num
                                if solve(board):
                                    return True
                                board[row][col] = 0
                        return False
            return True

        # Fill first row with shuffled numbers
        first_row = list(range(1, 10))
        random.shuffle(first_row)
        board[0] = first_row

        # Solve to get a complete board
        solve(board)
        return board

    @staticmethod
    def remove_cells(board: List[List[int]], count: int) -> List[List[int]]:
        """
        Remove 'count' cells from a completed board.
        
        Args:
            board: Completed Sudoku board
            count: Number of cells to remove
            
        Returns:
            Board with 'count' empty cells (represented as 0)
        """
        board_copy = deepcopy(board)
        removed = 0
        attempts = 0
        max_attempts = 100

        while removed < count and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board_copy[row][col] != 0:
                board_copy[row][col] = 0
                removed += 1
            attempts += 1

        return board_copy

    @staticmethod
    def generate_easy_board() -> Tuple[List[List[int]], str]:
        """Generate board with 1 empty cell."""
        completed = SudokuBoardGenerator.generate_completed_board()
        board = SudokuBoardGenerator.remove_cells(completed, 1)
        player = random.choice(["P1", "P2"])
        return board, player

    @staticmethod
    def generate_medium_board() -> Tuple[List[List[int]], str]:
        """Generate board with 2-4 empty cells."""
        completed = SudokuBoardGenerator.generate_completed_board()
        num_empty = random.randint(2, 4)
        board = SudokuBoardGenerator.remove_cells(completed, num_empty)
        player = random.choice(["P1", "P2"])
        return board, player

    @staticmethod
    def generate_hard_board() -> Tuple[List[List[int]], str]:
        """Generate board with 5-8 empty cells."""
        completed = SudokuBoardGenerator.generate_completed_board()
        num_empty = random.randint(5, 8)
        board = SudokuBoardGenerator.remove_cells(completed, num_empty)
        player = random.choice(["P1", "P2"])
        return board, player

    @staticmethod
    def generate_a_bit_more_hard_board() -> Tuple[List[List[int]], str]:
        """Generate board with 9-12 empty cells."""
        completed = SudokuBoardGenerator.generate_completed_board()
        num_empty = random.randint(9, 12)
        board = SudokuBoardGenerator.remove_cells(completed, num_empty)
        player = random.choice(["P1", "P2"])
        return board, player

    @staticmethod
    def generate_tiebreaking_board() -> Tuple[List[List[int]], str]:
        """
        Generate board where multiple moves have same minimax value.
        This requires careful construction.
        """
        # Start with completed board and remove cells strategically
        completed = SudokuBoardGenerator.generate_completed_board()
        board = SudokuBoardGenerator.remove_cells(completed, 3)
        
        # Ensure we have at least 2 valid moves
        valid_moves = SudokuValidator.get_valid_moves(board)
        while len(valid_moves) < 2:
            board = SudokuBoardGenerator.remove_cells(completed, 3)
            valid_moves = SudokuValidator.get_valid_moves(board)

        player = random.choice(["P1", "P2"])
        return board, player

    @staticmethod
    def generate_random_board() -> Tuple[List[List[int]], str]:
        """Generate board with random number of empty cells."""
        completed = SudokuBoardGenerator.generate_completed_board()
        num_empty = random.randint(1, 21)
        board = SudokuBoardGenerator.remove_cells(completed, num_empty)
        player = random.choice(["P1", "P2"])
        return board, player


# ============================================================================
# MINIMAX SOLVER (GROUND TRUTH)
# ============================================================================

class MinimaxSolver:
    """Independent Minimax solver for ground truth computation."""

    def __init__(self):
        """Initialize solver."""
        self.memo = {}

    def clear_memo(self):
        """Clear memoization cache."""
        self.memo = {}

    def board_to_key(self, board: List[List[int]]) -> tuple:
        """Convert board to hashable key for memoization."""
        return tuple(tuple(row) for row in board)

    def evaluate_state(self, board: List[List[int]], is_max_player: bool) -> int:
        """
        Evaluate board state without making moves (terminal evaluation).
        
        Args:
            board: Current board state
            is_max_player: True if evaluating for MAX player (P1)
            
        Returns:
            Heuristic score
        """
        # Count empty cells
        empty_count = sum(row.count(0) for row in board)
        
        # If board is full, it's a terminal state (score 0, no moves)
        if empty_count == 0:
            return 0
        
        # Heuristic: favor states with fewer empty cells for current player
        if is_max_player:
            return empty_count
        else:
            return -empty_count

    def minimax(
        self,
        board: List[List[int]],
        is_max_player: bool,
        depth: int = 0,
        max_depth: int = None
    ) -> Tuple[int, Optional[Tuple[int, int, int]]]:
        """
        Minimax algorithm without alpha-beta pruning.
        
        Args:
            board: Current board state
            is_max_player: True if maximizing player's turn
            depth: Current recursion depth
            max_depth: Maximum depth to search (None = exhaustive)
            
        Returns:
            (minimax_value, best_move) where best_move is (row, col, num) or None
        """
        # Memoization key
        board_key = self.board_to_key(board)
        memo_key = (board_key, is_max_player)

        if memo_key in self.memo:
            return self.memo[memo_key]

        # Get valid moves
        valid_moves = SudokuValidator.get_valid_moves(board)

        # Terminal state: no valid moves or max depth reached
        if not valid_moves or (max_depth is not None and depth >= max_depth):
            value = self.evaluate_state(board, is_max_player)
            self.memo[memo_key] = (value, None)
            return value, None

        best_value = float('-inf') if is_max_player else float('inf')
        best_move = None

        # Try all valid moves in sorted order (for consistent tie-breaking)
        for move in valid_moves:
            row, col, num = move
            
            # Apply move
            new_board = deepcopy(board)
            new_board[row][col] = num
            
            # Recurse
            next_value, _ = self.minimax(new_board, not is_max_player, depth + 1, max_depth)
            
            # Add move's score
            move_score = num if not is_max_player else -num  # P2 is minimizing in our scoring
            combined_value = next_value + (num if is_max_player else -num)

            # Update best move
            if is_max_player:
                if combined_value > best_value:
                    best_value = combined_value
                    best_move = move
            else:
                if combined_value < best_value:
                    best_value = combined_value
                    best_move = move

        # Store in memo
        result = (best_value, best_move)
        self.memo[memo_key] = result
        return result

    def compute_best_move(
        self,
        board: List[List[int]],
        is_max_player: bool
    ) -> Tuple[Optional[Tuple[int, int, int]], Dict]:
        """
        Compute the best move using Minimax.
        
        Args:
            board: Current board state
            is_max_player: True for P1, False for P2
            
        Returns:
            (best_move, info_dict) where best_move is (row, col, num) or None
        """
        self.clear_memo()
        
        valid_moves = SudokuValidator.get_valid_moves(board)
        
        if not valid_moves:
            return None, {"no_moves": True}

        # Get minimax value and best move
        _, best_move = self.minimax(board, is_max_player)
        
        if best_move is None:
            return None, {"no_moves": True}

        return best_move, {"valid_moves_count": len(valid_moves)}


# ============================================================================
# INPUT/OUTPUT FILE HANDLING
# ============================================================================

class FileHandler:
    """Handles reading and writing test files."""

    @staticmethod
    def write_input_file(
        board: List[List[int]],
        current_player: str,
        filepath: str
    ) -> None:
        """
        Write test case to input file.
        
        Args:
            board: 9x9 Sudoku board (0-indexed)
            current_player: "P1" or "P2"
            filepath: Path to input file
        """
        with open(filepath, 'w') as f:
            for row in board:
                line = ' '.join(str(cell) if cell != 0 else '.' for cell in row)
                f.write(line + '\n')
            f.write(current_player + '\n')

    @staticmethod
    def read_output_file(filepath: str) -> Dict:
        """
        Parse output file from student solution.
        
        Args:
            filepath: Path to output file
            
        Returns:
            Dictionary with parsed output or error info
        """
        result = {
            "success": False,
            "row": None,
            "col": None,
            "number": None,
            "p1_score": None,
            "p2_score": None,
            "board": None,
            "error": None
        }

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            if not content.strip():
                result["error"] = "Empty output file"
                return result

            # Parse Best Move
            best_move_match = re.search(r'Best Move:', content)
            row_match = re.search(r'Row\s*=\s*(\d+)', content)
            col_match = re.search(r'Column\s*=\s*(\d+)', content)
            num_match = re.search(r'Number\s*=\s*(\d+)', content)

            if not (row_match and col_match and num_match):
                result["error"] = "Could not parse Best Move"
                return result

            result["row"] = int(row_match.group(1)) - 1  # Convert to 0-indexed
            result["col"] = int(col_match.group(1)) - 1
            result["number"] = int(num_match.group(1))

            # Parse Scores
            p1_score_match = re.search(r'Player\s+1\s+Score\s*=\s*(\d+)', content)
            p2_score_match = re.search(r'Player\s+2\s+Score\s*=\s*(\d+)', content)

            if not (p1_score_match and p2_score_match):
                result["error"] = "Could not parse scores"
                return result

            result["p1_score"] = int(p1_score_match.group(1))
            result["p2_score"] = int(p2_score_match.group(1))

            # Parse Updated Board (colon after header is optional)
            board_match = re.search(r'Updated Sudoku Board:?\s*\n((?:(?:[0-9.].*\n)*[0-9.].*))', content)
            if board_match:
                board_text = board_match.group(1)
                board = []
                for line in board_text.strip().split('\n'):
                    if line.strip():
                        row_data = line.strip().split()
                        board_row = [int(cell) if cell != '.' else 0 for cell in row_data]
                        board.append(board_row)

                if len(board) == 9 and all(len(row) == 9 for row in board):
                    result["board"] = board
                else:
                    result["error"] = "Invalid board dimensions in output"
                    return result
            else:
                result["error"] = "Could not parse board"
                return result

            result["success"] = True
            return result

        except Exception as e:
            result["error"] = f"Exception: {str(e)}"
            return result


# ============================================================================
# VALIDATION LOGIC
# ============================================================================

class OutputValidator:
    """Validates student output against ground truth."""

    @staticmethod
    def validate_move_validity(
        original_board: List[List[int]],
        row: int,
        col: int,
        number: int
    ) -> Tuple[bool, str]:
        """
        Validate that the move is legal.
        
        Returns:
            (is_valid, error_message)
        """
        # Check bounds
        if not (0 <= row < 9 and 0 <= col < 9 and 1 <= number <= 9):
            return False, f"Move ({row}, {col}, {number}) out of bounds"

        # Check cell was empty
        if original_board[row][col] != 0:
            return False, f"Cell ({row}, {col}) was not empty"

        # Check if placement is valid
        if not SudokuValidator.is_valid_placement(original_board, row, col, number):
            return False, f"Number {number} is not valid at ({row}, {col})"

        return True, ""

    @staticmethod
    def validate_board_update(
        original_board: List[List[int]],
        updated_board: List[List[int]],
        row: int,
        col: int,
        number: int
    ) -> Tuple[bool, str]:
        """
        Validate that only one cell changed correctly.
        
        Returns:
            (is_valid, error_message)
        """
        # Check dimensions
        if len(updated_board) != 9 or any(len(row) != 9 for row in updated_board):
            return False, "Invalid board dimensions"

        changes = []
        for i in range(9):
            for j in range(9):
                if original_board[i][j] != updated_board[i][j]:
                    changes.append((i, j, original_board[i][j], updated_board[i][j]))

        # Should have exactly one change
        if len(changes) != 1:
            return False, f"Expected 1 change, got {len(changes)}"

        change_row, change_col, old_val, new_val = changes[0]

        # Change should match the move
        if (change_row, change_col, new_val) != (row, col, number):
            return False, (
                f"Change at ({change_row}, {change_col}): {old_val} -> {new_val} "
                f"doesn't match move ({row}, {col}, {number})"
            )

        return True, ""

    @staticmethod
    def validate_scores(
        original_board: List[List[int]],
        updated_board: List[List[int]],
        current_player: str,
        row: int,
        col: int,
        number: int,
        p1_score: int,
        p2_score: int,
        p1_prev_score: int = 0,
        p2_prev_score: int = 0
    ) -> Tuple[bool, str]:
        """
        Validate score calculation.
        
        Returns:
            (is_valid, error_message)
        """
        # Calculate expected score change
        if current_player == "P1":
            expected_p1 = p1_prev_score + number
            expected_p2 = p2_prev_score
        else:  # P2
            expected_p1 = p1_prev_score
            expected_p2 = p2_prev_score + number

        if p1_score != expected_p1 or p2_score != expected_p2:
            return False, (
                f"Score mismatch. Expected P1={expected_p1}, P2={expected_p2}; "
                f"Got P1={p1_score}, P2={p2_score}"
            )

        return True, ""

    @staticmethod
    def validate_move_optimality(
        original_board: List[List[int]],
        current_player: str,
        row: int,
        col: int,
        number: int
    ) -> Tuple[bool, str, Dict]:
        """
        Validate that the move is optimal according to Minimax.
        
        Returns:
            (is_valid, error_message, debug_info)
        """
        solver = MinimaxSolver()
        is_max_player = (current_player == "P1")
        
        best_move, info = solver.compute_best_move(original_board, is_max_player)

        if best_move is None:
            return False, "No valid moves available (unexpected)", {}

        expected_row, expected_col, expected_num = best_move
        actual_move = (row, col, number)

        if actual_move == best_move:
            return True, "", {"expected": best_move, "actual": actual_move}
        else:
            return False, (
                f"Suboptimal move. Expected ({expected_row}, {expected_col}, {expected_num}); "
                f"Got ({row}, {col}, {number})"
            ), {"expected": best_move, "actual": actual_move}


# ============================================================================
# TEST CASE MANAGEMENT
# ============================================================================

class TestCase:
    """Represents a single test case."""

    def __init__(
        self,
        case_id: int,
        category: str,
        board: List[List[int]],
        current_player: str
    ):
        """Initialize test case."""
        self.case_id = case_id
        self.category = category
        self.board = deepcopy(board)
        self.current_player = current_player
        self.result = None  # Will store TestResult

    def __repr__(self):
        return f"TestCase(id={self.case_id}, category={self.category})"


class TestResult:
    """Stores result of test case execution."""

    def __init__(self, test_case: TestCase):
        """Initialize test result."""
        self.test_case = test_case
        self.status = "PENDING"  # PASS, FAIL, ERROR
        self.reason = None
        self.expected_move = None
        self.actual_move = None
        self.expected_scores = None
        self.actual_scores = None
        self.validation_errors = []
        self.execution_error = None

    def __repr__(self):
        return f"TestResult(id={self.test_case.case_id}, status={self.status})"


# ============================================================================
# TEST EXECUTION
# ============================================================================

class TestExecutor:
    """Executes tests and validates results."""

    def __init__(self, input_file: str, output_file: str, solution_script: str):
        """Initialize executor."""
        self.input_file = input_file
        self.output_file = output_file
        self.solution_script = solution_script

    def run_student_solution(self) -> Tuple[bool, str]:
        """
        Execute student solution.
        
        Returns:
            (success, error_message)
        """
        try:
            result = subprocess.run(
                ["python", self.solution_script, self.input_file, self.output_file],
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode != 0:
                error_msg = f"Exit code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr[:200]}"
                return False, error_msg

            return True, ""

        except subprocess.TimeoutExpired:
            return False, "Timeout (30s exceeded)"
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def execute_test_case(self, test_case: TestCase) -> TestResult:
        """
        Execute a single test case.
        
        Args:
            test_case: TestCase to execute
            
        Returns:
            TestResult with pass/fail status
        """
        result = TestResult(test_case)

        # Compute expected move and scores
        solver = MinimaxSolver()
        is_max_player = (test_case.current_player == "P1")
        expected_move, _ = solver.compute_best_move(test_case.board, is_max_player)

        if expected_move is None:
            result.status = "ERROR"
            result.reason = "No valid moves for test case"
            return result

        result.expected_move = expected_move

        # Compute expected scores
        if is_max_player:
            result.expected_scores = (expected_move[2], 0)  # (P1, P2)
        else:
            result.expected_scores = (0, expected_move[2])

        # Write input file
        try:
            FileHandler.write_input_file(
                test_case.board,
                test_case.current_player,
                self.input_file
            )
        except Exception as e:
            result.status = "ERROR"
            result.reason = f"Failed to write input: {str(e)}"
            return result

        # Run student solution
        success, error_msg = self.run_student_solution()
        if not success:
            result.status = "ERROR"
            result.execution_error = error_msg
            return result

        # Parse output
        parsed = FileHandler.read_output_file(self.output_file)
        if not parsed["success"]:
            result.status = "ERROR"
            result.reason = parsed["error"]
            return result

        # Extract actual results
        row = parsed["row"]
        col = parsed["col"]
        number = parsed["number"]
        p1_score = parsed["p1_score"]
        p2_score = parsed["p2_score"]
        updated_board = parsed["board"]

        result.actual_move = (row, col, number)
        result.actual_scores = (p1_score, p2_score)

        # Validate results
        # 1. Move validity
        is_valid, error = OutputValidator.validate_move_validity(
            test_case.board, row, col, number
        )
        if not is_valid:
            result.validation_errors.append(f"Move Validity: {error}")

        # 2. Board update
        is_valid, error = OutputValidator.validate_board_update(
            test_case.board, updated_board, row, col, number
        )
        if not is_valid:
            result.validation_errors.append(f"Board Update: {error}")

        # 3. Scores
        is_valid, error = OutputValidator.validate_scores(
            test_case.board, updated_board, test_case.current_player,
            row, col, number, p1_score, p2_score, 0, 0
        )
        if not is_valid:
            result.validation_errors.append(f"Scores: {error}")

        # 4. Move optimality
        is_valid, error, debug_info = OutputValidator.validate_move_optimality(
            test_case.board, test_case.current_player, row, col, number
        )
        if not is_valid:
            result.validation_errors.append(f"Optimality: {error}")

        # Determine overall status
        if result.validation_errors:
            result.status = "FAIL"
            result.reason = result.validation_errors[0]
        else:
            result.status = "PASS"

        return result


# ============================================================================
# REPORTING
# ============================================================================

class ReportGenerator:
    """Generates test reports."""

    @staticmethod
    def format_board(board: List[List[int]]) -> str:
        """Format board for display."""
        lines = []
        for row in board:
            line = ' '.join(str(cell) if cell != 0 else '.' for cell in row)
            lines.append(line)
        return '\n'.join(lines)

    @staticmethod
    def generate_test_report(result: TestResult) -> str:
        """Generate detailed test report in required format."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"TEST CASE {result.test_case.case_id:02d}")
        lines.append("=" * 60)
        lines.append("")

        # INPUT BOARD section
        lines.append("INPUT BOARD")
        lines.append("-" * 60)
        lines.append(ReportGenerator.format_board(result.test_case.board))
        lines.append("")
        lines.append(f"Current Player: {result.test_case.current_player}")
        lines.append("")

        if result.status == "ERROR":
            # Error section
            lines.append("ERROR")
            lines.append("-" * 60)
            if result.execution_error:
                lines.append(f"Execution Error: {result.execution_error}")
            else:
                lines.append(f"Error: {result.reason}")
            lines.append("")
            lines.append("OVERALL RESULT  : ERROR")
            lines.append("")
            return '\n'.join(lines)

        # EXPECTED RESULT section
        lines.append("EXPECTED RESULT")
        lines.append("-" * 60)
        lines.append("Best Move:")
        lines.append(f"Row = {result.expected_move[0] + 1}")
        lines.append(f"Column = {result.expected_move[1] + 1}")
        lines.append(f"Number = {result.expected_move[2]}")
        lines.append("")
        lines.append(f"Player 1 Score = {result.expected_scores[0]}")
        lines.append(f"Player 2 Score = {result.expected_scores[1]}")
        lines.append("")
        lines.append("Expected Board:")
        
        # Compute expected board
        expected_board = deepcopy(result.test_case.board)
        expected_board[result.expected_move[0]][result.expected_move[1]] = result.expected_move[2]
        lines.append(ReportGenerator.format_board(expected_board))
        lines.append("")

        # ACTUAL RESULT section
        lines.append("ACTUAL RESULT")
        lines.append("-" * 60)
        lines.append("Best Move:")
        lines.append(f"Row = {result.actual_move[0] + 1}")
        lines.append(f"Column = {result.actual_move[1] + 1}")
        lines.append(f"Number = {result.actual_move[2]}")
        lines.append("")
        lines.append(f"Player 1 Score = {result.actual_scores[0]}")
        lines.append(f"Player 2 Score = {result.actual_scores[1]}")
        lines.append("")
        lines.append("Actual Board:")
        
        # Compute actual board
        actual_board = deepcopy(result.test_case.board)
        actual_board[result.actual_move[0]][result.actual_move[1]] = result.actual_move[2]
        lines.append(ReportGenerator.format_board(actual_board))
        lines.append("")

        # VALIDATION section
        lines.append("VALIDATION")
        lines.append("-" * 60)
        
        # Move check
        is_valid_move, _ = OutputValidator.validate_move_validity(
            result.test_case.board, result.actual_move[0], 
            result.actual_move[1], result.actual_move[2]
        )
        move_status = "PASS" if is_valid_move else "FAIL"
        lines.append(f"Move Check      : {move_status}")

        # Score check
        score_valid = (result.actual_scores == result.expected_scores)
        score_status = "PASS" if score_valid else "FAIL"
        lines.append(f"Score Check     : {score_status}")

        # Board check
        is_valid_board, _ = OutputValidator.validate_board_update(
            result.test_case.board, actual_board,
            result.actual_move[0], result.actual_move[1], result.actual_move[2]
        )
        board_status = "PASS" if is_valid_board else "FAIL"
        lines.append(f"Board Check     : {board_status}")

        # Tie-breaking check
        is_optimal, _, _ = OutputValidator.validate_move_optimality(
            result.test_case.board, result.test_case.current_player,
            result.actual_move[0], result.actual_move[1], result.actual_move[2]
        )
        tiebreak_status = "PASS" if is_optimal else "FAIL"
        lines.append(f"Tie Break Check : {tiebreak_status}")

        lines.append("")
        lines.append(f"OVERALL RESULT  : {result.status}")
        lines.append("")

        return '\n'.join(lines)

    @staticmethod
    def generate_summary_report(results: List[TestResult]) -> str:
        """Generate summary report."""
        lines = []
        lines.append("=" * 60)
        lines.append("SUMMARY REPORT")
        lines.append("=" * 60)
        lines.append("")

        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")
        errors = sum(1 for r in results if r.status == "ERROR")
        total = len(results)

        pass_rate = (passed / total * 100) if total > 0 else 0

        lines.append(f"Total Tests  : {total}")
        lines.append(f"Passed       : {passed}")
        lines.append(f"Failed       : {failed}")
        lines.append(f"Errors       : {errors}")
        lines.append(f"Pass Rate    : {pass_rate:.1f}%")
        lines.append("")

        # Breakdown by category
        categories = {}
        for result in results:
            cat = result.test_case.category
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "errors": 0}
            
            if result.status == "PASS":
                categories[cat]["passed"] += 1
            elif result.status == "FAIL":
                categories[cat]["failed"] += 1
            else:
                categories[cat]["errors"] += 1

        lines.append("Breakdown by Category:")
        for cat in sorted(categories.keys()):
            stats = categories[cat]
            total_cat = sum(stats.values())
            pass_rate_cat = (stats["passed"] / total_cat * 100) if total_cat > 0 else 0
            lines.append(f"  {cat:<20} : {stats['passed']:2d}/{total_cat:2d} ({pass_rate_cat:5.1f}%)")

        lines.append("")
        return '\n'.join(lines)


# ============================================================================
# MAIN TEST FRAMEWORK
# ============================================================================

class TestFramework:
    """Main test framework orchestrator."""

    def __init__(self, workspace_dir: str = "."):
        """Initialize framework."""
        self.workspace_dir = Path(workspace_dir)
        self.input_file = str(self.workspace_dir / "inputPS1.txt")
        self.output_file = str(self.workspace_dir / "outputPS1.txt")
        self.solution_script = str(self.workspace_dir / "solutionPS1.py")
        self.report_file = str(self.workspace_dir / "validation_report.txt")
        self.test_cases = []
        self.results = []

    def generate_test_cases(self) -> None:
        """Generate all 50 test cases."""
        print("Generating test cases...")
        case_id = 1

        # Category 1: Easy (1 empty cell)
        for _ in range(10):
            board, player = SudokuBoardGenerator.generate_easy_board()
            self.test_cases.append(TestCase(case_id, "Easy", board, player))
            case_id += 1

        # Category 2: Medium (2-4 empty cells)
        for _ in range(10):
            board, player = SudokuBoardGenerator.generate_medium_board()
            self.test_cases.append(TestCase(case_id, "Medium", board, player))
            case_id += 1

        # Category 3: Hard (5-8 empty cells)
        for _ in range(10):
            board, player = SudokuBoardGenerator.generate_hard_board()
            self.test_cases.append(TestCase(case_id, "Hard", board, player))
            case_id += 1

        # Category 4: A Bit More Hard (9-12 empty cells)
        for _ in range(10):
            board, player = SudokuBoardGenerator.generate_a_bit_more_hard_board()
            self.test_cases.append(TestCase(case_id, "A Bit More Hard", board, player))
            case_id += 1

        # Category 5: Tie-breaking
        for _ in range(10):
            board, player = SudokuBoardGenerator.generate_tiebreaking_board()
            self.test_cases.append(TestCase(case_id, "Tie-Breaking", board, player))
            case_id += 1

        # Category 6: Randomized
        for _ in range(10):
            board, player = SudokuBoardGenerator.generate_random_board()
            self.test_cases.append(TestCase(case_id, "Randomized", board, player))
            case_id += 1

        print(f"Generated {len(self.test_cases)} test cases")

    def run_all_tests(self) -> None:
        """Execute all test cases."""
        print(f"Running {len(self.test_cases)} tests...")
        executor = TestExecutor(self.input_file, self.output_file, self.solution_script)

        for i, test_case in enumerate(self.test_cases, 1):
            if i % 10 == 0:
                print(f"  Executing test {i}/{len(self.test_cases)}...")

            result = executor.execute_test_case(test_case)
            self.results.append(result)

        print(f"Completed all tests")

    def generate_report(self) -> str:
        """Generate complete report."""
        lines = []

        # Individual test reports
        for result in self.results:
            lines.append(ReportGenerator.generate_test_report(result))

        # Summary report
        lines.append(ReportGenerator.generate_summary_report(self.results))

        return '\n'.join(lines)

    def save_report(self, report: str) -> None:
        """Save report to file."""
        with open(self.report_file, 'w') as f:
            f.write(report)
        print(f"Report saved to {self.report_file}")

    def run(self) -> None:
        """Run complete test framework."""
        print("=" * 60)
        print("SUDOKU MINIMAX TEST FRAMEWORK")
        print("=" * 60)
        print()

        self.generate_test_cases()
        self.run_all_tests()
        report = self.generate_report()

        # Print to console
        print()
        print(report)

        # Save to file
        self.save_report(report)

        print()
        print("=" * 60)
        print("Testing Complete!")
        print("=" * 60)
        print()
        print("✓ Full detailed report saved to: validation_report.txt")
        print()


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    # Get workspace directory
    workspace_dir = Path(__file__).parent
    
    # Create and run framework
    framework = TestFramework(str(workspace_dir))
    framework.run()


if __name__ == "__main__":
    main()
