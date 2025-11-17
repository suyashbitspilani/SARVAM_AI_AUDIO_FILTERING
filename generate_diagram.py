import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')

def draw_box(ax, x, y, w, h, text, color, text_color='white', fontsize=10, bold=False, alpha=1.0):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", 
                         edgecolor='black', facecolor=color, linewidth=2, alpha=alpha)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    if text:
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                fontsize=fontsize, color=text_color, weight=weight, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, label='', style='->'):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, 
                           mutation_scale=20, linewidth=2, color='black')
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=8, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax.text(5, 13.5, 'Audio Filtering Pipeline for Indic Speech', 
        ha='center', fontsize=18, weight='bold')
ax.text(5, 13, 'Suyash Khare - Sarvam AI Assignment', 
        ha='center', fontsize=12, style='italic')

draw_box(ax, 0.5, 11.5, 2, 0.8, 'INPUT\nAudio Files\n(WAV/MP3/FLAC)', 
         '#3498db', fontsize=11, bold=True)

draw_arrow(ax, 1.5, 11.5, 1.5, 10.8)

draw_box(ax, 0.3, 10, 2.4, 0.6, 'Audio Loading & Resampling\nTarget: 16kHz', 
         '#2ecc71', fontsize=9)

draw_arrow(ax, 1.5, 10, 1.5, 9.3)

draw_box(ax, 0.2, 8.5, 2.6, 0.6, 'Duration Check\n1-30 seconds', 
         '#e74c3c', 'white', fontsize=9)

draw_arrow(ax, 1.5, 8.5, 3.5, 8.2, 'Pass')
draw_arrow(ax, 0.2, 8.2, 0.2, 7.5, 'Fail')
draw_box(ax, 0.05, 7.2, 0.3, 0.5, 'REJECT', '#e74c3c', fontsize=7, bold=True)

ax.text(5, 9.2, 'QUALITY METRICS COMPUTATION', ha='center', 
        fontsize=13, weight='bold', 
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.3, pad=0.5))

metrics_x_start = 3
metrics_y = 7.5
metric_names = [
    ('Signal-to-Noise\nRatio (SNR)', 'Energy-based\nframe analysis'),
    ('Silence\nRatio', 'Onset detection\ntop_db=30'),
    ('Clipping\nRatio', 'Sample threshold\n±0.99'),
    ('RMS\nEnergy', 'Root mean\nsquare'),
    ('Dynamic\nRange', 'Max-Min\nRMS (dB)'),
    ('Zero Crossing\nRate', 'Sign change\nfrequency'),
    ('Spectral\nCentroid', 'Frequency\ncenter of mass'),
    ('Spectral\nRolloff', '85% energy\nfrequency')
]

for i, (name, desc) in enumerate(metric_names):
    row = i // 4
    col = i % 4
    x = metrics_x_start + col * 1.7
    y = metrics_y - row * 1.3
    
    draw_box(ax, x, y, 1.5, 0.5, name, '#9b59b6', fontsize=8, bold=True)
    draw_box(ax, x, y-0.45, 1.5, 0.35, desc, '#d7bde2', 'black', fontsize=7)

for i in range(4):
    x = metrics_x_start + i * 1.7 + 0.75
    draw_arrow(ax, x, metrics_y - 0.5, x, metrics_y - 1.0, style='-')

ax.text(6.5, 5.2, 'All Metrics', ha='center', fontsize=9, weight='bold')

draw_arrow(ax, 6.5, 5.1, 6.5, 4.7)

ax.text(5, 4.5, 'TWO-STAGE FILTERING', ha='center', fontsize=13, 
        weight='bold', bbox=dict(boxstyle='round', facecolor='#e67e22', alpha=0.3, pad=0.5))

draw_box(ax, 3.5, 3.2, 2.8, 0.9, 
         'STAGE 1: Hard Thresholds\n\n' +
         'SNR ≥ 10 dB\n' +
         'Silence ≤ 40%\n' +
         'Clipping ≤ 1%\n' +
         'RMS ≥ 0.01\n' +
         'Dynamic Range ≥ 15 dB',
         '#e74c3c', fontsize=8)

