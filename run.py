#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import json
from src.ethbmc import EthBMC
from src.benchmark_downloader import BenchmarkDownloader

def main():
    # Check if we have enough benchmarks
    benchmark_dir = Path("benchmarks")
    if not benchmark_dir.exists() or len(list(benchmark_dir.glob("*.sol"))) < 100:
        print("Downloading benchmark contracts...")
        downloader = BenchmarkDownloader()
        downloaded = downloader.download_benchmarks(100)
        if downloaded < 100:
            print("Failed to download required number of benchmarks")
            sys.exit(1)
    
    # Initialize the model checker
    checker = EthBMC(max_depth=5)
    
    # Run analysis
    print("\nAnalyzing contracts...")
    results = checker.analyze_benchmarks()
    
    # Compute metrics
    metrics = checker.compute_metrics(results)
    
    # Save results
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    results.to_csv(results_dir / "analysis_results.csv")
    with open(results_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"Total contracts analyzed: {len(results)}")
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"F-measure: {metrics['f_measure']:.2f}")

if __name__ == "__main__":
    main()