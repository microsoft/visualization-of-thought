import PolyominoSolver from './Solver.js';
import { Polyomino, tetrominos  } from './Polyomino.js';
import fs from 'fs';
import path from 'path';
import minimist from 'minimist';

const default_emoji_list = ['🟥', '🟩', '🟦', '🟨', '🟪', '🟧'];
export const total_polyominoes = {
    'Tetromino I': new Polyomino([[0, 0], [0, 1], [0, 2], [0, 3]]),
    'Tetromino O': new Polyomino([[0, 0], [0, 1], [1, 1], [1, 0]]),
    'Tetromino T': new Polyomino([[0, 1], [1, 1], [1, 0], [2, 1]]),
    'Tetromino L': new Polyomino([[0, 2], [0, 1], [0, 0], [1, 0]]),
    'Tetromino Z': new Polyomino([[0, 0], [1, 0], [1, 1], [2, 1]]),
};
const total_polyomino_variations = Object.fromEntries(
    Object.entries(total_polyominoes).map(([name, polyomino]) => [name, generateVariations(polyomino)])
);

function textual_representation(polyominos) {
    // Define a set of emoji for different polyominos
    const emoji_list = ['🟥', '🟩', '🟦', '🟨', '🟪', '🟧'];

    // Determine the size of the grid
    const max_x = Math.max(...polyominos.flatMap(p => p.coords.map(coord => coord[0])));
    const max_y = Math.max(...polyominos.flatMap(p => p.coords.map(coord => coord[1])));

    // Initialize the grid with blank spaces
    const grid = Array.from({ length: max_y + 1 }, () => Array(max_x + 1).fill('⬜'));

    // Fill the grid with emojis for each polyomino
    polyominos.forEach((polyomino, index) => {
        const emoji = emoji_list[index % emoji_list.length];
        polyomino.coords.forEach(([x, y]) => {
            grid[y][x] = emoji;
        });
    });

    // Convert the grid to a string representation
    return '```\n' + grid.map(row => row.join('')).join('\n') + '\n```';
}

function textual_representation_mask(polyominos, mask = [], emoji_list = default_emoji_list) {
    const mask_emoji = '⬜';

    const max_x = Math.max(...polyominos.flatMap(p => p.coords.map(coord => coord[0])));
    const max_y = Math.max(...polyominos.flatMap(p => p.coords.map(coord => coord[1])));

    const grid = Array.from({ length: max_y + 1 }, () => Array(max_x + 1).fill(mask_emoji));
    let cur_emoji_idx = 0
    polyominos.forEach((polyomino, index) => {
        const emoji = mask.includes(index) ? mask_emoji : emoji_list[cur_emoji_idx++ % emoji_list.length];
        polyomino.coords.forEach(([x, y]) => {
            grid[y][x] = emoji;
        });
    });

    // Convert the grid to a string representation
    return '```\n' + grid.map(row => row.join('')).join('\n') + '\n```';
}

function generateVariations(polyomino) {
    let variations = [];

    for (let i = 0; i < 4; i++) {
        let rotated = polyomino.rotate(i).normalize();
        let reflected = rotated.reflect().normalize();

        // Add the variation if it's unique
        if (!variations.some(variation => variation.equals(rotated))) {
            variations.push(rotated);
        }
        if (!variations.some(variation => variation.equals(reflected))) {
            variations.push(reflected);
        }
    }

    return variations;
}

function findVariationName(polyominoVariation){
    let res = {};
    for (const [polyomino_name, variations] of Object.entries(total_polyomino_variations)) {
        variations.forEach((variation, variation_index) => {
            if (variation.equals(polyominoVariation.normalize())) {
                res = {polyomino_name, variation_name: variation_index + 1};
            }
        }
        );
    }
    return res;
}

function countEmptySquare(rectangle, selectedIndices){
    let emptySquares = 0
    selectedIndices.forEach(index =>{
        const polyomino = rectangle[index];
        emptySquares += polyomino.coords.length;
    })
    return emptySquares;
}

// Call the function with your tetrominos
// printVariations({'I': tetrominos['I'], 'L': tetrominos['L'], 'O': tetrominos['O'], 'T': tetrominos['T'], 'S': tetrominos['S']});

