#!/usr/bin/env python3
"""Build baseline data for NFL GPP Simulator"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Create baseline data directory and files"""
    print("Building baseline data...")
    
    # Create data directories
    data_dir = Path(__file__).parent.parent / "data"
    baseline_dir = data_dir / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    
    # Create placeholder file
    placeholder = baseline_dir / "README.txt"
    placeholder.write_text("Baseline data directory for NFL GPP Simulator\n")
    
    print(f"Created baseline directory at: {baseline_dir}")
    print("Baseline data ready!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
