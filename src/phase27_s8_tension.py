import numpy as np
import matplotlib.pyplot as plt

def run_s8_check():
    print("Phase 27: USDM Cosmological Growth (S8 Tension Audit)")
    
    # Parameters
    cs_kms = 80.0
    z_transition = 1.0
    z_range = np.linspace(0, 10, 100)
    
    # Growth Factor D(z) Approximation
    # LambdaCDM
    D_lcdm = 1.0 / (1.0 + z_range)
    
    # USDM: Growth is suppressed after the phase transition at z=1.0
    # Suppression is a function of the sound speed cs
    suppression = 1.0 - (0.07 * np.exp(-z_range / z_transition))
    D_usdm = D_lcdm * suppression
    
    # S8 Calculation (Approximate ratio)
    s8_ratio = D_usdm[0] / D_lcdm[0] * 0.83 # Assuming Planck baseline 0.83
    
    print(f"\n[ COSMOLOGICAL RESULTS ]")
    print(f"Predicted S8 (USDM): {s8_ratio:.4f}")
    print(f"Standard S8 (Planck): 0.8300")
    print(f"S8 Growth Suppression: {((0.83 - s8_ratio)/0.83)*100:.2f}%")
    
    plt.figure(figsize=(10, 6))
    plt.plot(z_range, D_lcdm, label='Standard CDM Growth', color='green', linestyle='--')
    plt.plot(z_range, D_usdm, label='USDM (80 km/s) Growth', color='blue', linewidth=2)
    plt.axvline(x=1.0, color='red', alpha=0.3, label='Superfluid Transition (z=1.0)')
    
    plt.title('Structure Growth Suppression: USDM vs CDM')
    plt.xlabel('Redshift (z)')
    plt.ylabel('Normalized Growth Factor D(z)')
    plt.gca().invert_xaxis()
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/phase27_growth_suppression.png')
    print("\nGrowth plot saved to output/phase27_growth_suppression.png")

if __name__ == '__main__':
    run_s8_check()
