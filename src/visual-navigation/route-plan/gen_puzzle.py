import base64
import os
import argparse
import json
from string import Template
import glob

parser = argparse.ArgumentParser()
parser.add_argument('--data-folder', type=str, default='../configurations')
parser.add_argument('--output-folder', type=str, default='prompt-instance')
parser.add_argument('--prompt-folder', type=str, default='./prompts')


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

if __name__ == '__main__':
    data_root = opt.data_folder
    output_root = opt.output_folder
    prompt_folder = opt.prompt_folder
    setting_templates = [(os.path.splitext(x)[0], os.path.join(prompt_folder, x)) for x in os.listdir(prompt_folder) if x.find('-') != -1]
    print(setting_templates)
    failed_cases = []
    total_cases = glob.glob(os.path.join(opt.data_folder, '*-map.txt'), recursive=True)
    for case in total_cases:
        try:
            print(f'processing {case}')
            data_folder = os.path.dirname(case)
            case_id = os.path.basename(case).split('-')[0]
            config_path = case.replace('map.txt', 'solution.json')
            problem_path = case
            output_folder = os.path.join(output_root, case_id)
            os.makedirs(output_folder, exist_ok=True)
            config_json = None
            with open(config_path, 'r') as f:
                config_json = json.load(f)
            instruction_list = []
            img_path = os.path.join(data_folder, f'{case_id}.png')
            config_json['ENCODED_MAP'] = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
            config_json['INITIAL_MAP'] = open(case, 'r').read().strip()

            substitute_dict = get_substitute_dict(config_json)
            for setting, template in setting_templates:
                prompt_path = os.path.join(output_folder, f'{setting}.txt')
                if os.path.exists(prompt_path):
                    continue
                fill_prompt(template, substitute_dict, prompt_path)
            open(os.path.join(output_folder, 'answer.txt'), 'w').write(json.dumps(config_json['solution']))
        except Exception as e:
            print(str(e))
            failed_cases.append(case_id)
    logging_path = os.path.join(output_root, 'error.log')
    with open(logging_path, 'w') as f:
        f.write('\n'.join(failed_cases))
