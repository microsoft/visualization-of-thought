import base64
import os
import argparse
import random
import sys
import json
from string import Template
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from emoji_to_image import emoji_to_image

parser = argparse.ArgumentParser()
parser.add_argument('--data-folder', type=str, default='data/level-2')
parser.add_argument('--output-folder', type=str, default='data/level-2')
parser.add_argument('--prompt-folder', type=str, default='./prompts')
parser.add_argument('--seed', type=int, default=42)


opt = parser.parse_args()
    
random.seed(opt.seed)

def fill_prompt(prompt_path: str, substitute_dict:dict, output_path: str):
    with open(prompt_path) as fprompt, open(output_path, 'w') as filled:
        prompt_template = Template(fprompt.read())
        filled.write(prompt_template.substitute(substitute_dict))

def get_substitute_dict(data: dict, options:dict)->dict:
    target_option = options[data['chosed_polyomino']]
    provided_polyominoes = [f'{idx + 1}. {item["polyomino_name"]} ({item["emoji"]})' for idx, item in enumerate(data['provided_polyomino_list'])]
    multimodal_provided_polyominoes = [json.dumps({'type':'text', 'text':f'{idx + 1}. {item["polyomino_name"]} ({item["emoji"]})'}) for idx, item in enumerate(data['provided_polyomino_list'])]
    multimodal_options = [json.dumps({'type':'text', 'text':option}) for option in target_option]
    substitute_dict = {'EMPTY_SQUARES': data['empty_squares'],
                        'TARGET_RECTANGLE': data['target_rectangle'], 
                        'ENCODED_RECTANGLE': data['encoded_rectangle'],
                       'PROVIDED_POLYOMINOES':'\n'.join(provided_polyominoes), 
                       'MULTIMODAL_PROVIDED_POLYOMINOES':','.join(multimodal_provided_polyominoes),
                       'POLYOMINO_VARIATIONS': data['variation_prompt_text'] , 
                       'MULTIMODAL_POLYOMINO_VARIATIONS': data['variation_prompt_multimodal'], 
                       'CHOSED_POLYOMINO': data['chosed_polyomino'],
                       'OPTIONS': '\n'.join(target_option),
                       'MULTIMODAL_OPTIONS': ','.join(multimodal_options)}
    return substitute_dict

def load_encoded_img_dict(img_folder) -> dict:
    img_dict = {}
    for img_id in os.listdir(img_folder):
        if not img_id.isdigit():
            continue
        img_path = os.path.join(img_folder, img_id)
        img_dict[f'IMG_{img_id}'] = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
    return img_dict

def gen_subset_variation(config_path:str, problem_path:str):
    """
    Generates a subset of variations for polyomino problems and creates prompts for corresponding variations.

    Args:
        config_path (str): Path to the configuration JSON file.
        problem_path (str): Path to the problem JSON file.

    Returns:
        tuple: Updated problem dictionary, list of prompt lines, options dictionary, and option answers dictionary.
    """
    subsets = []
    with open(config_path, 'r') as fconfig, open(problem_path, 'r') as fproblem:
        config = json.load(fconfig)
        problem = json.load(fproblem)

        # Iterate over each spatial configuration of all possible answers
        for answer in config['answers']:
            block_list = {}
            
            # Build a block list for each polyomino to ensure an unique answer
            for polyomino_name in config['provided_polyominoes']:
                target_index = [option['variation_name'] - 1 for option in answer if option['polyomino_name'] == polyomino_name][0]
                block_list[polyomino_name] = set(
                    [option['variation_name'] - 1 for options in config['answers'] 
                     for option in options if option['polyomino_name'] == polyomino_name and option['variation_name'] - 1 != target_index]
                )
            # Generate variation options and append to subsets
            subsets.append(select_variation_options(config, problem, answer, block_list))
        problem['answers'] = config['answers']

    img_path = os.path.join(os.path.dirname(config_path), 'image', 'target-rectangle.png')
    emoji_to_image([list(line) for line in problem['target_rectangle'].split('\n')[1:-1]], img_path)
    problem['encoded_rectangle'] = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
    chosed = random.choice(subsets)
    prompt_lines = []
    problem['all_correct'] = {}
    options, option_answer = {}, {}

    # Process each polyomino in the chosen subset
    for polyomino_info in chosed:
        polyomino_name = polyomino_info['polyomino_name']

        # Add prompt lines for each polyomino's variations
        prompt_lines.append({"text": f'Variations for {polyomino_name}:'})
        for variation in polyomino_info['variations']:
            variation_name = variation["variation_name"]
            img_path = os.path.join(os.path.dirname(config_path), 'image', f'{polyomino_name}-Variation {variation_name}.png')
            emoji_to_image([list(line) for line in variation['grid'].split('\n')[1:-1]], img_path)

            # Add prompt lines for the variation
            prompt_lines.append({'text': f'Variation {variation_name} fitting into its bounding box:'})
            prompt_lines.append({
                "text": variation['grid'],
                "encoded_image": base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
            })

        # Separator for the next polyomino
        prompt_lines.append({'text':'-------------------------'})

        # Store options for each polyomino
        problem['all_correct'][polyomino_name] = polyomino_info['all_correct']
        variations = sorted([variation["variation_name"] for variation in polyomino_info['variations']])
        options[polyomino_name] = [f'A. {variations[0]}', f'B. {variations[1]}', 'C. Neither']
        option_answer[polyomino_name] = 'A' if polyomino_info['answer'] == variations[0] else 'B'
        
    return problem, prompt_lines, options, option_answer


