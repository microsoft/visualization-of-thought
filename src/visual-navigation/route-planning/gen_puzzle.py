import base64
import os
import argparse
import json
from string import Template
import glob

parser = argparse.ArgumentParser()
parser.add_argument('--config-folder', type=str, default='../configurations')
parser.add_argument('--puzzle-folder', type=str, default='./puzzles')
parser.add_argument('--prompt-folder', type=str, default='./prompts')
parser.add_argument('--output-jsonl', required=True, help='Path to the output JSONL file.')
parser.add_argument('--difficulty', required=True, type=int, help='difficulty level of generated puzzles')


opt = parser.parse_args()
icon_to_image_dict = {}
    
def fill_prompt(prompt_path: str, substitute_dict:dict, output_path: str):
    with open(prompt_path) as fprompt, open(output_path, 'w') as filled:
        prompt_template = Template(fprompt.read())
        filled.write(prompt_template.substitute(substitute_dict))

def get_substitute_dict(data: dict)->dict:
    
    substitute_dict = {'ENCODED_MAP': data['ENCODED_MAP'],
                       'INITIAL_MAP': data['INITIAL_MAP']}

    return substitute_dict

def add_jsonl(config_folder, case_folder, output_jsonl):
    text_path = os.path.join(case_folder, 'desc-text.txt')
    mm_path = os.path.join(case_folder, 'desc-multimodal.txt')
    answer_path = os.path.join(case_folder, 'answer.txt')

    if os.path.isfile(text_path) and os.path.isfile(mm_path) and os.path.isfile(answer_path):
        with open(text_path, 'r') as f:
            desc = f.read().strip()
        try:
            with open(answer_path, 'r') as f:
                answer = json.load(f)
            with open(mm_path, 'r') as f:
                desc_multimodal = json.load(f)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON in {mm_path} or {answer_path}")
            return

        with open(output_jsonl, 'a') as outfile:
            json_record = {
                "desc": desc,
                "desc_multimodal": desc_multimodal,
                "answer": answer,
                "puzzle_path": os.path.relpath(case_folder, os.path.dirname(output_jsonl)),
                "config_path": os.path.relpath(config_folder, os.path.dirname(output_jsonl)),
                "difficulty": opt.difficulty,
                "instance_id": os.path.relpath(case_folder, opt.puzzle_folder)
            }
            outfile.write(json.dumps(json_record) + '\n')

if __name__ == '__main__':
    data_root = opt.config_folder
    output_root = opt.puzzle_folder
    prompt_folder = opt.prompt_folder
    setting_templates = [(os.path.splitext(x)[0], os.path.join(prompt_folder, x)) for x in os.listdir(prompt_folder) if x.find('-') != -1]
    print(setting_templates)
    failed_cases = []
    for case_id in os.listdir(data_root):
        if not case_id.isdigit():
            continue
        try:
            print(f'processing {case_id}')
            data_folder = os.path.join(data_root, case_id)
            config_path = os.path.join(data_folder, 'solution.json')
            problem_path = os.path.join(data_folder, 'map.txt')
            output_folder = os.path.join(output_root, case_id)
            os.makedirs(output_folder, exist_ok=True)
            config_json = None
            with open(config_path, 'r') as f:
                config_json = json.load(f)
            instruction_list = []
            img_path = os.path.join(data_folder, 'map.png')
            config_json['ENCODED_MAP'] = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
            config_json['INITIAL_MAP'] = open(problem_path, 'r').read().strip()

            substitute_dict = get_substitute_dict(config_json)
            for setting, template in setting_templates:
                prompt_path = os.path.join(output_folder, f'{setting}.txt')
                if os.path.exists(prompt_path):
                    continue
                fill_prompt(template, substitute_dict, prompt_path)
            open(os.path.join(output_folder, 'answer.txt'), 'w').write(json.dumps(config_json['solution']))

            add_jsonl(data_folder, output_folder, opt.output_jsonl)
        except Exception as e:
            print(str(e))
            failed_cases.append(case_id)
    logging_path = os.path.join(output_root, 'error.log')
    with open(logging_path, 'w') as f:
        f.write('\n'.join(failed_cases))
