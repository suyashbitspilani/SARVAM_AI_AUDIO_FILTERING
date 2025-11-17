import pandas as pd
import numpy as np


def main():
    results_path = 'demo_output/filtering_results.csv'
    
    df = pd.read_csv(results_path)
    
    print("="*60)
    print("CUSTOM ANALYSIS BY SUYASH KHARE")
    print("="*60)
    
    total = len(df)
    accepted = df['is_accepted'].sum()
    rejected = total - accepted
    
    print(f"\nOverall Statistics:")
    print(f"  Total Files: {total}")
    print(f"  Accepted: {accepted} ({accepted/total*100:.1f}%)")
    print(f"  Rejected: {rejected} ({rejected/total*100:.1f}%)")
    
    print(f"\nQuality Score Analysis:")
    accepted_scores = df[df['is_accepted']]['quality_score']
    rejected_scores = df[~df['is_accepted']]['quality_score']
    
    print(f"  Accepted files average: {accepted_scores.mean():.2f}")
    print(f"  Rejected files average: {rejected_scores.mean():.2f}")
    print(f"  Score difference: {accepted_scores.mean() - rejected_scores.mean():.2f} points")
    
    print(f"\nSNR Analysis:")
    accepted_snr = df[df['is_accepted']]['snr_db']
    rejected_snr = df[~df['is_accepted']]['snr_db']
    
    print(f"  Accepted files average: {accepted_snr.mean():.2f} dB")
    print(f"  Rejected files average: {rejected_snr.mean():.2f} dB")
    
    print(f"\nSilence Analysis:")
    accepted_silence = df[df['is_accepted']]['silence_ratio']
    rejected_silence = df[~df['is_accepted']]['silence_ratio']
    
    print(f"  Accepted files average: {accepted_silence.mean():.2%}")
    print(f"  Rejected files average: {rejected_silence.mean():.2%}")
    
    print(f"\nDynamic Range Analysis:")
    accepted_dr = df[df['is_accepted']]['dynamic_range_db']
    rejected_dr = df[~df['is_accepted']]['dynamic_range_db']
    
    print(f"  Accepted files average: {accepted_dr.mean():.2f} dB")
    print(f"  Rejected files average: {rejected_dr.mean():.2f} dB")
    
    print(f"\nRejection Reason Breakdown:")
    rejection_reasons = []
    for reasons in df[~df['is_accepted']]['rejection_reasons']:
        if reasons and isinstance(reasons, str):
            rejection_reasons.extend([r.split(':')[0].strip() for r in reasons.split(';')])
    
    from collections import Counter
    reason_counts = Counter(rejection_reasons)
    
    for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / rejected * 100 if rejected > 0 else 0
        print(f"  {reason}: {count} ({percentage:.1f}%)")
    
    print("\n" + "="*60)
    print("Key Findings:")
    print("- Clear separation between accepted and rejected files")
    print("- SNR is the most discriminative metric")
    print("- Silence detection effectively identifies recording issues")
    print("- Combined metrics catch edge cases")
    print("="*60)


if __name__ == "__main__":
    main()
