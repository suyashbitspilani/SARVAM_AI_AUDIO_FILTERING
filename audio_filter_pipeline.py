import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import csv
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


@dataclass
class AudioMetrics:
    file_path: str
    duration: float
    sample_rate: int
    snr_db: float
    silence_ratio: float
    clipping_ratio: float
    zero_crossing_rate: float
    spectral_centroid_mean: float
    spectral_rolloff_mean: float
    rms_energy: float
    dynamic_range_db: float
    quality_score: float
    is_accepted: bool
    rejection_reasons: List[str]


class AudioQualityAnalyzer:
    
    def __init__(self, sr: int = 16000):
        self.sr = sr
        
    def compute_snr(self, audio: np.ndarray, frame_length: int = 2048) -> float:
        hop_length = frame_length // 2
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        energy = np.sum(frames ** 2, axis=0)
        
        if len(energy) == 0:
            return -np.inf
        
        noise_threshold = np.percentile(energy, 10)
        noise_frames = energy[energy <= noise_threshold]
        signal_frames = energy[energy > noise_threshold]
        
        if len(noise_frames) == 0 or len(signal_frames) == 0:
            return 0.0
        
        noise_power = np.mean(noise_frames)
        signal_power = np.mean(signal_frames)
        
        if noise_power == 0:
            return 50.0
        
        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)
    
    def compute_silence_ratio(self, audio: np.ndarray, top_db: int = 30) -> float:
        non_silent_intervals = librosa.effects.split(audio, top_db=top_db)
        
        if len(non_silent_intervals) == 0:
            return 1.0
        
        non_silent_duration = sum(end - start for start, end in non_silent_intervals)
        silence_ratio = 1.0 - (non_silent_duration / len(audio))
        
        return float(max(0.0, min(1.0, silence_ratio)))
    
    def compute_clipping_ratio(self, audio: np.ndarray, threshold: float = 0.99) -> float:
        clipped_samples = np.sum(np.abs(audio) >= threshold)
        clipping_ratio = clipped_samples / len(audio)
        return float(clipping_ratio)
    
    def compute_zero_crossing_rate(self, audio: np.ndarray) -> float:
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        return float(np.mean(zcr))
    
    def compute_spectral_features(self, audio: np.ndarray) -> Tuple[float, float]:
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sr)[0]
        
        return float(np.mean(spectral_centroid)), float(np.mean(spectral_rolloff))
    
    def compute_rms_energy(self, audio: np.ndarray) -> float:
        rms = librosa.feature.rms(y=audio)[0]
        return float(np.mean(rms))
    
    def compute_dynamic_range(self, audio: np.ndarray) -> float:
        if len(audio) == 0:
            return 0.0
        
        rms = librosa.feature.rms(y=audio)[0]
        rms_db = librosa.amplitude_to_db(rms + 1e-10)
        
        dynamic_range = np.max(rms_db) - np.min(rms_db)
        return float(dynamic_range)
    
    def analyze_audio(self, audio: np.ndarray) -> Dict[str, float]:
        metrics = {}
        
        metrics['snr_db'] = self.compute_snr(audio)
        metrics['silence_ratio'] = self.compute_silence_ratio(audio)
        metrics['clipping_ratio'] = self.compute_clipping_ratio(audio)
        metrics['zero_crossing_rate'] = self.compute_zero_crossing_rate(audio)
        
        spectral_centroid, spectral_rolloff = self.compute_spectral_features(audio)
        metrics['spectral_centroid_mean'] = spectral_centroid
        metrics['spectral_rolloff_mean'] = spectral_rolloff
        
        metrics['rms_energy'] = self.compute_rms_energy(audio)
        metrics['dynamic_range_db'] = self.compute_dynamic_range(audio)
        
        return metrics


