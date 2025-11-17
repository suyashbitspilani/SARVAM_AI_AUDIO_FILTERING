# Quick Start Guide

Author: Suyash Khare

## Installation

Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Demo

Generate synthetic audio and test the pipeline:
```bash
python demo.py
```

This creates 20 sample audio files and processes them through the pipeline. Results are saved to demo_output/.

## View Results

Check the summary:
```bash
cat demo_output/filtering_results.csv
cat demo_output/rejected_files.txt
```

Generate visualizations:
```bash
python analyze_results.py demo_output
```

## Process Your Own Data

Process a directory of audio files:
```bash
python run_pipeline.py --dataset-dir /path/to/audio --output-dir results --num-workers 8
```

Process files from a list:
```bash
python run_pipeline.py --file-list audio_files.txt --output-dir results
```

## Custom Configuration

Create a JSON config file or override thresholds via command line:
```bash
python run_pipeline.py --dataset-dir data/ --min-snr 15 --max-silence 0.3 --output-dir results
```

Use predefined configurations:
```bash
python run_pipeline.py --config configs/strict_quality.json --dataset-dir data/ --output-dir results
```

## Understanding Output

filtering_results.csv: Per-sample metrics and filtering decisions  
accepted_files.txt: List of files that passed quality checks  
rejected_files.txt: List of rejected files with reasons  
config.json: Configuration used for the run  

## Typical Workflow

1. Run demo to verify installation
2. Test on small sample of your data
3. Adjust thresholds based on results
4. Process full dataset
5. Analyze results with visualization script

## Common Adjustments

For noisy field recordings:
```bash
python run_pipeline.py --min-snr 8 --max-silence 0.5 --dataset-dir data/
```

For high-quality studio recordings:
```bash
python run_pipeline.py --min-snr 15 --max-clipping 0.005 --dataset-dir data/
```

For short utterances:
```bash
python run_pipeline.py --config configs/short_utterances.json --dataset-dir data/
```
