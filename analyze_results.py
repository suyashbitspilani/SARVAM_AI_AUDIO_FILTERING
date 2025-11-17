import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class ResultsAnalyzer:
    
    def __init__(self, results_path: str):
        self.results_path = Path(results_path)
        self.df = pd.read_csv(self.results_path / "filtering_results.csv")
        self.df['rejection_reasons'] = self.df['rejection_reasons'].fillna('')
        
    def generate_summary_statistics(self) -> Dict:
        stats = {}
        
        stats['total_files'] = int(len(self.df))
        stats['accepted_files'] = int(self.df['is_accepted'].sum())
        stats['rejected_files'] = int(stats['total_files'] - stats['accepted_files'])
        stats['acceptance_rate'] = float(stats['accepted_files'] / stats['total_files'])
        
        stats['total_duration_hours'] = float(self.df['duration'].sum() / 3600)
        stats['accepted_duration_hours'] = float(self.df[self.df['is_accepted']]['duration'].sum() / 3600)
        stats['avg_duration_sec'] = float(self.df['duration'].mean())
        
        metrics = ['snr_db', 'silence_ratio', 'clipping_ratio', 'rms_energy', 
                  'dynamic_range_db', 'quality_score']
        
        stats['metrics'] = {}
        for metric in metrics:
            stats['metrics'][metric] = {
                'mean': float(self.df[metric].mean()),
                'median': float(self.df[metric].median()),
                'std': float(self.df[metric].std()),
                'min': float(self.df[metric].min()),
                'max': float(self.df[metric].max()),
            }
        
        rejection_reasons = []
        for reasons in self.df[~self.df['is_accepted']]['rejection_reasons']:
            if reasons:
                rejection_reasons.extend(reasons.split('; '))
        
        from collections import Counter
        reason_counts = Counter(rejection_reasons)
        stats['rejection_breakdown'] = {k: int(v) for k, v in reason_counts.items()}
        
        return stats
    
    def plot_quality_distributions(self, output_dir: str = None):
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Quality Metrics Distributions', fontsize=16, fontweight='bold')
        
        metrics = [
            ('snr_db', 'Signal-to-Noise Ratio (dB)'),
            ('silence_ratio', 'Silence Ratio'),
            ('clipping_ratio', 'Clipping Ratio'),
            ('rms_energy', 'RMS Energy'),
            ('dynamic_range_db', 'Dynamic Range (dB)'),
            ('quality_score', 'Overall Quality Score')
        ]
        
        for idx, (metric, title) in enumerate(metrics):
            ax = axes[idx // 3, idx % 3]
            
            accepted = self.df[self.df['is_accepted']][metric]
            rejected = self.df[~self.df['is_accepted']][metric]
            
            ax.hist(accepted, bins=30, alpha=0.6, label='Accepted', color='green', density=True)
            ax.hist(rejected, bins=30, alpha=0.6, label='Rejected', color='red', density=True)
            
            ax.set_xlabel(title)
            ax.set_ylabel('Density')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(Path(output_dir) / 'quality_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_rejection_reasons(self, output_dir: str = None):
        rejection_reasons = []
        for reasons in self.df[~self.df['is_accepted']]['rejection_reasons']:
            if reasons:
                rejection_reasons.extend([r.split(':')[0].strip() for r in reasons.split('; ')])
        
        from collections import Counter
        reason_counts = Counter(rejection_reasons)
        
        if not reason_counts:
            print("No rejections to plot")
            return
        
        plt.figure(figsize=(12, 6))
        reasons = list(reason_counts.keys())
        counts = list(reason_counts.values())
        
        colors = plt.cm.Set3(range(len(reasons)))
        bars = plt.bar(reasons, counts, color=colors)
        
        plt.xlabel('Rejection Reason', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.title('Breakdown of Rejection Reasons', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(Path(output_dir) / 'rejection_reasons.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_correlation_heatmap(self, output_dir: str = None):
        metrics = ['snr_db', 'silence_ratio', 'clipping_ratio', 'zero_crossing_rate',
                  'rms_energy', 'dynamic_range_db', 'quality_score']
        
        correlation_matrix = self.df[metrics].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Between Quality Metrics', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(Path(output_dir) / 'correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_quality_score_vs_acceptance(self, output_dir: str = None):
        plt.figure(figsize=(10, 6))
        
        accepted_scores = self.df[self.df['is_accepted']]['quality_score']
        rejected_scores = self.df[~self.df['is_accepted']]['quality_score']
        
        plt.hist(accepted_scores, bins=30, alpha=0.6, label='Accepted', color='green')
        plt.hist(rejected_scores, bins=30, alpha=0.6, label='Rejected', color='red')
        
        plt.axvline(accepted_scores.mean(), color='green', linestyle='--', 
                   label=f'Accepted Mean: {accepted_scores.mean():.2f}')
        plt.axvline(rejected_scores.mean(), color='red', linestyle='--',
                   label=f'Rejected Mean: {rejected_scores.mean():.2f}')
        
        plt.xlabel('Quality Score', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.title('Quality Score Distribution by Acceptance Status', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(Path(output_dir) / 'quality_score_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_duration_analysis(self, output_dir: str = None):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].hist(self.df[self.df['is_accepted']]['duration'], bins=30, 
                    alpha=0.6, label='Accepted', color='green')
        axes[0].hist(self.df[~self.df['is_accepted']]['duration'], bins=30,
                    alpha=0.6, label='Rejected', color='red')
        axes[0].set_xlabel('Duration (seconds)', fontsize=12)
        axes[0].set_ylabel('Count', fontsize=12)
        axes[0].set_title('Audio Duration Distribution', fontsize=12, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        duration_bins = pd.cut(self.df['duration'], bins=10)
        acceptance_by_duration = self.df.groupby(duration_bins)['is_accepted'].mean()
        
        axes[1].plot(range(len(acceptance_by_duration)), acceptance_by_duration.values, 
                    marker='o', linewidth=2, markersize=8, color='blue')
        axes[1].set_xlabel('Duration Bin', fontsize=12)
        axes[1].set_ylabel('Acceptance Rate', fontsize=12)
        axes[1].set_title('Acceptance Rate by Duration', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim([0, 1.05])
        
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(Path(output_dir) / 'duration_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self, output_dir: str):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("Generating analysis report...")
        
        stats = self.generate_summary_statistics()
        
        print("Creating visualizations...")
        self.plot_quality_distributions(output_dir)
        self.plot_rejection_reasons(output_dir)
        self.plot_correlation_heatmap(output_dir)
        self.plot_quality_score_vs_acceptance(output_dir)
        self.plot_duration_analysis(output_dir)
        
        self._generate_text_report(stats, output_path)
        
        print(f"\nAnalysis complete. Report saved to {output_dir}/")
    
    def _generate_text_report(self, stats: Dict, output_path: Path):
        report = []
        report.append("="*70)
        report.append("AUDIO FILTERING PIPELINE - ANALYSIS REPORT")
        report.append("="*70)
        report.append("")
        
        report.append("OVERVIEW")
        report.append("-"*70)
        report.append(f"Total Files Processed:    {stats['total_files']:,}")
        report.append(f"Accepted Files:           {stats['accepted_files']:,} ({stats['acceptance_rate']:.1%})")
        report.append(f"Rejected Files:           {stats['rejected_files']:,} ({1-stats['acceptance_rate']:.1%})")
        report.append(f"Total Duration:           {stats['total_duration_hours']:.2f} hours")
        report.append(f"Accepted Duration:        {stats['accepted_duration_hours']:.2f} hours")
        report.append(f"Average Duration:         {stats['avg_duration_sec']:.2f} seconds")
        report.append("")
        
        report.append("QUALITY METRICS STATISTICS")
        report.append("-"*70)
        for metric, values in stats['metrics'].items():
            report.append(f"\n{metric.upper().replace('_', ' ')}:")
            report.append(f"  Mean:   {values['mean']:.4f}")
            report.append(f"  Median: {values['median']:.4f}")
            report.append(f"  Std:    {values['std']:.4f}")
            report.append(f"  Range:  [{values['min']:.4f}, {values['max']:.4f}]")
        report.append("")
        
        report.append("REJECTION REASONS BREAKDOWN")
        report.append("-"*70)
        for reason, count in sorted(stats['rejection_breakdown'].items(), 
                                   key=lambda x: x[1], reverse=True):
            percentage = count / stats['rejected_files'] * 100
            report.append(f"  {reason:.<50} {count:>5} ({percentage:>5.1f}%)")
        report.append("")
        report.append("="*70)
        
        with open(output_path / 'analysis_report.txt', 'w') as f:
            f.write('\n'.join(report))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze filtering results')
    parser.add_argument('results_dir', type=str, help='Directory with filtering results')
    parser.add_argument('--output-dir', type=str, default=None, 
                       help='Output directory for analysis')
    
    args = parser.parse_args()
    
    output_dir = args.output_dir or args.results_dir
    
    analyzer = ResultsAnalyzer(args.results_dir)
    analyzer.generate_report(output_dir)


if __name__ == "__main__":
    main()
