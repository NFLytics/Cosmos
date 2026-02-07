"""
Hardware Monitoring for GPU Compute Nodes
Mimics Nexus.Platform methodology for VRAM safety.
"""

import subprocess
import logging
import re

logger = logging.getLogger(__name__)

class HardwareMonitor:
    """Monitor system vitals for GPU compute safety"""
    
    @staticmethod
    def get_vram_usage():
        """
        Query NVIDIA GPU memory usage.
        
        Returns:
            Tuple of (used_mb, total_mb) or (0, 0) if failed
        """
        try:
            cmd = ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"]
            result = subprocess.check_output(cmd).decode('utf-8').strip()
            parts = result.split(',')
            if len(parts) == 2:
                return float(parts[0]), float(parts[1])
        except Exception as e:
            logger.warning(f"Failed to query VRAM via nvidia-smi: {e}")
        return 0.0, 0.0

    @staticmethod
    def check_vram_limit(threshold_gb=7.8):
        """
        Ensure VRAM usage is below threshold.
        
        Args:
            threshold_gb: VRAM threshold in GB
            
        Returns:
            True if safe, False if close to limit
        """
        used, total = HardwareMonitor.get_vram_usage()
        if total == 0:
            return True # Assume safe if no GPU detected
            
        used_gb = used / 1024.0
        if used_gb > threshold_gb:
            logger.warning(f"VRAM CRITICAL: {used_gb:.2f}GB / {total/1024.0:.2f}GB")
            return False
        return True

    @staticmethod
    def get_gpu_name():
        """Get GPU model name"""
        try:
            cmd = ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]
            return subprocess.check_output(cmd).decode('utf-8').strip()
        except:
            return "Unknown GPU"
