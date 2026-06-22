# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from text_processor_base import *  # noqa: F403,E402
# fmt: off
from text_processor_p1 import OutputFormatter, TextProcessor  # noqa: E402,E501
# fmt: on


class FileManager:
    """Manages file I/O operations and batch processing"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        
    def log_verbose(self, message: str):
        """Log verbose message if verbose mode enabled"""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)
            
    def find_text_files(self, directory: str) -> List[str]:
        """Find all text files in directory"""
        text_extensions = {'.txt', '.md', '.rst', '.csv', '.log'}
        text_files = []
        
        try:
            for file_path in Path(directory).rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                    text_files.append(str(file_path))
                    
        except PermissionError:
            raise PermissionError(f"Permission denied accessing directory: {directory}")
            
        return text_files
        
    def write_output(self, content: str, output_path: Optional[str] = None):
        """Write content to file or stdout"""
        if output_path:
            try:
                # Create directory if needed
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
                self.log_verbose(f"Output written to: {output_path}")
                
            except PermissionError:
                raise PermissionError(f"Permission denied writing to: {output_path}")
        else:
            print(content)
def analyze_command(args: argparse.Namespace) -> int:
    """Handle analyze command"""
    try:
        processor = TextProcessor(args.encoding)
        file_manager = FileManager(args.verbose)
        
        file_manager.log_verbose(f"Analyzing file: {args.file}")
        
        # Process the file
        results = processor.process_file(args.file)
        
        # Format output
        if args.format == 'json':
            output = OutputFormatter.format_json(results)
        else:
            output = OutputFormatter.format_human_readable(results)
            
        # Write output
        file_manager.write_output(output, args.output)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"Try using --encoding option with different encoding", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
def transform_command(args: argparse.Namespace) -> int:
    """Handle transform command"""
    try:
        processor = TextProcessor(args.encoding)
        file_manager = FileManager(args.verbose)
        
        file_manager.log_verbose(f"Transforming file: {args.file}")
        
        # Read and transform the file
        with open(args.file, 'r', encoding=args.encoding) as file:
            content = file.read()
            
        transformed = processor.transform_text(content, args.mode)
        
        # Write transformed content
        file_manager.write_output(transformed, args.output)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
