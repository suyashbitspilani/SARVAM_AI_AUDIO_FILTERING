import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('demo_output/filtering_results.csv')

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

fig.suptitle('Audio Filtering Pipeline - Decision Analysis\nSuyash Khare', 
             fontsize=16, weight='bold')

accepted = df[df['is_accepted']]
rejected = df[~df['is_accepted']]

ax1.scatter(accepted['snr_db'], accepted['silence_ratio'], 
           color='green', alpha=0.6, s=100, label='Accepted', edgecolors='black')
ax1.scatter(rejected['snr_db'], rejected['silence_ratio'], 
           color='red', alpha=0.6, s=100, label='Rejected', edgecolors='black')
ax1.axvline(10, color='black', linestyle='--', linewidth=2, label='SNR Threshold (10 dB)')
ax1.axhline(0.4, color='black', linestyle='--', linewidth=2, label='Silence Threshold (40%)')
ax1.set_xlabel('SNR (dB)', fontsize=12, weight='bold')
ax1.set_ylabel('Silence Ratio', fontsize=12, weight='bold')
ax1.set_title('Decision Boundary: SNR vs Silence', fontsize=13, weight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)

scores_accepted = accepted['quality_score'].values
scores_rejected = rejected['quality_score'].values

bp = ax2.boxplot([scores_accepted, scores_rejected], 
                  labels=['Accepted', 'Rejected'],
                  patch_artist=True,
                  boxprops=dict(facecolor='lightblue', alpha=0.7),
                  medianprops=dict(color='red', linewidth=2))
bp['boxes'][0].set_facecolor('green')
bp['boxes'][0].set_alpha(0.5)
bp['boxes'][1].set_facecolor('red')
bp['boxes'][1].set_alpha(0.5)

ax2.set_ylabel('Quality Score', fontsize=12, weight='bold')
ax2.set_title('Quality Score Distribution', fontsize=13, weight='bold')
ax2.grid(True, alpha=0.3, axis='y')

for i, (label, data) in enumerate([('Accepted', scores_accepted), ('Rejected', scores_rejected)]):
    ax2.text(i+1, data.mean(), f'{data.mean():.1f}', 
            ha='center', va='bottom', fontsize=10, weight='bold')

metrics = ['snr_db', 'silence_ratio', 'clipping_ratio', 'rms_energy', 'dynamic_range_db']
accepted_means = [accepted[m].mean() for m in metrics]
rejected_means = [rejected[m].mean() for m in metrics]

x = np.arange(len(metrics))
width = 0.35

bars1 = ax3.bar(x - width/2, accepted_means, width, label='Accepted', 
                color='green', alpha=0.7, edgecolor='black')
bars2 = ax3.bar(x + width/2, rejected_means, width, label='Rejected', 
                color='red', alpha=0.7, edgecolor='black')

ax3.set_ylabel('Average Value', fontsize=12, weight='bold')
ax3.set_title('Metric Comparison: Accepted vs Rejected', fontsize=13, weight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(['SNR\n(dB)', 'Silence\nRatio', 'Clipping\nRatio', 
                     'RMS\nEnergy', 'Dynamic\nRange'], fontsize=9)
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

ax4.scatter(df['snr_db'], df['quality_score'], 
           c=df['is_accepted'].map({True: 'green', False: 'red'}),
           alpha=0.6, s=100, edgecolors='black')
ax4.axvline(10, color='black', linestyle='--', linewidth=2, alpha=0.5)
ax4.set_xlabel('SNR (dB)', fontsize=12, weight='bold')
ax4.set_ylabel('Quality Score', fontsize=12, weight='bold')
ax4.set_title('SNR vs Quality Score', fontsize=13, weight='bold')
ax4.grid(True, alpha=0.3)

z = np.polyfit(df['snr_db'], df['quality_score'], 1)
p = np.poly1d(z)
ax4.plot(df['snr_db'].sort_values(), p(df['snr_db'].sort_values()), 
        "b--", linewidth=2, label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
ax4.legend()

plt.tight_layout()
plt.savefig('demo_output/decision_boundary.png', dpi=300, bbox_inches='tight')
print("Visualization saved to demo_output/decision_boundary.png")
print("\nKey Observations:")
print(f"- Accepted files: Mean quality score = {scores_accepted.mean():.2f}")
print(f"- Rejected files: Mean quality score = {scores_rejected.mean():.2f}")
print(f"- Clear separation of {scores_accepted.mean() - scores_rejected.mean():.2f} points")
print(f"- Decision boundaries effectively split quality space")