function printVariationsAndMaskedRectangle(rectangle, selectedIndices) {
    let printContent = []
    let problem = {'polyomino_variations':[], 'target_rectangle':'', 'provided_polyomino_list':[], 'empty_squares':0}
    let empty_squares = countEmptySquare(rectangle, selectedIndices)
    printContent.push(`Target rectangle with ${empty_squares} empty squares:`);
    problem.empty_squares = empty_squares
    let emoji_for_existing_polyominoes = default_emoji_list.filter((_, index) => !selectedIndices.includes(index))
    let mask_region = textual_representation_mask(rectangle, selectedIndices, emoji_for_existing_polyominoes)
    printContent.push(mask_region);
    problem.target_rectangle = mask_region

    printContent.push("Provided polyominoes:");
    let maskedCoords = []
    let allTetrominoNames = rectangle.map(polyomino => findVariationName(polyomino).polyomino_name)
    selectedIndices.forEach((index, listno) => {
        const polyomino = rectangle[index];
        polyomino.coords.forEach(coord =>{
            maskedCoords.push(coord)
        });
        printContent.push(`${listno + 1}. ${allTetrominoNames[index]} (${default_emoji_list[index]})`);
        problem.provided_polyomino_list.push({'polyomino_name':allTetrominoNames[index], 'emoji':default_emoji_list[index]})
    }
    );
    printContent.push("-------------------------");
    selectedIndices.forEach(index => {
        const polyomino = rectangle[index];
        let polyomino_name = allTetrominoNames[index]
        printContent.push(`All variations for ${polyomino_name}:`);
        let cur_polyomino_variations = []
        const variations = total_polyomino_variations[polyomino_name];
        variations.forEach((variation, varIndex) => {
            printContent.push(`Variation ${varIndex + 1} fitting into its bounding box:`);
            let grid = textual_representation_mask([variation], [], [default_emoji_list[index]])
            printContent.push(grid);
            cur_polyomino_variations.push(grid)
        });
        problem.polyomino_variations.push({polyomino_name, 'variations': cur_polyomino_variations})
        printContent.push("-------------------------");
    });
    return {'maskRegion': new Polyomino(maskedCoords), 'providedTetrominoNames': selectedIndices.map(index => allTetrominoNames[index]), 'printContent':printContent, 'problem_json': problem}
}

function generateCombinations(arr, len) {
    if (len === 1) return arr.map(el => [el]);

    let combinations = [];

    arr.forEach((current, index) => {
        const remaining = arr.slice(index + 1);
        const remainingCombinations = generateCombinations(remaining, len - 1);
        const combined = remainingCombinations.map(combination => [current, ...combination]);
        combinations = combinations.concat(combined);
    });

    return combinations;
}

function isIdentical(config1, config2){
    if (config1.length !== config2.length) {
        return false; // Different number of polyominos
    }

    for (let i = 0; i < config1.length; i++) {
        const polyomino1 = config1[i];
        const polyomino2 = config2[i];

        if (!polyomino1.equals(polyomino2)){
            return false;
        }
    }
    return true; // All polyominos and their coordinates match
}

function InitializeRegion(width, height){
    // Define a 3x4 rectangle as the region
    const regionCoords = [];
    for (let x = 0; x < width; x++) {
        for (let y = 0; y < height; y++) {
            regionCoords.push([x, y]);
        }
    }
    return new Polyomino(regionCoords);
}

function getAllUniqSolutions(region, pieces){
    const solver = new PolyominoSolver();

    // Define the problem
    const problem = {
        pieces: pieces,
        region: region.coords,
        allowRotation: true,
        allowReflection: true
    };
    let uniqSolutions = []
    for (let i = 0; i < 100; ++i){
        const satSolution = solver.solveSAT(problem).solutions;
        if (satSolution.length == 0){
            continue
        }
        if (uniqSolutions.some(existSolution => isIdentical(existSolution, satSolution[0]))){
            continue
        }
        uniqSolutions.push(satSolution[0])
    }
    const dlxSolution = solver.solveDLX(problem).solutions;
    if (dlxSolution.length && !uniqSolutions.some(existSolution => isIdentical(existSolution, dlxSolution[0]))){
        uniqSolutions.push(dlxSolution[0])
    }
    console.log(`total unique solution: ${uniqSolutions.length}`)

    return uniqSolutions
}

