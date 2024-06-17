import os
import sys
import argparse
import random
import json
from copy import deepcopy
from typing import Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join('../', os.path.dirname(SCRIPT_DIR)))

from emoji_to_image import emoji_to_image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

parser = argparse.ArgumentParser()
parser.add_argument('--turn', type=int, default=2)
parser.add_argument('--dest-folder', type=str, default='')
opt = parser.parse_args()

random.seed()

dir_path = os.path.dirname(os.path.realpath(__file__))

destination = '🏢'
start = '🏠'
road = '⬜'
wall = '🚧'

def move_forwards(movements:list[str], solution:json) -> (int, int, list[str]):
    wall = '🚧'
    dir_dict = {'up':[-1, 0], 'down':[1, 0], 'left':[0, -1], 'right':[0, 1]}
    xx, yy = solution['current_pos']
    grid = solution['cur_map']
    height, width = solution['height'], solution['width']
    is_reach_boundary = lambda move: (
    (next_y := yy + dir_dict[move][0]) >= 0 and
    next_y < height and
    (next_x := xx + dir_dict[move][1]) >= 0 and
    next_x < width and
    grid[next_y][next_x] != wall)

    applied_steps = set()
    for idx, move in enumerate(movements):
        while move in dir_dict and is_reach_boundary(move):
            yy += dir_dict[move][0]
            xx += dir_dict[move][1]
            applied_steps.add(idx)
    return (yy, xx, [movements[idx] for idx in applied_steps])

def validate_plan(y:int, x:int, vec_list:list[list], block_set:set) -> bool:
    yy, xx = y, x
    for vec in vec_list:
        yy += vec[0]
        xx += vec[1]
        node = (yy, xx)
        if node in block_set:
            return False
    return True

def add_block_set(node:Tuple, path_set:set, block_set:set):
    for move_vec in [[-1, 0], [0, -1], [1, 0], [0, 1]]:
        next_y = node[0] + move_vec[0]
        next_x = node[1] + move_vec[1]
        next_node = (next_y, next_x)
        if next_node not in path_set:
            block_set.add(next_node)

def make_one_move(node:Tuple, move_vec:list[int], path_set:set, block_set:set) -> Tuple:
    move_ahead = lambda pos, move_vec:(pos[0] + move_vec[0], pos[1] + move_vec[1])
    next_node = move_ahead(node, move_vec)
    path_set.add(next_node)
    add_block_set(node, path_set, block_set)
    return next_node

def span_path(dir_list:list[str]) -> list[list[int]]:
    total_move = []
    dir2idx = {'up':0, 'left':1, 'down':2, 'right':3}
    dir_move = [[-1, 0], [0, -1], [1, 0], [0, 1]]
    path_set, block_set = set(), set()
    yy, xx = 0, 0
    pre_move = None
    path_set.add((yy, xx))
    
    for cur_dir in dir_list:
        move = dir_move[dir2idx[cur_dir]]
        while not validate_plan(yy, xx, [move, move], block_set):
            node = (yy, xx)
            #TODO: need backtrace
            if not validate_plan(yy, xx, [pre_move], block_set):
                print('need backtrace, exit')
                return []
            yy, xx = make_one_move(node, pre_move, path_set, block_set)
            total_move.append(pre_move)
        for i in range(2): #a road is at least 3 squares long
            node = (yy, xx)
            yy, xx = make_one_move(node, move, path_set, block_set)
            total_move.append(move)
        pre_move = move
    return total_move

def gen_route(solution:json) -> list[list[int]]:
    updated_solution = deepcopy(solution)
    paths = []
    for move in updated_solution['solution']:
        src = updated_solution['current_pos']
        if len(paths) == 0:
            paths.append(src)
        yy, xx, _ = move_forwards([move], updated_solution)
        target = [xx, yy]
        updated_solution['current_pos'] = target
        paths.append(target)
    return paths

def gen_board_by_dir_list(dir_list:list[str]):
    total_move = span_path(dir_list)
    if len(total_move) == 0:
        return None
    u, d, l, r = 0, 0, 0, 0
    yy, xx = 0, 0
    for move in total_move:
        yy += move[0]
        xx += move[1]
        u = min(u, yy)
        d = max(d, yy)
        l = min(l, xx)
        r = max(r, xx)
   #move origin
    row_num = d - u + 1
    col_num = r - l + 1
    grid = []
    for i in range(row_num):
        grid.append([])
        for j in range(col_num):
            grid[i].append(wall)
    yy, xx = -u, -l
    for move in total_move:
        yy += move[0]
        xx += move[1]
        grid[yy][xx] = road
    grid[-u][-l] = start
    grid[yy][xx] = destination

    solution = {'initial_map':grid, 'cur_map': grid, 'height':row_num, 'width':col_num, 'solution':dir_list, 'current_pos':[-l, -u], 'start_pos':[-l, -u], 'dest_pos':[xx, yy]}
    solution['route_list'] = gen_route(solution)
    return solution

def get_all_dir_list(cur_idx:int, rest_step:int) ->list[list[str]]:
    dir_str = ['up', 'left', 'down', 'right']
    dir_list = []
    path_prefix = [dir_str[cur_idx]]
    if rest_step == 1:
        return [path_prefix]
    for i in [(cur_idx + 1) % 4, (cur_idx + 3) % 4]:
        for cand in get_all_dir_list(i, rest_step - 1):
            cur = deepcopy(path_prefix)
            cur.extend(cand)
            dir_list.append(cur)
    return dir_list

def format_grid(board) -> str:
    return '\n'.join([''.join(board[i]) for i in range(len(board))])

def gen_all_solutions(total_step:int):
    dest_folder = opt.dest_folder
    os.makedirs(dest_folder, exist_ok=True)
    file_idx = 1
    for i in range(4):
        for dir_list in get_all_dir_list(i, total_step):
            print('gen case:%d' %file_idx)
            solution = gen_board_by_dir_list(dir_list)
            if solution is None:
                continue

            map_file_path = os.path.join(dest_folder, '%d-map.txt' % file_idx)
            map_img_path = os.path.join(dest_folder, '%d.png' % file_idx)
            solution_file_path = os.path.join(dest_folder, '%d-solution.json' % file_idx)
            with open(map_file_path, 'w') as f:
                f.write(format_grid(solution['initial_map']))
            emoji_to_image(solution['initial_map'], map_img_path)
            with open(solution_file_path, 'w') as f:
                json.dump(solution, f)
            file_idx += 1

if __name__ == '__main__':
    gen_all_solutions(opt.turn)
