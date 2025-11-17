import os
from pathlib import Path
from datasets import load_dataset
import soundfile as sf
from tqdm import tqdm
import json


def download_indicvoices_subset(
    output_dir: str = "data/indicvoices",
    languages: list = None,
    max_samples_per_language: int = 500,
    split: str = "train"
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Loading IndicVoices dataset...")
    print("Note: This may take a while on first run as data is downloaded.")
    
    dataset = load_dataset(
        "ai4bharat/IndicVoices",
        split=split,
        streaming=True
    )
    
    if languages is None:
        languages = ['hindi', 'bengali', 'telugu', 'marathi', 'tamil', 
                    'gujarati', 'kannada', 'malayalam', 'punjabi', 'odia']
    
    language_counts = {lang: 0 for lang in languages}
    audio_files = []
    metadata = []
    
    print(f"\nDownloading up to {max_samples_per_language} samples per language...")
    
    for idx, sample in enumerate(tqdm(dataset)):
        if all(count >= max_samples_per_language for count in language_counts.values()):
            break
        
        lang = sample.get('language', '').lower()
        
        if lang not in languages or language_counts[lang] >= max_samples_per_language:
            continue
        
        try:
            audio_data = sample['audio']
            audio_array = audio_data['array']
            sampling_rate = audio_data['sampling_rate']
            
            lang_dir = output_path / lang
            lang_dir.mkdir(exist_ok=True)
            
            file_name = f"{lang}_{language_counts[lang]:05d}.wav"
            file_path = lang_dir / file_name
            
            sf.write(file_path, audio_array, sampling_rate)
            
            metadata.append({
                'file_path': str(file_path),
                'language': lang,
                'duration': len(audio_array) / sampling_rate,
                'sample_rate': sampling_rate,
                'text': sample.get('text', ''),
                'speaker_id': sample.get('speaker_id', ''),
            })
            
            audio_files.append(str(file_path))
            language_counts[lang] += 1
            
        except Exception as e:
            print(f"\nError processing sample {idx}: {e}")
            continue
    
    metadata_path = output_path / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    filelist_path = output_path / "file_list.txt"
    with open(filelist_path, 'w') as f:
        for file_path in audio_files:
            f.write(f"{file_path}\n")
    
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Total files downloaded: {len(audio_files)}")
    print(f"Saved to: {output_path}")
    print(f"\nFiles per language:")
    for lang, count in sorted(language_counts.items()):
        print(f"  {lang}: {count}")
    print(f"\nMetadata saved to: {metadata_path}")
    print(f"File list saved to: {filelist_path}")
    print("="*60)
    
    return audio_files, metadata


def load_file_list(file_list_path: str) -> list:
    with open(file_list_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    audio_files, metadata = download_indicvoices_subset(
        output_dir="data/indicvoices",
        languages=['hindi', 'bengali', 'telugu', 'tamil', 'kannada'],
        max_samples_per_language=200,
        split="train"
    )
    
    print(f"\nDataset ready for processing")
    print(f"Use the file list at: data/indicvoices/file_list.txt")
