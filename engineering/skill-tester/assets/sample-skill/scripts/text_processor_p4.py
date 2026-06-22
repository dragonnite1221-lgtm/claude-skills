# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from text_processor_base import *  # noqa: F403,E402
# fmt: off
from text_processor_p2 import analyze_command, transform_command  # noqa: E402,E501
from text_processor_p3 import batch_command  # noqa: E402,E501
# fmt: on


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Sample Text Processor - Basic text analysis and transformation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Analysis:
    python text_processor.py analyze document.txt
    python text_processor.py analyze document.txt --format json --output results.json
  
  Transformation:
    python text_processor.py transform document.txt --mode upper
    python text_processor.py transform document.txt --mode title --output transformed.txt
  
  Batch processing:
    python text_processor.py batch text_files/ --verbose
    python text_processor.py batch text_files/ --format json --output batch_results.json

Transformation modes:
  upper   - Convert to uppercase
  lower   - Convert to lowercase  
  title   - Convert to title case
  reverse - Reverse the text
        """
    )
    
    parser.add_argument('--format', 
                       choices=['json', 'text'], 
                       default='text',
                       help='Output format (default: text)')
    parser.add_argument('--output', 
                       help='Output file path (default: stdout)')
    parser.add_argument('--encoding', 
                       default='utf-8',
                       help='Text file encoding (default: utf-8)')
    parser.add_argument('--verbose', 
                       action='store_true',
                       help='Enable verbose output')
                       
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze subcommand
    analyze_parser = subparsers.add_parser('analyze', help='Analyze text file statistics')
    analyze_parser.add_argument('file', help='Text file to analyze')
    
    # Transform subcommand  
    transform_parser = subparsers.add_parser('transform', help='Transform text file')
    transform_parser.add_argument('file', help='Text file to transform')
    transform_parser.add_argument('--mode', 
                                 required=True,
                                 choices=['upper', 'lower', 'title', 'reverse'],
                                 help='Transformation mode')
    
    # Batch subcommand
    batch_parser = subparsers.add_parser('batch', help='Process multiple files')
    batch_parser.add_argument('directory', help='Directory containing text files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'analyze':
            return analyze_command(args)
        elif args.command == 'transform':
            return transform_command(args)
        elif args.command == 'batch':
            return batch_command(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
