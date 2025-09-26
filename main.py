#!/usr/bin/env python3
"""
Main entry point for the Logistics Analytics Q&A Tool
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def run_cli():
    """Run the CLI interface"""
    from src.cli.main import main
    main()


def run_web():
    """Run the web interface"""
    from src.web.app import app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Starting web interface on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


def run_demo():
    """Run the demo script"""
    from src.demo.demo_script import main
    main()


def run_pipeline():
    """Run the data pipeline"""
    from run_pipeline import main
    main()


def generate_data():
    """Generate demo data"""
    from src.demo.data_generator import main
    main()


def main():
    """Main entry point with command selection"""
    parser = argparse.ArgumentParser(
        description='Logistics Analytics Q&A Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py cli                    # Start CLI interface
  python main.py web                    # Start web interface  
  python main.py demo                   # Run demo script
  python main.py pipeline               # Run data pipeline
  python main.py generate-data          # Generate demo data
        """
    )
    
    parser.add_argument(
        'command',
        choices=['cli', 'web', 'demo', 'pipeline', 'generate-data'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for web interface (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode for web interface'
    )
    
    args = parser.parse_args()
    
    # Set environment variables for web interface
    if args.command == 'web':
        os.environ['PORT'] = str(args.port)
        if args.debug:
            os.environ['FLASK_DEBUG'] = 'True'
    
    # Route to appropriate function
    commands = {
        'cli': run_cli,
        'web': run_web,
        'demo': run_demo,
        'pipeline': run_pipeline,
        'generate-data': generate_data
    }
    
    try:
        print(f"🚚 Logistics Analytics Q&A Tool")
        print(f"Running: {args.command}")
        print("-" * 50)
        
        commands[args.command]()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
