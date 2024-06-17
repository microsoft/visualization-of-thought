# Get the directory of the script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo $SCRIPT_DIR
cd "$SCRIPT_DIR/gen-solution"
#npm install
#jq '. + {"type": "module"}' node_modules/boolean-sat/package.json > tmp.$$.json && mv tmp.$$.json node_modules/boolean-sat/package.json
#node run.js --width=4 --height=5 --masked=2 --dest='../configurations/level-2' --pieces='TTLII'
#node run.js --width=4 --height=5 --masked=3 --dest='../data/level-3' --pieces='TTLII'
cd ..
python gen_puzzle.py --config-folder configurations/level-2 --puzzle-folder data/level-2 --output-jsonl visual-tiling.jsonl
python gen_puzzle.py --config-folder configurations/level-3 --puzzle-folder data/level-3 --output-jsonl visual-tiling.jsonl