class AudioFilterPipeline:
    
    def __init__(self, config: Dict):
        self.config = config
        self.analyzer = AudioQualityAnalyzer(sr=config['sample_rate'])
        self.thresholds = config['thresholds']
        self.weights = config.get('weights', {})
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        try:
            audio, sr = librosa.load(file_path, sr=self.config['sample_rate'])
            return audio, sr
        except Exception as e:
            raise RuntimeError(f"Failed to load {file_path}: {e}")
    
    def compute_quality_score(self, metrics: Dict[str, float]) -> float:
        score = 0.0
        
        snr = metrics['snr_db']
        snr_score = min(30, max(0, (snr / 20) * 30))
        score += snr_score * self.weights.get('snr', 0.3)
        
        silence_score = (1 - metrics['silence_ratio']) * 20
        score += silence_score * self.weights.get('silence', 0.2)
        
        clipping_score = (1 - min(1.0, metrics['clipping_ratio'] * 100)) * 20
        score += clipping_score * self.weights.get('clipping', 0.2)
        
        dr = metrics['dynamic_range_db']
        dr_score = min(15, max(0, (dr / 40) * 15))
        score += dr_score * self.weights.get('dynamic_range', 0.15)
        
        rms = metrics['rms_energy']
        rms_score = min(15, max(0, (rms / 0.1) * 15))
        score += rms_score * self.weights.get('rms', 0.15)
        
        return score
    
    def check_thresholds(self, metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
        reasons = []
        
        if metrics['snr_db'] < self.thresholds['min_snr_db']:
            reasons.append(f"Low SNR: {metrics['snr_db']:.2f} dB")
        
        if metrics['silence_ratio'] > self.thresholds['max_silence_ratio']:
            reasons.append(f"Too much silence: {metrics['silence_ratio']:.2%}")
        
        if metrics['clipping_ratio'] > self.thresholds['max_clipping_ratio']:
            reasons.append(f"Clipping detected: {metrics['clipping_ratio']:.2%}")
        
        if metrics['rms_energy'] < self.thresholds['min_rms_energy']:
            reasons.append(f"Low energy: {metrics['rms_energy']:.4f}")
        
        if metrics['dynamic_range_db'] < self.thresholds['min_dynamic_range_db']:
            reasons.append(f"Low dynamic range: {metrics['dynamic_range_db']:.2f} dB")
        
        is_accepted = len(reasons) == 0
        return is_accepted, reasons
    
    def process_file(self, file_path: str) -> AudioMetrics:
        try:
            audio, sr = self.load_audio(file_path)
            duration = len(audio) / sr
            
            if duration < self.thresholds['min_duration_sec']:
                return AudioMetrics(
                    file_path=file_path,
                    duration=duration,
                    sample_rate=sr,
                    snr_db=0, silence_ratio=0, clipping_ratio=0,
                    zero_crossing_rate=0, spectral_centroid_mean=0,
                    spectral_rolloff_mean=0, rms_energy=0, dynamic_range_db=0,
                    quality_score=0,
                    is_accepted=False,
                    rejection_reasons=[f"Too short: {duration:.2f}s"]
                )
            
            if duration > self.thresholds['max_duration_sec']:
                return AudioMetrics(
                    file_path=file_path,
                    duration=duration,
                    sample_rate=sr,
                    snr_db=0, silence_ratio=0, clipping_ratio=0,
                    zero_crossing_rate=0, spectral_centroid_mean=0,
                    spectral_rolloff_mean=0, rms_energy=0, dynamic_range_db=0,
                    quality_score=0,
                    is_accepted=False,
                    rejection_reasons=[f"Too long: {duration:.2f}s"]
                )
            
            metrics = self.analyzer.analyze_audio(audio)
            quality_score = self.compute_quality_score(metrics)
            is_accepted, rejection_reasons = self.check_thresholds(metrics)
            
            return AudioMetrics(
                file_path=file_path,
                duration=duration,
                sample_rate=sr,
                quality_score=quality_score,
                is_accepted=is_accepted,
                rejection_reasons=rejection_reasons,
                **metrics
            )
            
        except Exception as e:
            return AudioMetrics(
                file_path=file_path,
                duration=0, sample_rate=0,
                snr_db=0, silence_ratio=0, clipping_ratio=0,
                zero_crossing_rate=0, spectral_centroid_mean=0,
                spectral_rolloff_mean=0, rms_energy=0, dynamic_range_db=0,
                quality_score=0,
                is_accepted=False,
                rejection_reasons=[f"Processing error: {str(e)}"]
            )
    
    def process_dataset(self, file_paths: List[str], output_path: str, 
                       num_workers: int = 4) -> List[AudioMetrics]:
        results = []
        
        print(f"Processing {len(file_paths)} files with {num_workers} workers...")
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_path = {
                executor.submit(self.process_file, path): path 
                for path in file_paths
            }
            
            for future in tqdm(as_completed(future_to_path), total=len(file_paths)):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    path = future_to_path[future]
                    print(f"Error processing {path}: {e}")
        
        self.save_results(results, output_path)
        self.print_summary(results)
        
        return results
    
    def save_results(self, results: List[AudioMetrics], output_path: str):
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        csv_path = output_path / "filtering_results.csv"
        with open(csv_path, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=asdict(results[0]).keys())
                writer.writeheader()
                for result in results:
                    row = asdict(result)
                    row['rejection_reasons'] = '; '.join(row['rejection_reasons'])
                    writer.writerow(row)
        
        json_path = output_path / "filtering_results.json"
        with open(json_path, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        
        accepted_path = output_path / "accepted_files.txt"
        rejected_path = output_path / "rejected_files.txt"
        
        with open(accepted_path, 'w') as f:
            for r in results:
                if r.is_accepted:
                    f.write(f"{r.file_path}\n")
        
        with open(rejected_path, 'w') as f:
            for r in results:
                if not r.is_accepted:
                    f.write(f"{r.file_path}\t{'; '.join(r.rejection_reasons)}\n")
        
        print(f"\nResults saved to {output_path}/")
    
    def print_summary(self, results: List[AudioMetrics]):
        total = len(results)
        accepted = sum(1 for r in results if r.is_accepted)
        rejected = total - accepted
        
        print("\n" + "="*60)
        print("FILTERING SUMMARY")
        print("="*60)
        print(f"Total files processed: {total}")
        print(f"Accepted: {accepted} ({accepted/total*100:.1f}%)")
        print(f"Rejected: {rejected} ({rejected/total*100:.1f}%)")
        
        if rejected > 0:
            print("\nRejection reasons breakdown:")
            reason_counts = {}
            for r in results:
                if not r.is_accepted:
                    for reason in r.rejection_reasons:
                        reason_key = reason.split(':')[0]
                        reason_counts[reason_key] = reason_counts.get(reason_key, 0) + 1
            
            for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count} ({count/rejected*100:.1f}%)")
        
        scores = [r.quality_score for r in results]
        print(f"\nQuality Score Statistics:")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Median: {np.median(scores):.2f}")
        print(f"  Std Dev: {np.std(scores):.2f}")
        print(f"  Min: {np.min(scores):.2f}")
        print(f"  Max: {np.max(scores):.2f}")
        print("="*60)


def create_default_config() -> Dict:
    return {
        'sample_rate': 16000,
        'thresholds': {
            'min_snr_db': 10.0,
            'max_silence_ratio': 0.4,
            'max_clipping_ratio': 0.01,
            'min_rms_energy': 0.01,
            'min_dynamic_range_db': 15.0,
            'min_duration_sec': 1.0,
            'max_duration_sec': 30.0,
        },
        'weights': {
            'snr': 0.30,
            'silence': 0.20,
            'clipping': 0.20,
            'dynamic_range': 0.15,
            'rms': 0.15,
        }
    }
