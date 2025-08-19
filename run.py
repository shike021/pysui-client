#!/usr/bin/env python3
"""
Pysui Client Launcher Script

This script provides an easy way to launch the pysui client with different modes.
"""

import sys
import argparse
from pathlib import Path

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='Pysui Client Launcher')
    parser.add_argument('mode', nargs='?', default='interactive', 
                       choices=['interactive', 'test', 'demo', 'verify'],
                       help='Launch mode (default: interactive)')
    
    args = parser.parse_args()
    
    # Add current directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        if args.mode == 'interactive':
            from quick_start import main as quick_main
            print("🌊 Starting Pysui Client Interactive Mode...")
            quick_main()
        elif args.mode == 'test':
            from test_client import main as test_main
            print("🧪 Running Basic Tests...")
            test_main()
        elif args.mode == 'demo':
            from 功能演示 import main as demo_main
            print("🎯 Running Feature Demo...")
            demo_main()
        elif args.mode == 'verify':
            from verify_json_rpc_offline import main as verify_main
            print("🔍 Verifying JSON-RPC Usage...")
            verify_main()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
