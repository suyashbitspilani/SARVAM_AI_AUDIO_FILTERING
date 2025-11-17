import pandas as pd

configs = {
    "Default": {"min_snr_db": 10.0, "max_silence_ratio": 0.4},
    "Strict": {"min_snr_db": 15.0, "max_silence_ratio": 0.3},
    "Lenient": {"min_snr_db": 7.0, "max_silence_ratio": 0.5}
}

df = pd.read_csv('demo_output/filtering_results.csv')

print("="*60)
print("THRESHOLD SENSITIVITY ANALYSIS")
print("="*60)

for config_name, thresholds in configs.items():
    accepted = df[
        (df['snr_db'] >= thresholds['min_snr_db']) & 
        (df['silence_ratio'] <= thresholds['max_silence_ratio'])
    ]
    
    acceptance_rate = len(accepted) / len(df) * 100
    avg_score = accepted['quality_score'].mean() if len(accepted) > 0 else 0
    
    print(f"\n{config_name} Configuration:")
    print(f"  SNR threshold: {thresholds['min_snr_db']} dB")
    print(f"  Silence threshold: {thresholds['max_silence_ratio']:.1%}")
    print(f"  Acceptance rate: {acceptance_rate:.1f}%")
    print(f"  Avg quality score: {avg_score:.2f}")

print("="*60)
print("\nKey Insights:")
print("- Default thresholds balance quality and retention")
print("- Stricter thresholds ensure higher quality but reduce dataset size")
print("- Lenient thresholds maximize dataset size but accept lower quality")
print("\nProduction Recommendation:")
print("- A/B test different thresholds with downstream ASR accuracy")
print("- Monitor rejection patterns by language and recording condition")
print("="*60)
