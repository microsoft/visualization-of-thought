# Transparency.md for VoT

## Overview
Visualization-of-Thought (VoT) is an innovative project focused on enhancing the spatial reasoning capabilities of Large Language Models (LLMs). By leveraging the VoT prompting method, we aim to elicit the "mind's eye" of LLMs, allowing them to create and manipulate mental images during reasoning tasks. This project includes data curation scripts, utility code for metrics evaluation, and sample code to run experiments with the dataset.

## Objective
The primary objective of the VoT project is to explore and demonstrate the potential of LLMs in spatial reasoning tasks by visualizing their intermediate reasoning steps. This approach aims to improve the spatial awareness of LLMs, making them more effective in tasks such as natural language navigation, visual navigation, and visual tiling.

## Audience
This documentation is intended for researchers, AI practitioners, and developers who are interested in the application, limitations, and optimization of LLMs for spatial reasoning tasks.

## Key Features
- Scripts for data curation to generate synthetic datasets for spatial reasoning tasks.
- Utility code for metrics evaluation to assess model performance.
- Sample code to run experiments and evaluate the performance.

## Limitations
- This code repo works as a testbed for spatial reasoning tasks proposed. It's not designed for real-world scenarios and tasks.
- The current implementation of LLM response parsing is regex, which might lead to empty parsing. Please pay attention to those failure cases. You might add more regex patterns to avoid parsing failure, or use an LLM to extract and format answers from the raw responses.


## Best Practices for Performance
- Implement the run_llm_client function in sample code provided for each task.
- Experiment with different prompts and methods to optimize performance.

## Social Impact Statement
VoT is designed to advance our understanding of spatial reasoning in LLMs and their practical applications. Our work aims to contribute positively to society by evaluating and improving AI's cognitive and reasoning abilities.

## Usage
- This project is intended for research and experimental purposes. Further testing and validation are recommended before applying it in real-world scenarios.

## Feedback and Collaboration
We welcome feedback and collaboration from our audience. If you have suggestions, questions, or would like to contribute to the project, please feel free to contact us at wenswu@microsoft.com.

## Future Updates
The VoT project is an ongoing initiative. We plan to expand its capabilities to handle more diverse data types and improve its performance in spatial reasoning tasks. Stay updated with our progress through our code repository and publications.

## Conclusion
The VoT project represents a significant advancement in enhancing the spatial reasoning capabilities of LLMs. We hope this framework will be valuable for researchers, AI practitioners, and developers in their respective domains.