def get_bounding_box_size(grid_str:str)->str:
    rows = grid_str.split('\n')[1:-1]
    return f'{len(rows)}x{len(rows[0])}'


def select_variation_options(config:json, problem:json, answer: list[dict], block_list):
    """
    Selects variation options for polyomino problems based on given answers and a block list.

    Args:
        config (json): Configuration settings (not used in the current function).
        problem (json): Contains polyomino variations information.
        answer (list[dict]): List of answers with polyomino names and their selected variations.
        block_list (dict): List of blocked variations for each polyomino.

    Returns:
        subset (list[dict]): List of polyomino names with their selected variations, indicating if all variations are correct or not.
    """
    polyomino_variations, total_box = {}, {}

    # Populate the polyomino_variations and total_box dictionaries
    for polyomino_variation in problem['polyomino_variations']:
        polyomino_name, variations = polyomino_variation['polyomino_name'], polyomino_variation['variations']
        polyomino_variations[polyomino_name] = variations
        total_box[polyomino_name] = [get_bounding_box_size(variation) for variation in variations]

    subset = []
    # Process each answer to find suitable variation options
    for polyomino_answer in answer:
        polyomino_name, variation_idx = polyomino_answer['polyomino_name'], polyomino_answer['variation_name'] - 1

        # Get the bounding box size of the current variation
        cur_box = get_bounding_box_size(polyomino_variations[polyomino_name][variation_idx])

        # Find candidate variations with the same bounding box size, excluding blocked ones
        cands = [idx for idx, x in enumerate(total_box[polyomino_name]) if x == cur_box and idx != variation_idx and idx not in block_list[polyomino_name]]

        # Find variations with different bounding box sizes, excluding blocked ones
        diff_group = [idx for idx, x in enumerate(total_box[polyomino_name]) if x != cur_box and idx != variation_idx and idx not in block_list[polyomino_name]]

        # Check if all answers are correct
        all_correct = False
        if len(cands) == 0 and len(diff_group) == 0:
            all_correct = True
        
        # Select variations based on the availability of non-answer candidates
        if not all_correct:
            chosed = sorted([variation_idx] + ([random.choice(cands)] if len(cands) else [random.choice(diff_group)]))
        else:
            chosed = [idx for idx, _ in enumerate(total_box[polyomino_name])]
        
        # Append the results to the subset list
        subset.append({
            'polyomino_name': polyomino_name, 
            'variations': [{'grid': polyomino_variations[polyomino_name][idx], 'variation_name': idx + 1} for idx in chosed], 
            'all_correct': all_correct, 
            'answer': polyomino_answer['variation_name']
        })
    return subset

if __name__ == '__main__':
    data_root = opt.data_folder
    output_root = opt.output_folder
    prompt_folder = opt.prompt_folder
    setting_templates = [(os.path.splitext(x)[0], os.path.join(prompt_folder, x)) for x in os.listdir(prompt_folder) if x.find('-') != -1]
    failed_cases = []
    for case_id in os.listdir(data_root):
        if not case_id.isdigit():
            continue
        try:
            print(f'processing {case_id}')
            data_foler = os.path.join(data_root, case_id)
            config_path = os.path.join(data_foler, 'config.json')
            problem_path = os.path.join(data_foler, 'problem.txt')
            output_folder = os.path.join(output_root, case_id)
            os.makedirs(output_folder, exist_ok=True)
            problem, prompt_lines, options, option_answer = gen_subset_variation(config_path, problem_path.replace('.txt', '.json'))
            problem['variation_prompt_text'] = '\n'.join([line['text'] for line in prompt_lines])
            problem['variation_prompt_multimodal'] = ','.join([json.dumps({ "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64," + line['encoded_image']}} if 'encoded_image' in line else {'type':'text', 'text': line['text']}) for line in prompt_lines])
            for polyomino_name in [polyomino['polyomino_name'] for polyomino in problem['provided_polyomino_list']]:
                if problem['all_correct'][polyomino_name]:
                    print(f'{polyomino_name} all correct, skipped')
                    continue
                problem['chosed_polyomino'] = polyomino_name
                substitute_dict = get_substitute_dict(problem, options)
                question_folder = os.path.join(output_folder, 'puzzles', polyomino_name)
                os.makedirs(question_folder, exist_ok=True)
                for setting, template in setting_templates:
                    prompt_path = os.path.join(question_folder, f'{setting}.txt')
                    if os.path.exists(prompt_path):
                        continue
                    fill_prompt(template, substitute_dict, prompt_path)
                answer_path = os.path.join(question_folder, 'answer.txt')
                with open(answer_path, 'w') as f:
                    f.writelines([option_answer[polyomino_name]])
        except Exception as e:
            print(str(e))
            failed_cases.append(case_id)
    logging_path = os.path.join(output_root, 'error.log')
    with open(logging_path, 'w') as f:
        f.write('\n'.join(failed_cases))