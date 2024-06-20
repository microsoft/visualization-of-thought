#!/bin/bash

# Check if the output folder argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <output-folder>"
  exit 1
fi

# Get the absolute path of the output folder
OUTPUT_FOLDER=$(realpath "$1")

# Get the directory of the script and convert to absolute path
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo "Script directory: $SCRIPT_DIR"
echo "Output directory: $OUTPUT_FOLDER"

# Create necessary directories in the output folder
mkdir -p "$OUTPUT_FOLDER/configurations"
mkdir -p "$OUTPUT_FOLDER/route-planning"
mkdir -p "$OUTPUT_FOLDER/next-step-prediction"

cd "$SCRIPT_DIR"
python gen_all_paths.py --turn 2 --dest-folder "$OUTPUT_FOLDER/configurations/level-2"
python gen_all_paths.py --turn 3 --dest-folder "$OUTPUT_FOLDER/configurations/level-3"
python gen_all_paths.py --turn 4 --dest-folder "$OUTPUT_FOLDER/configurations/level-4"
python gen_all_paths.py --turn 5 --dest-folder "$OUTPUT_FOLDER/configurations/level-5"
python gen_all_paths.py --turn 6 --dest-folder "$OUTPUT_FOLDER/configurations/level-6"
python gen_all_paths.py --turn 7 --dest-folder "$OUTPUT_FOLDER/configurations/level-7"

find "$OUTPUT_FOLDER" -name "*.jsonl" | xargs rm -rf
# Route planning
cd route-planning
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-2" --puzzle-folder "$OUTPUT_FOLDER/route-planning/level-2" --output-jsonl "$OUTPUT_FOLDER/route-planning.jsonl" --difficulty 2
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-3" --puzzle-folder "$OUTPUT_FOLDER/route-planning/level-3" --output-jsonl "$OUTPUT_FOLDER/route-planning.jsonl" --difficulty 3
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-4" --puzzle-folder "$OUTPUT_FOLDER/route-planning/level-4" --output-jsonl "$OUTPUT_FOLDER/route-planning.jsonl" --difficulty 4
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-5" --puzzle-folder "$OUTPUT_FOLDER/route-planning/level-5" --output-jsonl "$OUTPUT_FOLDER/route-planning.jsonl" --difficulty 5
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-6" --puzzle-folder "$OUTPUT_FOLDER/route-planning/level-6" --output-jsonl "$OUTPUT_FOLDER/route-planning.jsonl" --difficulty 6
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-7" --puzzle-folder "$OUTPUT_FOLDER/route-planning/level-7" --output-jsonl "$OUTPUT_FOLDER/route-planning.jsonl" --difficulty 7

# Next step prediction
cd "$SCRIPT_DIR/next-step-prediction"
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-2" --puzzle-folder "$OUTPUT_FOLDER/next-step-prediction/level-2" --output-jsonl "$OUTPUT_FOLDER/next-step-prediction.jsonl" --difficulty 2
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-3" --puzzle-folder "$OUTPUT_FOLDER/next-step-prediction/level-3" --output-jsonl "$OUTPUT_FOLDER/next-step-prediction.jsonl" --difficulty 3
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-4" --puzzle-folder "$OUTPUT_FOLDER/next-step-prediction/level-4" --output-jsonl "$OUTPUT_FOLDER/next-step-prediction.jsonl" --difficulty 4
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-5" --puzzle-folder "$OUTPUT_FOLDER/next-step-prediction/level-5" --output-jsonl "$OUTPUT_FOLDER/next-step-prediction.jsonl" --difficulty 5
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-6" --puzzle-folder "$OUTPUT_FOLDER/next-step-prediction/level-6" --output-jsonl "$OUTPUT_FOLDER/next-step-prediction.jsonl" --difficulty 6
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-7" --puzzle-folder "$OUTPUT_FOLDER/next-step-prediction/level-7" --output-jsonl "$OUTPUT_FOLDER/next-step-prediction.jsonl" --difficulty 7
