import numpy as np
import pandas as pd

def run_quantum_scaling():
    print("Phase 40: Quantum-Derivative Scaling & Interaction Audit")
    df = pd.read_csv("data/standardized_cosmos_v2.csv").dropna(subset=['r_kpc', 'v_obs', 'v_disk'])
    
    # Fundamental Quantum Units (2.8349 eV)
    m_boson = 2.8349 
    h_bar = 1.0 # Natural units for the audit
    cs_basal = 80.0
    
    results = []
    for name, group in df.groupby('galaxy'):
        if len(group) < 10: continue
        group = group.sort_values('r_kpc')
        
        # Calculate Potential Curvature (The Scaling Trigger)
        dr = np.gradient(group['r_kpc'])
        dv = np.gradient(group['v_obs'])
        potential_gradient = dv / dr
        
        # 1. Effective Mass Scaling (m*)
        # m* increases in high-gradient (HSB) environments
        m_eff = m_boson * (1.0 + 0.05 * np.abs(potential_gradient))
        
        # 2. Quantum Reynolds Scaling (Req)
        # Low Req = Laminar (LSB); High Req = Turbulent (HSB)
        re_q = (group['v_obs'] * group['r_kpc'] * m_eff) / h_bar
        
        # 3. Corrected Interaction Lift
        # Lift is suppressed as Req enters the Turbulent Breach (Re_q > Threshold)
        scaling_impact = 1.0 / (1.0 + (re_q / re_q.mean())**0.5)
        
        # Apply Scaling to the 80 km/s interaction
        g_bar = (group['v_gas']**2 + 0.5*group['v_disk']**2) / group['r_kpc']
        g_usdm = (cs_basal**2 / (group['r_kpc'] + 0.1)) * scaling_impact * 0.15
        
        prediction = g_bar + g_usdm
        resid = np.sqrt(np.mean((np.log10(group['v_obs']**2 / group['r_kpc']) - np.log10(prediction))**2))
        
        results.append({'galaxy': name, 'mean_req': re_q.mean(), 'mean_meff': m_eff.mean(), 'resid': resid})

    final_df = pd.DataFrame(results)
    print("\n[ QUANTUM-DERIVATIVE SCORECARD ]")
    print(f"Mean Quantum Reynolds (Re_q): {final_df['mean_req'].mean():.2f}")
    print(f"Mean Effective Mass Shift:    {((final_df['mean_meff'].mean()/m_boson)-1)*100:.2f}%")
    print(f"Residual with Scaling:        {final_df['resid'].mean():.6f}")

if __name__ == '__main__':
    run_quantum_scaling()
