import sys, time, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import solutionPS1 as s

def run_sample_case():
    board = [
        [5,3,4,6,7,8,9,1,0],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9],
    ]
    t0 = time.perf_counter()
    res = s.find_best_move(board, 'P2')
    t1 = time.perf_counter()
    print('sample_case result:', res, 'time:', t1-t0)


def run_full_minimax():
    full_board = [
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9],
    ]
    t0 = time.perf_counter()
    res = s.minimax(s.board_to_tuple(full_board), 'P1', {})
    t1 = time.perf_counter()
    print('full_minimax result:', res, 'time:', t1-t0)

if __name__ == '__main__':
    run_sample_case()
    run_full_minimax()
