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
cd route-plan
python gen_puzzle.py --data-folder ../configurations/2 --output-folder puzzles/2
python gen_puzzle.py --data-folder ../configurations/3 --output-folder puzzles/3
#python gen_puzzle.py --data-folder ../configurations/4 --output-folder puzzles/4
#python gen_puzzle.py --data-folder ../configurations/5 --output-folder puzzles/5
#python gen_puzzle.py --data-folder ../configurations/6 --output-folder puzzles/6
#python gen_puzzle.py --data-folder ../configurations/7 --output-folder puzzles/7
##next step prediction
cd ../next-step-prediction
python gen_puzzle.py --data-folder ../configurations/2 --output-folder puzzles/2
python gen_puzzle.py --data-folder ../configurations/3 --output-folder puzzles/3
#python gen_puzzle.py --data-folder ../configurations/4 --output-folder puzzles/4
#python gen_puzzle.py --data-folder ../configurations/5 --output-folder puzzles/5
#python gen_puzzle.py --data-folder ../configurations/6 --output-folder puzzles/6
#python gen_puzzle.py --data-folder ../configurations/7 --output-folder puzzles/7
