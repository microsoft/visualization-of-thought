import base64
import os
import argparse
import json
from string import Template
import glob

parser = argparse.ArgumentParser()
parser.add_argument('--data-folder', type=str, default='../configurations')
parser.add_argument('--output-folder', type=str, default='puzzles')
parser.add_argument('--prompt-folder', type=str, default='./prompts-QA')


opt = parser.parse_args()
icon_to_image_dict = {}
    
def fill_prompt(prompt_path: str, substitute_dict:dict, output_path: str):
    with open(prompt_path) as fprompt, open(output_path, 'w') as filled:
        prompt_template = Template(fprompt.read())
        filled.write(prompt_template.substitute(substitute_dict))

def get_substitute_dict(data: dict)->dict:
    multimodal_instructions = [json.dumps({'type':'text', 'text':instruction}) for instruction in data['instruction_list']]
    
    substitute_dict = {'ENCODED_MAP': data['ENCODED_MAP'],
                       'INITIAL_MAP': data['INITIAL_MAP'],
                       'NAVIGATING_INSTRUCTIONS': '\n'.join(data['instruction_list']),
                       'MULTIMODAL_NAVAIGATING_INSTRUCTION': ','.join(multimodal_instructions)}

    return substitute_dict

        
if __name__ == '__main__':
    data_root = opt.data_folder
    output_root = opt.output_folder
    prompt_folder = opt.prompt_folder
    setting_templates = [(os.path.splitext(x)[0], os.path.join(prompt_folder, x)) for x in os.listdir(prompt_folder) if x.find('-') != -1]
    failed_cases = []
    total_cases = glob.glob(os.path.join(opt.data_folder, '*-map.txt'), recursive=True)
    for case in total_cases:
        case_id = os.path.basename(case).split('-')[0]
        try:
            print(f'processing {case_id}')
            config_path = os.path.join(data_root, f'{case_id}-solution.json')
            problem_path = os.path.join(data_root,f'{case_id}-map.txt')
            output_folder = os.path.join(output_root, case_id)
            os.makedirs(output_folder, exist_ok=True)
            config_json = None
            with open(config_path, 'r') as f:
                config_json = json.load(f)
            instruction_list = []
            img_path = os.path.join(data_root, f'{case_id}.png')
            config_json['ENCODED_MAP'] = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
            config_json['INITIAL_MAP'] = open(problem_path, 'r').read().strip()
            for idx, step in enumerate(config_json['solution']):
                if idx == len(config_json['solution']) - 1:
                    break
                instruction_list.append(f'{idx + 1}. Move {step} to the end of continuous road.')
                config_json['instruction_list'] = instruction_list
                question_folder = os.path.join(output_folder, 'QA', f'{idx}')
                os.makedirs(question_folder, exist_ok=True)
                substitute_dict = get_substitute_dict(config_json)
                for setting, template in setting_templates:
                    prompt_path = os.path.join(question_folder, f'{setting}.txt')
                    if os.path.exists(prompt_path):
                        continue
                    fill_prompt(template, substitute_dict, prompt_path)
                answer_path = os.path.join(question_folder, 'answer.txt')
                with open(answer_path, 'w') as f:
                    f.write('\n'.join([config_json['solution'][idx + 1]]))
        except Exception as e:
            print(str(e))
            failed_cases.append(case_id)
    logging_path = os.path.join(output_root, 'error.log')
    with open(logging_path, 'w') as f:
        f.write('\n'.join(failed_cases))