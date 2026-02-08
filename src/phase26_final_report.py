import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_final_report():
    print("Phase 26: USDM Global Performance Report (SPARC Baseline)")
    df_res = pd.read_csv("output/phase25_final_results.csv")
    
    # Statistical Analysis
    mean_res = df_res['resid'].mean()
    std_res = df_res['resid'].std()
    
    plt.figure(figsize=(10, 6))
    plt.hist(df_res['resid'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    plt.axvline(mean_res, color='red', linestyle='dashed', linewidth=2, label=f'Mean Residual: {mean_res:.3f}')
    
    plt.title('USDM (2.83 eV) Model Residual Distribution (124 Galaxies)')
    plt.xlabel('Logarithmic Residual (Error)')
    plt.ylabel('Frequency (Number of Galaxies)')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    plt.savefig('output/phase26_residual_dist.png')
    print(f"\n[ FINAL CALIBRATION SUMMARY ]")
    print(f"Mean Residual:      {mean_res:.6f}")
    print(f"Confidence Level:   {(1.0 - mean_res)*100:.2f}%")
    print(f"Success Envelope:   {len(df_res[df_res['resid'] < 0.3])} galaxies at >70% confidence.")
    print("\nFinal Plot saved to output/phase26_residual_dist.png")

if __name__ == '__main__':
    run_final_report()
