import yaml
from pathlib import Path

def load_config(config_path: str = 'config/analysis_config.yaml'):
    """Load analysis configuration."""
    if not Path(config_path).exists():
        # Try relative to project root if called from src
        alt_path = Path(__file__).parent.parent / config_path
        if alt_path.exists():
            config_path = str(alt_path)
            
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config
