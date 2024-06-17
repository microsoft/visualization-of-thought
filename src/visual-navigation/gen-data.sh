# Get the directory of the script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo $SCRIPT_DIR
cd $SCRIPT_DIR
python gen_all_paths.py --turn 2 --dest-folder configurations/2
python gen_all_paths.py --turn 3 --dest-folder configurations/3
#python gen_all_paths.py --turn 4 --dest-folder configurations/4
#python gen_all_paths.py --turn 5 --dest-folder configurations/5
#python gen_all_paths.py --turn 6 --dest-folder configurations/6
#python gen_all_paths.py --turn 7 --dest-folder configurations/7
#route planning
cd route-planning
python gen_puzzle.py --config-folder ../configurations/2 --puzzle-folder puzzles/2 --output-jsonl route-planning.jsonl
python gen_puzzle.py --config-folder ../configurations/3 --puzzle-folder puzzles/3 --output-jsonl route-planning.jsonl
#python gen_puzzle.py --config-folder ../configurations/4 --puzzle-folder puzzles/4 --output-jsonl route-planning.jsonl
#python gen_puzzle.py --config-folder ../configurations/5 --puzzle-folder puzzles/5 --output-jsonl route-planning.jsonl
#python gen_puzzle.py --config-folder ../configurations/6 --puzzle-folder puzzles/6 --output-jsonl route-planning.jsonl
#python gen_puzzle.py --config-folder ../configurations/7 --puzzle-folder puzzles/7 --output-jsonl route-planning.jsonl
##next step prediction
cd ../next-step-prediction
python gen_puzzle.py --config-folder ../configurations/2 --puzzle-folder puzzles/2  --output-jsonl next-step-prediction.jsonl
python gen_puzzle.py --config-folder ../configurations/3 --puzzle-folder puzzles/3  --output-jsonl next-step-prediction.jsonl
#python gen_puzzle.py --config-folder ../configurations/4 --puzzle-folder puzzles/4  --output-jsonl next-step-prediction.jsonl
#python gen_puzzle.py --config-folder ../configurations/5 --puzzle-folder puzzles/5  --output-jsonl next-step-prediction.jsonl
#python gen_puzzle.py --config-folder ../configurations/6 --puzzle-folder puzzles/6  --output-jsonl next-step-prediction.jsonl
#python gen_puzzle.py --config-folder ../configurations/7 --puzzle-folder puzzles/7  --output-jsonl next-step-prediction.jsonl
