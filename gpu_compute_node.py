"""
NEXUS COMPUTE NODE - Cosmological Analytics (Phase 1B)
Standalone worker for high-throughput ONNX-CUDA processing.
"""

import os
import sys
import logging
import time
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.onnx_engine import ONNXComputeEngine
from src.hardware_monitor import HardwareMonitor
from src.sparc_loader_v2 import SPARCRotationCurvesV2
from src.radial_analysis_v2 import RadialDependenceAnalyzerV2

logging.basicConfig(level=logging.INFO, format='[NODE] %(message)s')
logger = logging.getLogger(__name__)

def listen_for_interop():
    """Optional: Basic named pipe listener simulation for Nexus Interop"""
    pipe_path = r'\\.\pipe\NexusCosmoNode'
    logger.info(f"Interop: Listening on {pipe_path} (Simulation mode)")
    # In a real scenario, we would use win32pipe here.
    # For now, we proceed to direct execution.

def run_node():
    logger.info("Initializing Nexus Compute Node...")
    listen_for_interop()
    
    # 1. AUDIT: Hardware and VRAM Check
    gpu_name = HardwareMonitor.get_gpu_name()
    used, total = HardwareMonitor.get_vram_usage()
    logger.info(f"Hardware: {gpu_name} | VRAM: {used:.0f}MB / {total:.0f}MB")
    
    if not HardwareMonitor.check_vram_limit():
        logger.error("Insufficient VRAM for optimal compute. Aborting.")
        return

    # 2. LOAD: High-efficiency data ingestion
    logger.info("Loading SPARC ensemble data...")
    try:
        sparc = SPARCRotationCurvesV2("data/raw_sparc", strictness="relaxed")
        quality_galaxies = sparc.get_quality_galaxies()
        logger.info(f"Loaded {len(quality_galaxies)} quality galaxies.")
    except Exception as e:
        logger.error(f"Load failed: {e}")
        return

    # 3. PROCESS: Proper ONNX-CUDA Compute
    logger.info("Engaging ONNX-CUDA Engine...")
    engine = ONNXComputeEngine()
    analyzer = RadialDependenceAnalyzerV2(use_gpu=True)
    
    start_time = time.time()
    results = []
    
    # Efficient process loop
    for i, gal_name in enumerate(quality_galaxies):
        gal_data = sparc.extract_galaxy_profile(gal_name)
        if gal_data is not None:
            # Inject ONNX engine into analyzer's fitter if not already there
            analyzer.fitter.engine = engine
            
            res = analyzer.analyze_galaxy(gal_data, gal_name)
            if res and 'scale_dependence' in res:
                results.append(res)
        
        # Periodic VRAM check (Nexus pattern)
        if i % 20 == 0:
            u, _ = HardwareMonitor.get_vram_usage()
            logger.info(f"Processing: {i}/{len(quality_galaxies)} | VRAM: {u:.0f}MB")

    elapsed = time.time() - start_time
    logger.info(f"Process complete. Total time: {elapsed:.2f}s ({elapsed/len(results):.3f}s/gal)")

    # 4. OUTPUT: Structured result emission
    output_path = Path("output/gpu_node_results.csv")
    output_path.parent.mkdir(exist_ok=True)
    
    # Flatten results for CSV
    flattened = []
    for r in results:
        sd = r['scale_dependence']
        if sd.get('success'):
            flattened.append({
                'galaxy': r['galaxy'],
                'morphology': r['morphology'],
                'ratio': sd['ratio'],
                'z_score': sd['z_score'],
                'vram_at_end': HardwareMonitor.get_vram_usage()[0]
            })
    
    df = pd.DataFrame(flattened)
    df.to_csv(output_path, index=False)
    logger.info(f"Verification: Results persisted to {output_path}")
    logger.info(f"Mean Ensemble Ratio: {df['ratio'].mean():.4f}")

if __name__ == "__main__":
    run_node()
