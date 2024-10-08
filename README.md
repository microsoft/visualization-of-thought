# Visualization-of-Thought (VoT)

## Overview

Visualization-of-Thought (VoT) prompting is designed to enhance the spatial reasoning abilities of large language models (LLMs) by visualizing their reasoning traces, thus guiding subsequent reasoning steps. This approach leverages the concept of the "mind's eye" in human cognition, which refers to the ability to visualize and manipulate mental images. By emulating this cognitive process, VoT has been applied to tasks such as natural language navigation, visual navigation, and visual tiling in 2D grid worlds, significantly improving the performance of LLMs in these areas.
![image](https://github.com/user-attachments/assets/cc34d9b5-3f34-4e2b-87fc-6d1d7d81bcb1)

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Python 3.x.
- You have installed nodejs (needed for data augmentation).

### Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/microsoft/Visualization-of-Thought.git
cd Visualization-of-Thought
pip install -r src/requirements.txt
```

### Dataset Prepare

You need to download the dataset and then generate prompts for different settings. The dataset includes tasks designed to evaluate the spatial reasoning capabilities of LLMs:

1. **Natural Language Navigation**:
   - A square map defined by a sequence of random walk instructions and associated objects.
   - Task: Identify the associated object at a specified location determined by navigation instructions.
   - Data generation is implemented by [SpatialEvalLLM](https://github.com/runopti/SpatialEvalLLM) repository. Use the following command to generate the data:
```bash
python square.py --seed 8 --size 4 --steps 8 --maptype square --label_path ./labels/imagenetsimple.json --n_sample 200 --out_dir results_map_global --special_order snake_order
```

2. **Visual Tasks**:
   
Download the dataset of visual tasks via this [link](https://github.com/microsoft/visualization-of-thought/raw/main/vot-dataset-visual-tasks.zip), and place it under the root folder of this repo.

```bash
mkdir -p dataset
unzip VoT-Dataset-Visual-Tasks.zip -d dataset
cd src
# fill in prompt template for different settings
sh patch-prompt.sh ../dataset
```
Please notice that prompts of different settings (CoT/VoT/GPT-4V CoT) for each instance have been removed from this released version. The `patch-prompt.sh` script is provided to automatically fill in prompt templates for all experiment settings across tasks. Prompt templates are stored in the prompts folder under each visual task. For example:
- visual-navigation/route-planning/prompts/{setting}.txt
- visual-navigation/next-step-prediction/prompts/{setting}.txt
- visual-tiling/prompts/{setting}.txt

To create your own prompt template for a new setting, simply add the template file under the `prompts` folder of the relevant task. An example of a template can be found in the [VoT template](https://github.com/microsoft/visualization-of-thought/blob/main/src/visual-tiling/prompts/0-shot-vot). 

### Evaluation
Sample codes are provided for each task to run experiments. You need to implement the `run_llm_client` function for each visual task, which writes response to specified output path. Then run following command for evaluation:
```bash
python visual-navigation/route-planning/sample.py --jsonl-path ../dataset/visual-navigation/route-planning.jsonl --output-folder {output-folder} --setting {setting}
python visual-navigation/next-step-prediction/sample.py --jsonl-path ../dataset/visual-navigation/next-step-prediction.jsonl --output-folder {output-folder} --setting {setting}
python visual-tiling/sample.py --jsonl-path ../dataset/visual-tiling/visual-tiling.jsonl --output-folder {output-folder} --setting {setting}
```
The performance of specific setting will be printed on the terminal. The path of log file is also provided, which includes all failing cases for debugging purpose.
To be noticed, the LLM-generated responses are parsed based on regex pattern, and default patterns implemented in the code are for GPT-family models. You may need to **specify regex patterns for other models** and pay attention to "failing to parse" cases in the log file. To use the regex patterns we implemented for [LLaMA](https://github.com/microsoft/visualization-of-thought/blob/main/src/visual-navigation/next-step-prediction/llama-regex-patterns.txt) or your customized patterns, just specify the parameter `--regex-path` when running the evaluation script.

## Dataset Schema
### Main Schema

| Field Name        | Description                                                                                 | Type              | Example                          |
|-------------------|---------------------------------------------------------------------------------------------|-------------------|----------------------------------|
| `desc`            | Text input for LLMs.                                                                        | String            | "" |
| `desc_multimodal` | Message array input for MLLMs, containing text and images, following [Azure OpenAI format](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision?tabs=rest%2Csystem-assigned%2Cresource#call-the-chat-completion-apis).   | Array of Messages | `[{}]` |
| `answer`          | A single string, or a list of strings for route planning tasks.                             | String or String Array   | "A" or `["left", "down"]` |
| `puzzle_path`     | Folder of each prompt instance.                                                               | String            | "puzzles/level-2/103/Tetromino T"            |
| `config_path`     | Folder of images and original spatial configurations.                                         | String            | "configurations/level-2/103"         |
| `difficulty`      | Difficulty level of the question or puzzle.                                                 | Integer            | 2                         |
| `instance_id`     | Relative path to the instance identifier within the puzzle folder.                          | String            | "103/Tetromino T"            |

### Schema for Natural Language Navigation Task

| Field Name        | Description                | Type   | Example                      |
|-------------------|----------------------------|--------|------------------------------|
| `question`        | The navigation question.   | String | "" |
| `answer`          | The name of the object to be found.     | String | "Sofa" |


## Code for data construction/augmentation
This dataset could be extended by specifying the difficulty. Please refer to the scripts generating the dataset of visual tasks.
1. **Visual Navigation**:

```bash
# make sure to switch to the src folder
mkdir -p ../dataset
sh visual-navigation/gen-data.sh ../dataset/visual-navigation
```
Run following commands to extend with a new difficulty level K.

```bash

python visual-navigation/gen_all_paths.py --turn {K} --dest-folder ../dataset/visual-navigation/configurations/level-{K}
python visual-navigation/route-planning/gen_puzzle.py --config-folder ../dataset/visual-navigation/configurations/level-{K} --puzzle-folder ../dataset/visual-navigation/route-planning/level-{K} --output-jsonl ../dataset/visual-navigation/route-planning.jsonl --difficulty {K}
python visual-navigation/next-step-prediction/gen_puzzle.py --config-folder ../dataset/visual-navigation/configurations/level-{K} --puzzle-folder ../dataset/visual-navigation/next-step-prediction/level-{K} --output-jsonl ../dataset/visual-navigation/next-step-prediction.jsonl --difficulty {K}
```
2. **Visual Tiling**:

```bash
# make sure to switch to the src folder
mkdir -p ../dataset
# uncomment line `npm install` to install dependency node modules.
sh visual-tiling/gen-data.sh ../dataset/visual-tiling
```

Run following commands to extend with a new difficulty level K, rectangle size and polyomino pieces. For example, a 5 * 4 rectangle could be filled by "TTLII" (2 T pieces, 1 L piece and 2 I pieces).

```bash
cd visual-tiling/gen-solution
node run.js --width=4 --height=5 --masked=K --dest=../dataset/visual-tiling/configurations/level-{K} --pieces='TTLII'
cd ..
python gen_puzzle.py --config-folder ../dataset/visual-tiling/configurations/level-{K} --puzzle-folder ../dataset/visual-tiling/puzzles/level-{K} --output-jsonl ../dataset/visual-tiling/visual-tiling.jsonl --difficulty {K}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, feel free to open an issue in the repository or contact the authors.

## Citation

If you use this dataset, please cite us:

```bibtex
@misc{wu2024mindseyellmsvisualizationofthought,
      title={Mind's Eye of LLMs: Visualization-of-Thought Elicits Spatial Reasoning in Large Language Models}, 
      author={Wenshan Wu and Shaoguang Mao and Yadong Zhang and Yan Xia and Li Dong and Lei Cui and Furu Wei},
      year={2024},
      eprint={2404.03622},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2404.03622}, 
}

