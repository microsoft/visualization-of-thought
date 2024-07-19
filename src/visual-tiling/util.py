import os
import re
import json

default_answer = 'NULL'

def extract_answer_single_line(line, polyomini_name, override_patterns: list[str]):
    patterns = [
        r'([A-C])\. Neither',
        r'([A-C])\.Neither',
        r'([A-B])\. (\d+) ',
        r'([A-B])\. (\d+),',
        r'([A-B])\. (\d+)\.',
        r'([A-B])\. (\d+)$',
        r'([A-B])\.(\d+) ',
        r'([A-B])\.(\d+),',
        r'([A-B])\.(\d+)\.',
        r'([A-B])\.(\d+)$',
        r'(?:V|v)ariation \d+ \(([A-B])\)',
        r'([A-B]) \(Variation \d+\)',
        r'Answer\**:\** ([A-C])',
        r'answer is \**([A-C])\**',
        r'([A-B])\. (\d+)\*\*',
        r'\*\*([A-C])\*\*',
        rf'{polyomini_name} is ([A-B])',
        rf'{polyomini_name} is (?:\*\*)?(?:Variation )?(\d+)',
        rf'{polyomini_name}[^,.]*Variation (\d+)[^,.]*is (?:the )?correct'
        # Add more patterns as needed
    ]

    for pattern in patterns:
        res = re.search(pattern, line)
        if res:
            return res.group(1)
    return ''

def extract_bounding_box(rectangle, emoji):
    min_row, min_col, max_row, max_col = len(rectangle), len(rectangle[0]), -1, -1

    for row_idx, row in enumerate(rectangle):
        for col_idx, char in enumerate(row):
            if char == emoji:
                min_row = min(min_row, row_idx)
                max_row = max(max_row, row_idx)
                min_col = min(min_col, col_idx)
                max_col = max(max_col, col_idx)

    # Check if the emoji was found and extract the sub-rectangle
    if min_row <= max_row and min_col <= max_col:
        return [row[min_col:max_col+1] for row in rectangle[min_row:max_row+1]]
    else:
        return None

def extract_answer_from_filled(problem: str, output: str, polyomino_type: str):
    global default_answer
    grid_pattern = r'```\n(.*?)\n```'
    empty_square = '⬜'
    emoji = re.search(rf'{polyomino_type} \((.)\)', problem, re.DOTALL).group(1)
    original_grid = re.findall(grid_pattern, problem, re.DOTALL)[0]
    output_grids = re.findall(grid_pattern, output, re.DOTALL)
    if len(output_grids) == 0:
        return default_answer
    final_grid = output_grids[-1]
    if len(original_grid) != len(final_grid):
        return default_answer
    
    #validate modifications
    violations = [idx for (idx, val) in enumerate(original_grid) if val != final_grid[idx] and original_grid[idx] != empty_square]
    if len(violations):
        return default_answer

    #find filled squares of provided polyomino
    rectangle = ["".join(char if char == emoji else empty_square for char in line) for line in final_grid.replace(' ', '').split('\n')]
    bbox = extract_bounding_box(rectangle, emoji)
    if not bbox is None:
        boxstr = '\n'.join(bbox)
        boxstr = f'\n```\n{boxstr}\n```'
        pos = problem.find(boxstr)
        if pos == -1:
            return default_answer
        regex_pattern = r'Variation (\d+) fitting into its bounding box:' + boxstr
        match = re.search(regex_pattern, problem, re.DOTALL | re.MULTILINE)
        return match_option(match.group(1), problem)
    return default_answer

def match_option(variation_name, problem):
    return 'A' if f'A. {variation_name}' in problem else 'B' if f'B. {variation_name}' in problem else 'C'


def parse_result(problem: str, output: str, polyomino_name: str, regex_patterns: list[str]):
    global default_answer
    parsed_answer = default_answer
    lines = output.split('\n')[::-1]
    for line in lines:
        cur = extract_answer_single_line(line, polyomino_name, regex_patterns)
        if len(cur):
            parsed_answer = cur if cur.isalpha() else match_option(cur, problem)
            break
    return parsed_answer

def evaluate_single_instance(output:str, instance_json_info:json, regex_patterns: list[str]):
    global default_answer
    puzzle_path = instance_json_info['puzzle_path']
    polyomino_name = os.path.basename(instance_json_info['puzzle_path'])
    problem = instance_json_info['desc']
    parsed_result = parse_result(problem, output, polyomino_name, regex_patterns)
    filled_result = 'NULL'
    try:
        filled_result = extract_answer_from_filled(problem, output, polyomino_name)
    except Exception as e:
        print(f'failed to extract visual answer from output of case {puzzle_path}, msg:{str(e)}')
    correct_answer = instance_json_info['answer']

    verbal_correct = parsed_result in correct_answer
    visual_correct = filled_result in correct_answer

    return {
        "verbal": {"answer": parsed_result, "correct": verbal_correct},
        "visual": {"answer": filled_result, "correct": visual_correct},
        "parse_fail": parsed_result == default_answer
    }
