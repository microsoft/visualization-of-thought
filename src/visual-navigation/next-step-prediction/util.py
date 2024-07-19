from email.policy import default
import glob
import os
import re
import json, string

default_answer = 'NULL'

def extract_answer_single_line(line: str, override_patterns: list[str]):
    patterns = [
        r'[A-D]\. (\w+)\.',
        r'[A-D]\. (\w+)$',
        r'[A-D]\.(\w+)\.',
        r'[A-D]\.(\w+)$',
        r'(?:is|be) [A-D]\. (\w+)[,]',
        r'(Up|up|Right|right|Down|down|Left|left) \([A-D]\)',
        r'\([A-D]\. (\w+)\)',
        r'"[A-D]\. (\w+)"',
        r'\**[A-D]\. (\w+)\**',
        r'\**Answer:\** ([A-D])',
        r'\*\*([A-D])\*\*',
        r'answer is[\s*:]\s*\**([A-D])\**\.',
        r'(?:"|`|\*\*)?(Up|up|Right|right|Down|down|Left|left)(?:"|`|\*\*)? \((?:option )?[A-D]\)',
        r'(left(?:ward|wards)?|right(?:ward|wards)?|up(?:ward|wards)?|down(?:ward|wards)?) \([A-D]\)',
        # Add more patterns as needed
    ]
    if override_patterns:
        patterns = override_patterns
    for pattern in patterns:
        res = re.search(pattern, line)
        if res:
            return res.group(1).split('ward')[0]
    return ''

def extract_answer_multiline(lines):
    lines += '\n'
    patterns = [
        r"\n\n[A-D]\. (?:Move |move )?(\w+).*$\n(?![B-D]\. )", #match the answer without subsequent options
        r":\n[A-D]\. (?:Move |move )?(\w+).*$\n(?![B-D]\. )",  #match answer when there's no preceeding empty line
    ]
    for pattern in patterns:
        res = re.findall(pattern, lines, re.MULTILINE)
        if res:
            return res[-1].split('ward')[0]
    return ''

def check_none_answer(output:str):
    unmatched_default = 'NULL'
    patterns = [
        r'none of (?:the above|them)',
        r'next movement (?:is|would be) not (?:applicable|necessary)',
        r'there (?:is|would be) no next movement',
        r"there(?:'s| is| would be) no need for",
        r'no further \b\w+\b (?:is |are |would be )?(?:required|necessary|needed)',
        r'cannot (\b\w+\b )?(?:proceed|determine)',
        r'\bNone\b',
    ]
    for pattern in patterns:
        res = re.search(pattern, output, re.IGNORECASE)
        if res:
            return 'None'
    mistake_pattern = r'\b(?:mistake|error|discrepancy)\b'
    if re.search(mistake_pattern, output, re.IGNORECASE):
        return 'Incorrect'
    return unmatched_default

def match_dir_str(problem: str, option: str):
    global default_answer
    for dir_str in ['up', 'left', 'down', 'right']:
        if f'{option}. {dir_str}'.lower() in problem.lower():
            return dir_str
    return default_answer

def parse_result(problem: str, output: str, regex_patterns: list[str]):
    global default_answer
    parsed_answer = default_answer
    lines = output.split('\n')[::-1]
    for line in lines:
        cur = extract_answer_single_line(line, regex_patterns)
        if len(cur):
            parsed_answer = cur.lower()
            break
    if parsed_answer == default_answer:
        cur = extract_answer_multiline(output)
        if len(cur):
            parsed_answer = cur.lower()
    if parsed_answer == default_answer:
        parsed_answer = check_none_answer(output)
    #match option answer (A/B/C/D)
    if len(parsed_answer) == 1:
        parsed_answer = match_dir_str(problem, parsed_answer)
    return parsed_answer

def evaluate_single_instance(output:str, instance_json_info:json, regex_patterns: list[str]):
    global default_answer
    problem = instance_json_info['desc']

    parsed_result = parse_result(problem, output, regex_patterns)

    correct_answer = instance_json_info['answer']
    verbal_correct = parsed_result in correct_answer

    return {
        "verbal": {"answer": parsed_result, "correct": verbal_correct},
        "parse_fail": parsed_result == default_answer
    }
