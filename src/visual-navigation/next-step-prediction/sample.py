import json
import os
from util import evaluate_single_instance
import re

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

def main(jsonl_file_path, output_dir, setting, target_difficulty, regex_path: str):
    """
    Evaluate instances from a JSONL file.

    Args:
        jsonl_file_path (str): Path to the JSONL file containing the instances.
        output_dir (str): Directory where the output files will be written.
        setting (str): Experiment settings, used to locate prompt files.
        target_difficulty (int): Difficulty level to run instances. If 0, run all instances regardless of difficulty.
        regex_path (str): Path to the file containing regex patterns used for parsing responses and evaluation.
    """
    instances = load_jsonl(jsonl_file_path)
    results, failed_list = [], []
    total_verbal_correct = 0
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

        output_file_path = output_file_path.replace('/QA', '')

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

        # Track correctness
        total_verbal_correct += result['verbal']['correct']
        if result['parse_fail']:
            failed_list.append(output_file_path)

        """ # Print result for the instance
        print(f"Instance ID: {result['instance_id']}")
        print(f"  Verbal Answer: {result['verbal']['answer']} (Correct: {result['verbal']['correct']})")
        
        if len(results) % 10 == 0:
            completed_cnt = len(results)
            print('****************************Performance Snapshot****************************')
            print(f"            Total Instances: {completed_cnt}")
            print(f"            Verbal Correct: {total_verbal_correct} (Accuracy: {total_verbal_correct / completed_cnt * 100:.2f}%)")
            print('****************************************************************************') """

    total_instances = len(results)
    # Calculate accuracy
    verbal_accuracy = total_verbal_correct / total_instances

    # Print summary
    print("Summary:")
    print(f"  Total Instances: {total_instances}, Failed Instances: {len(failed_list)}")
    print(f"  Verbal Correct: {total_verbal_correct} (Accuracy: {verbal_accuracy * 100:.2f}%)")
    return results, failed_list

def write_logging(failed_list: list[str], logging_path: str):
    with open(logging_path, 'w') as f:
        f.writelines('\n'.join(failed_list))
    if failed_list:
        print(f'See failed instance in:')
        print(f'    {logging_path}')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate instances from a JSONL file")
    parser.add_argument("--jsonl-path", type=str, help="Path to the JSONL file containing the instances")
    parser.add_argument("--output-folder", type=str, help="output files will be written to: output-folder/setting/difficulty")
    parser.add_argument("--setting", type=str, help="experiment settings")
    parser.add_argument("--target-difficulty", type=int, help="run instances with specific difficulty, otherwise run all instances", default=0)
    parser.add_argument('--multimodal', action='store_true', help="Enable the flag")
    parser.add_argument("--regex-path", type=str, default='', help="Path to the file containing regex patterns to parse answers from LLM responses, default patterns are GPT-centric.")

    args = parser.parse_args()
    output_folder = os.path.join(args.output_folder, args.setting)
    os.makedirs(output_folder, exist_ok=True)
    results, failed_list = main(args.jsonl_path, output_folder, args.setting, args.target_difficulty, args.regex_path)
    logging_path = os.path.join(output_folder, 'error.log')
    write_logging(failed_list, logging_path)