import re
import json

def merge_continous_move(all_steps: list[str]) -> list[str]:
    # This function skips continuous duplicates in the list
    if not all_steps:
        return []

    result = [all_steps[0]]  # Start with the first element

    for i in range(1, len(all_steps)):
        if all_steps[i] != all_steps[i - 1]:
            result.append(all_steps[i])

    return result

def parse_path_summary(output: str) -> list[str]:
    repeat_pattern = ['(?:so|thus)[^.!?]*(?:is|are):', 'the steps[^,.!?]*(?:are|were):', 'summary of steps:']
    valid_directions = []
    for pattern in repeat_pattern:
        matches = re.finditer(pattern, output, re.IGNORECASE)
        for match in matches:
            # Search for any of the direction words after the current match
            end_pos = match.end()
            subsequent_text = output[end_pos:]
            direction_matches = re.findall(r'\b(?:up|left|down|right)\b', subsequent_text, re.IGNORECASE)
            if len(direction_matches):
                return [x.lower() for x in direction_matches]

    return valid_directions

def remove_summary(output:list[str]) -> list[str]:
    repeat_pattern = ['(?:so|thus)[^.!?]*(?:is|are):', 'the steps[^,.!?]*(?:are|were):', 'summary of steps:', 'visual representation', 'destination', 'reach 🏢']
    for pattern in repeat_pattern:
        dir_occur = False
        for idx, line in enumerate(output):
            dir_occur |= len(re.findall(r'mov(?:e|ing) (left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?)', line, re.IGNORECASE))
            if idx and re.search(pattern, line, re.IGNORECASE):
                if not dir_occur:
                    break
                #print('remove dup')
                return output[:idx + 1]
    return output

def match_uniq_dir(output: str) -> list[str]:
    direction_pattern = r"\b(left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?|west|east|north|south)\b"
    match_res = re.findall(direction_pattern, output, re.IGNORECASE)
    total_dirs = []
    if match_res:
        cands = set([x for x in match_res])
        if len(cands) == 1:
            total_dirs = list(cands)
    return total_dirs

def parse_instructions(output: str, override_patterns: list[str]) -> list[str]:
    lines = output.split('\n')
    if not override_patterns:
        lines = remove_summary(lines) #applicable for gpt family
    instruction_patterns = [
        r"\d+[:\.].*?(?:mov(?:e|ing)|take(?:\s+the)?|go(?:ing)?)\s+(left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?)",
        r"^\d+\.\s*(left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?)",
        r'mov(?:e|ing) (left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?):',
        r'- .*(?:we can )?(?:only )?move (left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?)',
    ]
    if override_patterns:
        instruction_patterns = override_patterns
    valid_directions = []
    normalize_dict = {'west':'left', 'east':'right', 'north':'up', 'south':'down'}

    for line in lines:
        for pattern in instruction_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                cur = match.group(1).lower().split('ward')[0]
                valid_directions.append(cur if cur not in normalize_dict else normalize_dict[cur])
                continue
    return valid_directions

def parse_result(problem: str, output: str, regex_patterns: list[str]):
    parsed_steps = parse_path_summary(output)

    if not parsed_steps:
        parsed_steps = parse_instructions(output, regex_patterns)

    return merge_continous_move(parsed_steps)

def simulate_move(movements: list[str], answer: list[str]) -> int:
    valid_step = 0
    dir_idx = {'up': 0, 'left': 1, 'down': 2, 'right': 3}

    for idx, step in enumerate(movements):
        if valid_step < len(answer) and step == answer[valid_step]: #move forward
            valid_step += 1
        elif valid_step and (dir_idx[step] + 2) % 4 == dir_idx[answer[valid_step - 1]]: #turn around
            valid_step -= 1
    return valid_step

def evaluate_single_instance(output:str, instance_json_info:json, regex_patterns: list[str]):
    global default_answer
    problem = instance_json_info['desc']

    parsed_steps = parse_result(problem, output, regex_patterns)

    correct_answer = instance_json_info['answer']
    valid_step = simulate_move(parsed_steps, correct_answer)
    
    return {
        "verbal": {
            'valid_step': valid_step, 'remaining_step': len(correct_answer) - valid_step, 'total_cost': len(parsed_steps),
            'completing_rate': valid_step / len(correct_answer), 'succ': valid_step == len(correct_answer)
        },
        "parse_fail": len(parsed_steps) == 0,
    }
