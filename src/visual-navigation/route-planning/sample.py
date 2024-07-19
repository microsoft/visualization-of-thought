import json
import os
from util import evaluate_single_instance
import subprocess

def load_jsonl(file_path):
    instances = []
    with open(file_path, 'r') as f:
        for line in f:
            instances.append(json.loads(line.strip()))
    return instances

def run_llm_client(instance_info: json, prompt_path: str, output_path: str):
    #for standard prompting
    task_query = instance_info['desc']
    task_query_multimodal = instance_info['desc_multimodal']
    pass

def main(jsonl_file_path: str, output_dir: str, setting: str, target_difficulty: int, cost_threshold: int, regex_path: str):
    """
    Evaluate instances from a JSONL file.

    Args:
        jsonl_file_path (str): Path to the JSONL file containing the instances.
        output_dir (str): Directory where the output files will be written.
        setting (str): Experiment settings, used to locate prompt files.
        target_difficulty (int): Difficulty level to run instances. If 0, run all instances regardless of difficulty.
        cost_threshold (int): Total cost threshold. Instances with costs greater than this threshold will be discarded.
        regex_path (str): Path to the file containing regex patterns used for parsing responses and evaluation.
    """

    instances = load_jsonl(jsonl_file_path)
    results, failed_list = [], []
    total_succ_cnt = 0
    completing_rate_list = []
    total_instances = len(instances)
    jsonl_dir = os.path.dirname(jsonl_file_path)  # Get the directory of the jsonl file

    if len(regex_path) and not os.path.exists(regex_path):
        print('specified regex file does not exist')
        exit(-1)
    # Load and compile regex patterns from the file
    regex_patterns = []
    if len(regex_path):
        with open(regex_path, 'r', encoding='utf-8') as f:
            regex_patterns = [f'{line.strip()}' for line in f if len(line)]

    for instance in instances:
        puzzle_folder = instance['puzzle_path'] #relative path to jsonl file
        instance_id = instance['instance_id']
        difficulty = instance['difficulty']
        if target_difficulty != 0 and difficulty != target_difficulty:
            continue
        output_file_path = os.path.join(output_dir, f'level-{difficulty}', instance_id, "output.txt")

        if not os.path.exists(output_file_path):
            prompt_path = os.path.join(jsonl_dir, puzzle_folder, f'{setting}.txt')
            run_llm_client(instance, prompt_path, output_file_path)
        # Check if output file exists
        if not os.path.exists(output_file_path):
            print(f"Output file not found for instance {instance_id}: {output_file_path}")
            failed_list.append(output_file_path)
            continue

        # Read the output file
        with open(output_file_path, 'r', encoding='utf-8') as f:
            output = f.read()

        # Evaluate the instance
        result = evaluate_single_instance(output, instance, regex_patterns)
        result['instance_id'] = instance_id
        results.append(result)

        # Track metrics
        excessive_guess = result['verbal']['total_cost'] >= cost_threshold
        completing_rate = 0 if excessive_guess else result['verbal']['completing_rate']
        completing_rate_list.append(completing_rate)
        total_succ_cnt += 0 if excessive_guess else result['verbal']['succ']

        if result['parse_fail']:
            failed_list.append(output_file_path)

        """ # Print result for the instance
        print(f"Level-{difficulty}, Instance ID: {result['instance_id']}")
        print(f"  Valid Steps: {result['verbal']['valid_step']}, Remaining Steps: {result['verbal']['remaining_step']})")
        
        if len(results) % 10 == 0:
            completed_cnt = len(results)
            print('****************************Performance Snapshot****************************')
            print(f"            Total Instances: {completed_cnt}")
            print(f"            Average Completing Rate: {sum(completing_rate_list) / len(results)}")
            print(f"            Succ Rate: {total_succ_cnt / len(results)}")
            print('****************************************************************************') """

    total_instances = len(results)
    # Print summary
    print("Summary:")
    print(f"  Total Instances: {total_instances}, Failed Instances: {len(failed_list)}")
    print(f"  Average Completing Rate: {sum(completing_rate_list) / len(results)}")
    print(f"  Succ Rate: {total_succ_cnt / len(results)}")
    return results, failed_list

def write_logging(failed_list: list[str], logging_path: str):
    with open(logging_path, 'w') as f:
        f.writelines('\n'.join(failed_list))
    if not failed_list:
        return
    unmatch_pattern_path = os.path.join(output_folder, 'unmatched_directional_patterns.log')
    unmatched_cnt = 0

    # Get the number of files without directional strings
    for instance in [x for x in failed_list if os.path.exists(x)]:
        unmatched_files_command = f'grep -i -E "(up|left|right|down|north|west|east|south)" -L {instance} | wc -l'
        result = subprocess.run(unmatched_files_command, shell=True, capture_output=True, text=True)
        unmatched_cnt += int(result.stdout.strip()) if result.returncode == 0 else 0
    notice = f"No directional strings found in {unmatched_cnt}/{len(failed_list)} files."
    shell_command = f"cat {logging_path} | xargs grep -i -E '(up|left|right|down|north|west|east|south)' -h | sort | uniq > {unmatch_pattern_path}"
    subprocess.run(shell_command, shell=True)
    print(f'\n************Warnings************')
    if unmatched_cnt:
        print(notice)
    print(f'See failed instance in:')
    print(f'    {logging_path}')
    if os.path.getsize(unmatch_pattern_path):
        print(f'See uncaptured directional patterns in:')
        print(f'    {unmatch_pattern_path}')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate instances from a JSONL file")
    parser.add_argument("--jsonl-path", type=str, help="Path to the JSONL file containing the instances")
    parser.add_argument("--output-folder", type=str, help="output files will be written to: output-folder/setting/difficulty")
    parser.add_argument("--setting", type=str, help="experiment settings")
    parser.add_argument("--target-difficulty", type=int, help="run instances with specific difficulty, otherwise run all instances", default=0)
    parser.add_argument('--multimodal', action='store_true', help="Enable the flag")
    parser.add_argument('--cost-threshold', type=int, default=100, help="total cost greater than this threshold will be discarded")
    parser.add_argument("--regex-path", type=str, default = '', help="Path to the file containing regex patterns to parse answers from LLM responses, default patterns are GPT-centric.")


    args = parser.parse_args()
    output_folder = os.path.join(args.output_folder, args.setting)
    os.makedirs(output_folder, exist_ok=True)
    results, failed_list = main(args.jsonl_path, output_folder, args.setting, args.target_difficulty, args.cost_threshold, args.regex_path)
    logging_path = os.path.join(output_folder, 'error.log')
    write_logging(failed_list, logging_path)
        