function genPromptAnswer(solution, selectedIndices){
    let maskInfo = printVariationsAndMaskedRectangle(solution, selectedIndices);
    const subSolutions = getAllUniqSolutions(maskInfo.maskRegion, maskInfo.providedTetrominoNames.map(name => total_polyominoes[name].coords));
    let subcontent = []
    let answers = []
    subSolutions.forEach(subSolution => {
        subcontent.push(textual_representation(subSolution));
        subcontent.push('')
        answers.push(subSolution.map(polyomino => findVariationName(polyomino)))
    });
    return {prompt: maskInfo.printContent, subcontent, answers, problem_json: maskInfo.problem_json}
}

function saveConfig(case_idx, configuration, dest_path){
    // Specify the directory and file path
    const directoryPath = path.join(dest_path, `${case_idx}`)
    const filePath = path.join(directoryPath, 'config.json');

    // Check if the directory exists, if not, create it
    if (!fs.existsSync(directoryPath)) {
        fs.mkdirSync(directoryPath, { recursive: true });
    }

    // Convert the object to a JSON string
    const jsonContent = JSON.stringify(configuration, null, 2);

    // Write the JSON string to a file
    fs.writeFile(filePath, jsonContent, 'utf8', (err) => {
        if (err) {
            console.log("An error occurred while writing JSON to file.");
            return console.log(err);
        }
    });

}

function saveProblem(case_idx, prompt, dest_path){
    const directoryPath = path.join(dest_path, `${case_idx}`)
    const filePath = path.join(directoryPath, 'problem.txt');
    fs.writeFile(filePath, prompt.join('\n'), 'utf8', (err) => {
        if (err) {
            console.log("An error occurred while writing text to file.");
            return console.log(err);
        }
    });
}

function saveVisualConfig(case_idx, configuration, dest_path){
    // Specify the directory and file path
    const directoryPath = path.join(dest_path, `${case_idx}`)
    const filePath = path.join(directoryPath, 'problem.json');

    // Check if the directory exists, if not, create it
    if (!fs.existsSync(directoryPath)) {
        fs.mkdirSync(directoryPath, { recursive: true });
    }

    // Convert the object to a JSON string
    const jsonContent = JSON.stringify(configuration, null, 2);

    // Write the JSON string to a file
    fs.writeFile(filePath, jsonContent, 'utf8', (err) => {
        if (err) {
            console.log("An error occurred while writing JSON to file.");
            return console.log(err);
        }
    });

}

function genByConfiguration(width, height, pieces, providedCount = 2, dest_path){
    let region = InitializeRegion(width, height)
    let uniqSolutions = getAllUniqSolutions(region, pieces)
    let case_idx = 1
    uniqSolutions.forEach(solution => {
        let all_combinations = generateCombinations(solution.map((_, index) => index), providedCount)
        let region_polyomino_names = solution.map(polyomino => findVariationName(polyomino, total_polyominoes).polyomino_name)
        all_combinations.forEach(selectedIndices => {
            let providedTetrominoNames = selectedIndices.map(index => 
                region_polyomino_names[index]);
            let meta_data = {'region': solution.map(polyomino => polyomino.coords), 'region_polyominoes':region_polyomino_names, 'mask_indices':selectedIndices, 'provided_polyominoes':providedTetrominoNames}
            if (new Set(providedTetrominoNames).size == providedCount){
                let res = genPromptAnswer(solution, selectedIndices);
                meta_data['answers'] = res.answers
                saveConfig(case_idx, meta_data, dest_path);
                saveProblem(case_idx, res.prompt, dest_path)
                saveVisualConfig(case_idx, res.problem_json, dest_path)
                ++case_idx;
            }
        }
        );
    }
    )
}

// Parse command-line arguments
const args = minimist(process.argv.slice(2));

// Extract arguments with default values
const width = args.width || 4;
const height = args.height || 5;
const numMaskedPieces = args.masked || 2;
const destFolder = args.dest || '../data/level-2';
const pieceTypesString = args.pieces || 'TTLII';

// Convert the string into an array of characters
const pieceTypes = pieceTypesString.split('');

// Define pieces array based on provided piece types
const pieces = pieceTypes.map(type => tetrominos[type].coords);

// Call your functions with the parsed arguments
genByConfiguration(width, height, pieces, numMaskedPieces, destFolder);
