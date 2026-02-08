#!/usr/bin/env python3
"""
plot_results.py

Optional visualization module for DWSIM parametric sweep results.
Creates plots showing trends in KPIs vs. sweep variables for both
PFR and distillation column simulations.
"""

import argparse
import csv
import os
import sys
from typing import Dict, List

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for headless execution
except ImportError:
    print("Error: matplotlib is required for plotting. Install with: pip install matplotlib")
    sys.exit(1)


def load_results(csv_path: str) -> List[Dict]:
    """Load results from CSV file."""
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for key in row:
                if key not in ['case_id', 'model', 'status', 'message', 'sweep_var_1', 'sweep_var_2']:
                    try:
                        row[key] = float(row[key])
                    except (ValueError, TypeError):
                        pass
            results.append(row)
    return results


def filter_successful(results: List[Dict], model: str) -> List[Dict]:
    """Filter for successful cases of a specific model."""
    return [r for r in results if r['model'] == model and r['status'] == 'OK']


def plot_pfr_results(results: List[Dict], output_dir: str):
    """Create plots for PFR parametric sweep results."""
    pfr_results = filter_successful(results, 'PFR')
    
    if not pfr_results:
        print("No successful PFR results to plot.")
        return
    
    # Extract unique values for each sweep variable
    volumes = sorted(list(set([r['sweep_val_1'] for r in pfr_results])))
    temps = sorted(list(set([r['sweep_val_2'] for r in pfr_results])))
    
    # Organize data for plotting
    data_by_volume = {}
    for vol in volumes:
        data_by_volume[vol] = {
            'temps': [],
            'conversion': [],
            'outlet_b': [],
            'duty': []
        }
        
        for r in pfr_results:
            if r['sweep_val_1'] == vol:
                data_by_volume[vol]['temps'].append(r['sweep_val_2'])
                data_by_volume[vol]['conversion'].append(r['conversion'])
                data_by_volume[vol]['outlet_b'].append(r['outlet_b_mol_s'])
                data_by_volume[vol]['duty'].append(r['reactor_duty_kw'])
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('PFR Parametric Sweep Results', fontsize=16, fontweight='bold')
    
    # Plot 1: Conversion vs Temperature
    ax = axes[0, 0]
    for vol in volumes:
        data = data_by_volume[vol]
        ax.plot(data['temps'], data['conversion'], 'o-', label=f'V = {vol} m³', linewidth=2, markersize=8)
    ax.set_xlabel('Temperature (K)', fontsize=12)
    ax.set_ylabel('Conversion', fontsize=12)
    ax.set_title('Conversion vs Temperature', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Outlet B Flow vs Temperature
    ax = axes[0, 1]
    for vol in volumes:
        data = data_by_volume[vol]
        ax.plot(data['temps'], data['outlet_b'], 's-', label=f'V = {vol} m³', linewidth=2, markersize=8)
    ax.set_xlabel('Temperature (K)', fontsize=12)
    ax.set_ylabel('Outlet B Flow (mol/s)', fontsize=12)
    ax.set_title('Product B Flow vs Temperature', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Heat Duty vs Temperature
    ax = axes[1, 0]
    for vol in volumes:
        data = data_by_volume[vol]
        ax.plot(data['temps'], data['duty'], '^-', label=f'V = {vol} m³', linewidth=2, markersize=8)
    ax.set_xlabel('Temperature (K)', fontsize=12)
    ax.set_ylabel('Heat Duty (kW)', fontsize=12)
    ax.set_title('Heat Duty vs Temperature', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Conversion vs Volume (for different temperatures)
    ax = axes[1, 1]
    data_by_temp = {}
    for temp in temps:
        data_by_temp[temp] = {'volumes': [], 'conversion': []}
        for r in pfr_results:
            if r['sweep_val_2'] == temp:
                data_by_temp[temp]['volumes'].append(r['sweep_val_1'])
                data_by_temp[temp]['conversion'].append(r['conversion'])
    
    for temp in temps:
        data = data_by_temp[temp]
        ax.plot(data['volumes'], data['conversion'], 'o-', label=f'T = {temp} K', linewidth=2, markersize=8)
    ax.set_xlabel('Reactor Volume (m³)', fontsize=12)
    ax.set_ylabel('Conversion', fontsize=12)
    ax.set_title('Conversion vs Reactor Volume', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'pfr_parametric_sweep.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved PFR plot to {output_path}")
    plt.close()


def plot_column_results(results: List[Dict], output_dir: str):
    """Create plots for distillation column parametric sweep results."""
    col_results = filter_successful(results, 'COLUMN')
    
    if not col_results:
        print("No successful column results to plot.")
        return
    
    # Extract unique values for each sweep variable
    reflux_ratios = sorted(list(set([r['sweep_val_1'] for r in col_results])))
    stages_list = sorted(list(set([int(r['sweep_val_2']) for r in col_results])))
    
    # Organize data for plotting
    data_by_rr = {}
    for rr in reflux_ratios:
        data_by_rr[rr] = {
            'stages': [],
            'dist_purity': [],
            'bot_purity': [],
            'condenser_duty': [],
            'reboiler_duty': []
        }
        
        for r in col_results:
            if abs(r['sweep_val_1'] - rr) < 0.01:  # Float comparison with tolerance
                data_by_rr[rr]['stages'].append(int(r['sweep_val_2']))
                data_by_rr[rr]['dist_purity'].append(r['distillate_purity'])
                data_by_rr[rr]['bot_purity'].append(r['bottoms_purity'])
                data_by_rr[rr]['condenser_duty'].append(r['condenser_duty_kw'])
                data_by_rr[rr]['reboiler_duty'].append(r['reboiler_duty_kw'])
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Distillation Column Parametric Sweep Results', fontsize=16, fontweight='bold')
    
    # Plot 1: Distillate Purity vs Number of Stages
    ax = axes[0, 0]
    for rr in reflux_ratios:
        data = data_by_rr[rr]
        ax.plot(data['stages'], data['dist_purity'], 'o-', label=f'RR = {rr}', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Stages', fontsize=12)
    ax.set_ylabel('Distillate Purity (mole frac)', fontsize=12)
    ax.set_title('Distillate Purity vs Number of Stages', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Bottoms Purity vs Number of Stages
    ax = axes[0, 1]
    for rr in reflux_ratios:
        data = data_by_rr[rr]
        ax.plot(data['stages'], data['bot_purity'], 's-', label=f'RR = {rr}', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Stages', fontsize=12)
    ax.set_ylabel('Bottoms Purity (mole frac)', fontsize=12)
    ax.set_title('Bottoms Purity vs Number of Stages', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Condenser Duty vs Number of Stages
    ax = axes[1, 0]
    for rr in reflux_ratios:
        data = data_by_rr[rr]
        ax.plot(data['stages'], data['condenser_duty'], '^-', label=f'RR = {rr}', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Stages', fontsize=12)
    ax.set_ylabel('Condenser Duty (kW)', fontsize=12)
    ax.set_title('Condenser Duty vs Number of Stages', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Reboiler Duty vs Number of Stages
    ax = axes[1, 1]
    for rr in reflux_ratios:
        data = data_by_rr[rr]
        ax.plot(data['stages'], data['reboiler_duty'], 'd-', label=f'RR = {rr}', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Stages', fontsize=12)
    ax.set_ylabel('Reboiler Duty (kW)', fontsize=12)
    ax.set_title('Reboiler Duty vs Number of Stages', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'column_parametric_sweep.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved column plot to {output_path}")
    plt.close()


def plot_success_rate(results: List[Dict], output_dir: str):
    """Create a summary plot showing success rates."""
    pfr_total = len([r for r in results if r['model'] == 'PFR'])
    pfr_success = len([r for r in results if r['model'] == 'PFR' and r['status'] == 'OK'])
    col_total = len([r for r in results if r['model'] == 'COLUMN'])
    col_success = len([r for r in results if r['model'] == 'COLUMN' and r['status'] == 'OK'])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    models = ['PFR', 'Column']
    success_rates = [
        (pfr_success / pfr_total * 100) if pfr_total > 0 else 0,
        (col_success / col_total * 100) if col_total > 0 else 0
    ]
    
    bars = ax.bar(models, success_rates, color=['#2ecc71', '#3498db'], alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels on bars
    for i, (bar, rate) in enumerate(zip(bars, success_rates)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.1f}%\n({[pfr_success, col_success][i]}/{[pfr_total, col_total][i]})',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Simulation Success Rate by Model Type', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'success_rate.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved success rate plot to {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Plot DWSIM parametric sweep results')
    parser.add_argument('--input', default='results.csv', help='Input CSV file from run_screening.py')
    parser.add_argument('--output-dir', default='.', help='Output directory for plots')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load results
    print(f"Loading results from {args.input}...")
    results = load_results(args.input)
    print(f"Loaded {len(results)} cases")
    
    # Generate plots
    print("\nGenerating plots...")
    plot_pfr_results(results, args.output_dir)
    plot_column_results(results, args.output_dir)
    plot_success_rate(results, args.output_dir)
    
    print(f"\nAll plots saved to {args.output_dir}/")
    return 0


if __name__ == '__main__':
    sys.exit(main())
