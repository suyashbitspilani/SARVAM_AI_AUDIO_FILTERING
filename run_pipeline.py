import argparse
import json
from pathlib import Path
from audio_filter_pipeline import AudioFilterPipeline, create_default_config


def load_file_list(file_list_path: str) -> list:
    with open(file_list_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def load_config(config_path: str = None):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return create_default_config()


def save_config(config: dict, output_path: str):
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Audio Filtering Pipeline for Indic Speech')
    
    parser.add_argument('--dataset-dir', type=str,
                       help='Directory containing audio files')
    parser.add_argument('--file-list', type=str,
                       help='Text file with list of audio file paths')
    parser.add_argument('--config', type=str,
                       help='Path to configuration JSON file')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for results')
    parser.add_argument('--num-workers', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--min-snr', type=float,
                       help='Minimum SNR in dB (override config)')
    parser.add_argument('--max-silence', type=float,
                       help='Maximum silence ratio 0-1 (override config)')
    parser.add_argument('--max-clipping', type=float,
                       help='Maximum clipping ratio 0-1 (override config)')
    
    args = parser.parse_args()
    
    file_paths = []
    
    if args.file_list:
        file_paths = load_file_list(args.file_list)
    elif args.dataset_dir:
        dataset_path = Path(args.dataset_dir)
        extensions = ['*.wav', '*.mp3', '*.flac', '*.ogg']
        for ext in extensions:
            file_paths.extend([str(p) for p in dataset_path.rglob(ext)])
    else:
        parser.error("Must specify --dataset-dir or --file-list")
    
    if not file_paths:
        print("Error: No audio files found")
        return
    
    print(f"\nFound {len(file_paths)} audio files")
    
    config = load_config(args.config)
    
    if args.min_snr is not None:
        config['thresholds']['min_snr_db'] = args.min_snr
    if args.max_silence is not None:
        config['thresholds']['max_silence_ratio'] = args.max_silence
    if args.max_clipping is not None:
        config['thresholds']['max_clipping_ratio'] = args.max_clipping
    
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    save_config(config, output_path / "config.json")
    
    print("\nConfiguration:")
    print(json.dumps(config, indent=2))
    
    print(f"\nStarting filtering pipeline...")
    pipeline = AudioFilterPipeline(config)
    results = pipeline.process_dataset(file_paths, args.output_dir, 
                                      num_workers=args.num_workers)
    
    print(f"\nPipeline completed successfully")
    print(f"Results saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
