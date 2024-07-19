#!/bin/bash

# Check if the output folder argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <output-folder>"
  exit 1
fi

# Get the absolute path of the output folder
DATASET_FOLDER=$(realpath "$1")
VISUAL_NAVIGATION_FOLDER="$DATASET_FOLDER/visual-navigation"
VISUAL_TILING_FOLDER="$DATASET_FOLDER/visual-tiling"

# Get the directory of the script and convert to absolute path
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo "Script directory: $SCRIPT_DIR"
echo "Dataset directory: $DATASET_FOLDER"

TEMP_PATCH_FOLDER="$DATASET_FOLDER/tmp"
mkdir -p $TEMP_PATCH_FOLDER

# Route planning
cd "$SCRIPT_DIR/visual-navigation/route-planning"

python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-2" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/route-planning/level-2" --output-jsonl "$TEMP_PATCH_FOLDER/route-planning.jsonl" --difficulty 2
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-3" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/route-planning/level-3" --output-jsonl "$TEMP_PATCH_FOLDER/route-planning.jsonl" --difficulty 3
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-4" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/route-planning/level-4" --output-jsonl "$TEMP_PATCH_FOLDER/route-planning.jsonl" --difficulty 4
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-5" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/route-planning/level-5" --output-jsonl "$TEMP_PATCH_FOLDER/route-planning.jsonl" --difficulty 5
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-6" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/route-planning/level-6" --output-jsonl "$TEMP_PATCH_FOLDER/route-planning.jsonl" --difficulty 6
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-7" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/route-planning/level-7" --output-jsonl "$TEMP_PATCH_FOLDER/route-planning.jsonl" --difficulty 7

# Next step prediction
cd "$SCRIPT_DIR/visual-navigation/next-step-prediction"
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-2" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/next-step-prediction/level-2" --output-jsonl "$TEMP_PATCH_FOLDER/next-step-prediction.jsonl" --difficulty 2
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-3" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/next-step-prediction/level-3" --output-jsonl "$TEMP_PATCH_FOLDER/next-step-prediction.jsonl" --difficulty 3
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-4" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/next-step-prediction/level-4" --output-jsonl "$TEMP_PATCH_FOLDER/next-step-prediction.jsonl" --difficulty 4
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-5" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/next-step-prediction/level-5" --output-jsonl "$TEMP_PATCH_FOLDER/next-step-prediction.jsonl" --difficulty 5
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-6" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/next-step-prediction/level-6" --output-jsonl "$TEMP_PATCH_FOLDER/next-step-prediction.jsonl" --difficulty 6
python gen_puzzle.py --config-folder "$VISUAL_NAVIGATION_FOLDER/configurations/level-7" --puzzle-folder "$VISUAL_NAVIGATION_FOLDER/next-step-prediction/level-7" --output-jsonl "$TEMP_PATCH_FOLDER/next-step-prediction.jsonl" --difficulty 7


# Visual tiling
cd "$SCRIPT_DIR/visual-tiling"
python gen_puzzle.py --config-folder "$VISUAL_TILING_FOLDER/configurations/level-2" --puzzle-folder "$VISUAL_TILING_FOLDER/puzzles/level-2" --output-jsonl "$TEMP_PATCH_FOLDER/visual-tiling.jsonl" --difficulty 2
python gen_puzzle.py --config-folder "$VISUAL_TILING_FOLDER/configurations/level-3" --puzzle-folder "$VISUAL_TILING_FOLDER/puzzles/level-3" --output-jsonl "$TEMP_PATCH_FOLDER/visual-tiling.jsonl" --difficulty 3

rm -rf $TEMP_PATCH_FOLDER