draw_arrow(ax, 6.3, 3.2, 7.3, 2.8, 'Fail')
draw_arrow(ax, 4.9, 3.2, 4.9, 2.6, 'Pass')

draw_box(ax, 7.3, 2.5, 2, 0.6, 
         'REJECT\nwith specific reason\n(Low SNR, etc.)',
         '#c0392b', fontsize=8, bold=True)

draw_box(ax, 3.7, 1.8, 2.4, 0.6,
         'STAGE 2: Quality Scoring\n\n' +
         'Score = SNR×0.30 + Silence×0.20\n' +
         '+ Clipping×0.20 + DR×0.15 + RMS×0.15',
         '#27ae60', fontsize=7)

draw_arrow(ax, 4.9, 1.8, 4.9, 1.3)

draw_box(ax, 3.9, 0.7, 2.0, 0.5,
         'ACCEPT\nQuality Score: 0-100',
         '#16a085', fontsize=9, bold=True)

ax.text(0.5, 5.8, 'PARALLEL\nPROCESSING', ha='center', fontsize=10, 
        weight='bold', rotation=90,
        bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.8, pad=0.3))

draw_box(ax, 0.05, 8.5, 0.25, 3.8, '', '#3498db', alpha=0.2)

workers = [(0.15, 11.3), (0.15, 10.5), (0.15, 9.7), (0.15, 8.9)]
for i, (x, y) in enumerate(workers):
    draw_box(ax, x, y, 0.15, 0.15, f'W{i+1}', '#2980b9', fontsize=6)

ax.text(0.5, 2.5, 'ProcessPoolExecutor\n8 Workers\n~4 files/sec', 
        ha='center', fontsize=8, 
        bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3, pad=0.3))

draw_arrow(ax, 4.9, 0.7, 4.9, 0.2)
draw_arrow(ax, 8.3, 2.5, 8.3, 0.2)

ax.text(5, 0.05, 'OUTPUT GENERATION', ha='center', fontsize=11, 
        weight='bold', bbox=dict(boxstyle='round', facecolor='#95a5a6', alpha=0.3, pad=0.3))

output_items = [
    ('filtering_results.csv', 0.5),
    ('filtering_results.json', 2.0),
    ('accepted_files.txt', 3.5),
    ('rejected_files.txt', 5.0),
    ('config.json', 6.5),
    ('Visualizations', 8.0)
]

for name, x in output_items:
    draw_box(ax, x, -0.8, 1.2, 0.4, name, '#7f8c8d', fontsize=7)
    draw_arrow(ax, x + 0.6, 0, x + 0.6, -0.4)

legend_x = 0.2
legend_y = 1.2

ax.text(legend_x, legend_y + 0.3, 'KEY FEATURES:', fontsize=9, weight='bold')

features = [
    ('8 complementary quality metrics', '#9b59b6'),
    ('Two-stage filtering logic', '#e67e22'),
    ('Parallel processing (linear scaling)', '#3498db'),
    ('Memory efficient (O(1) per worker)', '#2ecc71'),
    ('Configurable thresholds', '#f39c12')
]

for i, (feature, color) in enumerate(features):
    y = legend_y - i * 0.25
    draw_box(ax, legend_x, y - 0.1, 0.15, 0.15, '', color)
    ax.text(legend_x + 0.25, y, feature, fontsize=7, va='center')

perf_x = 0.2
perf_y = -0.3
ax.text(perf_x, perf_y, 'PERFORMANCE:', fontsize=9, weight='bold')
ax.text(perf_x, perf_y - 0.2, '• 4-5 files/second (8 cores)', fontsize=7)
ax.text(perf_x, perf_y - 0.4, '• 1000 files in ~4 minutes', fontsize=7)
ax.text(perf_x, perf_y - 0.6, '• Unlimited dataset size', fontsize=7)

ax.text(9.8, 13, 'Author: Suyash Khare\nDate: Nov 2024', 
        ha='right', fontsize=7, style='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sarvam-ai-audio-filtering/pipeline_diagram.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("Pipeline diagram saved to pipeline_diagram.png")
plt.close()

print("\nDiagram generated successfully!")
print("High-resolution PNG created for your video and documentation.")
