import PolyominoProblem from './PolyominoProblem.js';
import { Polyomino } from './Polyomino.js';
import parseSexp from 's-expression';
import satSolve from 'boolean-sat';
// import solveSat from 'boolean-sat';
import { solve as solveExactCover } from 'dlxlib';


export default class PolyominoSolver {
    constructor() {
        this.z3Ready = false;
        this.z3SolverOutputLines = [];
        this.z3Solver = null;
    }

    loadZ3() {
        // Load and initialize Z3 solver logic here
        this.z3Ready = true;
    }

    createPolyominoProblem(problem) {
        return new PolyominoProblem(
            problem.pieces.map(coords => new Polyomino(coords)),
            new Polyomino(problem.region),
            problem.allowRotation,
            problem.allowReflection
        );
    }
    rotateRectangle180(polyominos) {
        // Find the maximum x and y values to use for translation after rotation
        let maxX = Math.max(...polyominos.flatMap(p => p.coords.map(coord => coord[0])));
        let maxY = Math.max(...polyominos.flatMap(p => p.coords.map(coord => coord[1])));
    
        // Rotate each polyomino
        return polyominos.map(polyomino => (
            new Polyomino(polyomino.coords.map(([x, y]) => [-x + maxX, -y + maxY]).sort(([x1, y1], [x2, y2]) => {
                return (x1 - x2) !== 0 ? (x1 - x2) : (y1 - y2);
            }))
        ));
    }

    solveSAT(problem) {
        let polyProblem = this.createPolyominoProblem(problem);
        let { convertedProblem, interpreter } = polyProblem.convertToSAT();
        let startTime = Date.now();
        let { numVars, clauseList } = convertedProblem;
        let satSolution = satSolve(numVars, clauseList);
        let solutions = satSolution == false ? [] : [interpreter(satSolution)];
        // Assuming 'solutions' is an array of arrays of Polyomino objects
        let rotatedSolutions = solutions.map(this.rotateRectangle180);
        // Combine the original and rotated solutions
        let combinedSolutions = solutions.concat(rotatedSolutions);
        // or using the spread operator
        // let combinedSolutions = [...solutions, ...rotatedSolutions];

        // Assuming 'interpretedSolutions' is an array of arrays of Polyomino objects
        let sortedSolutions = solutions.map(polyominoes => {
            return polyominoes.sort((a, b) => {
                let [ax, ay] = a.coords[0];
                let [bx, by] = b.coords[0];

                if (ax !== bx) {
                    return ax - bx;
                }
                return ay - by;
            });
        });

        return { solutions: sortedSolutions, time: Date.now() - startTime };
    }

    solveZ3(problem) {
        if (!this.z3Ready) throw new Error('Z3 solver is still loading...');

        let polyProblem = this.createPolyominoProblem(problem);
        let startTime = Date.now();
        let { convertedProblem, interpreter } = polyProblem.convertToZ3();

        // Z3 solving logic
        let solutions = [];

        return { solutions, time: Date.now() - startTime };
    }

    solveDLX(problem) {
        let polyProblem = this.createPolyominoProblem(problem);
        let startTime = Date.now();
        let { convertedProblem, interpreter } = polyProblem.convertToDlx();

        let { matrix } = convertedProblem;

        // DLX solving logic
        let solutions = solveExactCover(matrix, null, null, 1);

        // Check if there are any solutions
        if (solutions.length === 0) {
            return { solutions: [], time: Date.now() - startTime };
        } else {
            // Interpret all solutions
            let interpretedSolutions = solutions.map(solution => {
                let rows = solution.map(i => matrix[i]);
                return interpreter(rows);
            });
            // Assuming 'solutions' is an array of arrays of Polyomino objects
            let rotatedSolutions = interpretedSolutions.map(this.rotateRectangle180);
            // Combine the original and rotated solutions
            let combinedSolutions = interpretedSolutions.concat(rotatedSolutions);
            // or using the spread operator
            // let combinedSolutions = [...solutions, ...rotatedSolutions];
            // Assuming 'interpretedSolutions' is an array of arrays of Polyomino objects
            let sortedSolutions = interpretedSolutions.map(polyominoes => {
                return polyominoes.sort((a, b) => {
                    let [ax, ay] = a.coords[0];
                    let [bx, by] = b.coords[0];

                    if (ax !== bx) {
                        return ax - bx;
                    }
                    return ay - by;
                });
            });

        return { solutions: sortedSolutions, time: Date.now() - startTime };

        }

    }
}
