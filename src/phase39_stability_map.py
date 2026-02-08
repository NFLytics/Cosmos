import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_stability_map():
    print("Phase 39: Unified Phase-Space Stability Mapping")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Define the 'Stability Index' based on the CS=80 limit
    # Index = (v_obs / 80.0)
    df['stability_index'] = df['v_obs'] / 80.0
    
    plt.figure(figsize=(10, 6))
    plt.scatter(df['r_kpc'], df['stability_index'], c=df['v_obs'], cmap='viridis', alpha=0.5)
    plt.axhline(y=1.0, color='red', linestyle='--', label='Acoustic Horizon (80 km/s)')
    
    plt.title('USDM Phase-Space: Acoustic Stability Map')
    plt.xlabel('Radius (kpc)')
    plt.ylabel('Stability Index (V_obs / C_s)')
    plt.colorbar(label='V_obs (km/s)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('output/phase39_stability_map.png')
    print("\n[ STABILITY AUDIT ]")
    print(f"Systems exceeding Acoustic Horizon: {len(df[df['stability_index'] > 1.0])} points")
    print("Stability Map saved to output/phase39_stability_map.png")

if __name__ == '__main__':
    run_stability_map()
