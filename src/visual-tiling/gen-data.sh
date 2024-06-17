cd gen-solution
npm install
jq '. + {"type": "module"}' node_modules/boolean-sat/package.json > tmp.$$.json && mv tmp.$$.json node_modules/boolean-sat/package.json
node run.js --width=4 --height=5 --masked=2 --dest='../data/level-2' --pieces='TTLII'
cd ..
python gen_puzzle.py --data-folder data/level-2 --output-folder data/level-2
