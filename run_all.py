#!/usr/bin/env python3
"""
MIT Coding Challenge — Master Runner Script
============================================
Executes all analyses from start to finish without manual intervention.

Usage:
    python run_all.py

This script runs all Task 1–4 analyses in the correct dependency order,
generating all tables, figures, and outputs in the Output/ directory.

Author: Trenton Eugene O'Bannon
"""

import subprocess
import sys
import os
import time
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Base directory (where this script lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# Scripts to run in order (dependency-sorted)
SCRIPTS = [
    # ─────────────────────────────────────────────────────────────────────────
    # TASK 1: Data Preparation & Visualization
    # ─────────────────────────────────────────────────────────────────────────
    ("task1_data_preparation.py", "Task 1: Data Preparation — merge MPS shocks, FX, and yields"),
    ("task1_visualizations.py", "Task 1: Visualizations — summary statistics figures"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # TASK 2: Event-Study Regressions
    # ─────────────────────────────────────────────────────────────────────────
    ("task2_regressions.py", "Task 2: Event-Study Regressions — FX and yield responses"),
    ("task2_placebo.py", "Task 2: Placebo Test — falsification with lead shock"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # TASK 3: Panel Regression with NFA Interaction
    # ─────────────────────────────────────────────────────────────────────────
    ("task3_panel_regression.py", "Task 3: Panel Regression — NFA × monetary policy interaction"),
    
    # ─────────────────────────────────────────────────────────────────────────
    # TASK 4: Time Variation & Extensions
    # ─────────────────────────────────────────────────────────────────────────
    ("task4_time_variation.py", "Task 4: Time Variation — post-GFC regime analysis"),
    ("task4b_vix_stress.py", "Task 4b: VIX Stress — high-volatility regime interaction"),
]

# Optional validation/diagnostic scripts (run after main analyses)
VALIDATION_SCRIPTS = [
    ("check_fx_convention.py", "Validation: FX convention check"),
    ("check_pc_column.py", "Validation: PC column check"),
    ("sanity_check_scaling.py", "Validation: Scaling sanity check"),
    ("check_task2.py", "Validation: Task 2 results check"),
]

# Additional analysis scripts (supplementary)
ADDITIONAL_SCRIPTS = [
    ("analyze_surprises.py", "Additional: Analyze monetary policy surprises"),
    ("compare_surprise_measures.py", "Additional: Compare STMT vs MP1 vs MP2"),
    ("final_measure_recommendation.py", "Additional: Final measure recommendation"),
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header():
    """Print script header"""
    print("\n" + "═" * 80)
    print("MIT CODING CHALLENGE — MASTER RUNNER")
    print("═" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {BASE_DIR}")
    print("═" * 80)


def print_section(title):
    """Print section header"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def run_script(script_name, description, script_num, total_scripts):
    """
    Run a Python script and handle errors.
    
    Args:
        script_name: Name of the Python script to run
        description: Human-readable description of what the script does
        script_num: Current script number (for progress tracking)
        total_scripts: Total number of scripts to run
    
    Returns:
        Tuple of (success: bool, elapsed_time: float)
    """
    print(f"\n[{script_num}/{total_scripts}] {description}")
    print(f"         Script: {script_name}")
    
    # Check if script exists
    if not os.path.exists(script_name):
        print(f"         ⚠️  WARNING: {script_name} not found, skipping...")
        return True, 0.0
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            cwd=BASE_DIR
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode != 0:
            print(f"         ❌ FAILED (exit code {result.returncode}) after {elapsed:.1f}s")
            return False, elapsed
        
        print(f"         ✓ Completed in {elapsed:.1f}s")
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"         ❌ ERROR: {e}")
        return False, elapsed


def run_script_group(scripts, group_name, start_num=1):
    """
    Run a group of scripts.
    
    Args:
        scripts: List of (script_name, description) tuples
        group_name: Name of this script group
        start_num: Starting script number for progress tracking
    
    Returns:
        Tuple of (all_success: bool, total_time: float, scripts_run: int)
    """
    print_section(group_name)
    
    total = len(scripts)
    all_success = True
    total_time = 0.0
    scripts_run = 0
    
    for i, (script, desc) in enumerate(scripts, 1):
        success, elapsed = run_script(script, desc, start_num + i - 1, start_num + total - 1)
        total_time += elapsed
        scripts_run += 1
        
        if not success:
            all_success = False
            print(f"\n❌ STOPPING: {script} failed. Fix errors and re-run.")
            break
    
    return all_success, total_time, scripts_run


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all analysis scripts in order"""
    
    print_header()
    
    total_scripts = len(SCRIPTS) + len(VALIDATION_SCRIPTS) + len(ADDITIONAL_SCRIPTS)
    print(f"Total scripts to run: {total_scripts}")
    
    overall_start = time.time()
    scripts_completed = 0
    
    # ── Run main analysis scripts ──
    success, elapsed, count = run_script_group(SCRIPTS, "MAIN ANALYSES (Required)", 1)
    scripts_completed += count
    
    if not success:
        print(f"\n{'═' * 80}")
        print("❌ EXECUTION FAILED")
        print(f"   Completed {scripts_completed} of {total_scripts} scripts")
        print(f"   Total time: {time.time() - overall_start:.1f}s")
        print(f"{'═' * 80}\n")
        sys.exit(1)
    
    # ── Run validation scripts ──
    success, elapsed, count = run_script_group(
        VALIDATION_SCRIPTS, 
        "VALIDATION SCRIPTS (Diagnostics)", 
        len(SCRIPTS) + 1
    )
    scripts_completed += count
    
    if not success:
        print("\n⚠️  Some validation scripts failed, but continuing...")
    
    # ── Run additional analysis scripts ──
    success, elapsed, count = run_script_group(
        ADDITIONAL_SCRIPTS, 
        "ADDITIONAL ANALYSES (Supplementary)", 
        len(SCRIPTS) + len(VALIDATION_SCRIPTS) + 1
    )
    scripts_completed += count
    
    # ── Summary ──
    total_time = time.time() - overall_start
    
    print(f"\n{'═' * 80}")
    print("✓ ALL ANALYSES COMPLETED SUCCESSFULLY!")
    print(f"{'═' * 80}")
    print(f"  Scripts run:    {scripts_completed}")
    print(f"  Total time:     {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"  End time:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nOutputs saved to: {os.path.join(BASE_DIR, 'Output')}/")
    print(f"{'═' * 80}\n")
    
    # List key output files
    output_dir = os.path.join(BASE_DIR, 'Output')
    if os.path.exists(output_dir):
        files = sorted(os.listdir(output_dir))
        tables = [f for f in files if f.endswith('.tex')]
        figures = [f for f in files if f.endswith('.png')]
        csvs = [f for f in files if f.endswith('.csv')]
        
        print("KEY OUTPUTS:")
        print(f"  LaTeX tables:  {len(tables)}")
        for t in tables:
            print(f"    • {t}")
        print(f"  Figures:       {len(figures)}")
        for f in figures:
            print(f"    • {f}")
        print(f"  Data files:    {len(csvs)}")
        print()


if __name__ == "__main__":
    main()
