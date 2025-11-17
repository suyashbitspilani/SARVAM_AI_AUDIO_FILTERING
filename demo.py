import numpy as np
import soundfile as sf
from pathlib import Path
import json
from audio_filter_pipeline import AudioFilterPipeline, create_default_config


def generate_sample_audio_files(output_dir: str = "demo_data", num_samples: int = 20):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    sr = 16000
    print(f"Generating {num_samples} sample audio files...")
    
    samples_info = []
    audio_files = []
    
    for i in range(num_samples):
        if i % 4 == 0:
            duration = 5.0
            snr_db = 20
            silence_ratio = 0.2
            sample_type = "good_quality"
        elif i % 4 == 1:
            duration = 4.0
            snr_db = 5
            silence_ratio = 0.15
            sample_type = "noisy"
        elif i % 4 == 2:
            duration = 6.0
            snr_db = 15
            silence_ratio = 0.6
            sample_type = "silent"
        else:
            duration = 3.0
            snr_db = 18
            silence_ratio = 0.1
            sample_type = "clipped"
        
        t = np.linspace(0, duration, int(sr * duration))
        
        signal = (
            0.3 * np.sin(2 * np.pi * 200 * t) +
            0.2 * np.sin(2 * np.pi * 400 * t) +
            0.1 * np.sin(2 * np.pi * 800 * t)
        )
        
        envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
        signal = signal * envelope
        
        if sample_type == "noisy":
            noise_power = 10 ** (-snr_db / 20)
            noise = np.random.normal(0, noise_power, len(signal))
            signal = signal + noise
        
        if sample_type == "silent":
            silent_sections = int(len(signal) * 0.5)
            signal[:silent_sections] = 0
        
        if sample_type == "clipped":
            signal = signal * 2.0
            signal = np.clip(signal, -1.0, 1.0)
        
        if sample_type != "clipped":
            signal = signal / (np.max(np.abs(signal)) + 0.01) * 0.8
        
        file_path = output_path / f"sample_{i:03d}_{sample_type}.wav"
        sf.write(file_path, signal, sr)
        
        samples_info.append({
            'file': str(file_path),
            'type': sample_type,
            'duration': duration,
            'expected_result': 'accept' if sample_type == 'good_quality' else 'reject'
        })
        
        audio_files.append(str(file_path))
    
    info_path = output_path / "samples_info.json"
    with open(info_path, 'w') as f:
        json.dump(samples_info, f, indent=2)
    
    print(f"Generated {num_samples} sample files in {output_dir}/")
    
    return audio_files


def run_demo():
    print("="*70)
    print("AUDIO FILTERING PIPELINE - DEMONSTRATION")
    print("="*70)
    print()
    
    print("Step 1: Generating Sample Audio Files")
    print("-"*70)
    sample_files = generate_sample_audio_files("demo_data", num_samples=20)
    print()
    
    print("Step 2: Initializing Pipeline")
    print("-"*70)
    config = create_default_config()
    pipeline = AudioFilterPipeline(config)
    print("Pipeline initialized with default configuration")
    print()
    
    print("Step 3: Processing Audio Files")
    print("-"*70)
    results = pipeline.process_dataset(
        file_paths=sample_files,
        output_path="demo_output",
        num_workers=4
    )
    print()
    
    print("Step 4: Sample Results")
    print("-"*70)
    print(f"\nShowing first 5 processed files:\n")
    
    for i, result in enumerate(results[:5]):
        status = "ACCEPTED" if result.is_accepted else "REJECTED"
        print(f"\nFile {i+1}: {Path(result.file_path).name}")
        print(f"  Status: {status}")
        print(f"  Quality Score: {result.quality_score:.2f}")
        print(f"  Duration: {result.duration:.2f}s")
        print(f"  SNR: {result.snr_db:.2f} dB")
        print(f"  Silence: {result.silence_ratio:.1%}")
        print(f"  Clipping: {result.clipping_ratio:.2%}")
        if not result.is_accepted:
            print(f"  Reasons: {', '.join(result.rejection_reasons)}")
    
    print()
    print("="*70)
    print("DEMONSTRATION COMPLETED")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Check demo_output/ for detailed results")
    print("2. View filtering_results.csv for all metrics")
    print("3. Check accepted_files.txt and rejected_files.txt")
    print()


if __name__ == "__main__":
    run_demo()
