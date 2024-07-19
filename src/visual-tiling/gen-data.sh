#!/bin/bash

# Check if the output folder argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <output-folder>"
  exit 1
fi

# Get the absolute path of the output folder
OUTPUT_FOLDER=$(realpath "$1")

# Get the directory of the script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo "Script directory: $SCRIPT_DIR"
echo "Output directory: $OUTPUT_FOLDER"

# Create output folder if it doesn't exist
mkdir -p "$OUTPUT_FOLDER"

cd "$SCRIPT_DIR/gen-solution"
#npm install
jq '. + {"type": "module"}' node_modules/boolean-sat/package.json > tmp.$$.json && mv tmp.$$.json node_modules/boolean-sat/package.json

# Run node scripts with specified output folders
node run.js --width=4 --height=5 --masked=2 --dest="$OUTPUT_FOLDER/configurations/level-2" --pieces='TTLII'
node run.js --width=4 --height=5 --masked=3 --dest="$OUTPUT_FOLDER/configurations/level-3" --pieces='TTLII'

cd ..
# Run python scripts with specified output folders
find "$OUTPUT_FOLDER" -name "*.jsonl" | xargs rm
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-2" --puzzle-folder "$OUTPUT_FOLDER/puzzles/level-2" --output-jsonl "$OUTPUT_FOLDER/visual-tiling.jsonl" --difficulty 2
python gen_puzzle.py --config-folder "$OUTPUT_FOLDER/configurations/level-3" --puzzle-folder "$OUTPUT_FOLDER/puzzles/level-3" --output-jsonl "$OUTPUT_FOLDER/visual-tiling.jsonl" --difficulty 3

