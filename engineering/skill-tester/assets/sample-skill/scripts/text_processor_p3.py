# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from text_processor_base import *  # noqa: F403,E402
# fmt: off
from text_processor_p1 import OutputFormatter, TextProcessor  # noqa: E402,E501
from text_processor_p2 import FileManager  # noqa: E402,E501
# fmt: on


def batch_command(args: argparse.Namespace) -> int:
    """Handle batch command"""
    try:
        processor = TextProcessor(args.encoding)
        file_manager = FileManager(args.verbose)
        
        file_manager.log_verbose(f"Finding text files in: {args.directory}")
        
        # Find all text files
        text_files = file_manager.find_text_files(args.directory)
        
        if not text_files:
            print(f"No text files found in directory: {args.directory}", file=sys.stderr)
            return 1
            
        file_manager.log_verbose(f"Found {len(text_files)} text files")
        
        # Process all files
        all_results = []
        for i, file_path in enumerate(text_files, 1):
            try:
                file_manager.log_verbose(f"Processing {i}/{len(text_files)}: {file_path}")
                results = processor.process_file(file_path)
                all_results.append(results)
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}", file=sys.stderr)
                continue
                
        if not all_results:
            print("Error: No files could be processed successfully", file=sys.stderr)
            return 1
            
        # Format batch results
        batch_summary = {
            'total_files': len(all_results),
            'total_words': sum(r.get('total_words', 0) for r in all_results),
            'total_characters': sum(r.get('total_characters', 0) for r in all_results),
            'files': all_results
        }
        
        if args.format == 'json':
            output = OutputFormatter.format_json(batch_summary)
        else:
            lines = []
            lines.append("=== BATCH PROCESSING RESULTS ===")
            lines.append(f"Total files processed: {batch_summary['total_files']}")
            lines.append(f"Total words across all files: {batch_summary['total_words']}")
            lines.append(f"Total characters across all files: {batch_summary['total_characters']}")
            lines.append("")
            lines.append("Individual file results:")
            for result in all_results:
                lines.append(f"  {result['file']}: {result['total_words']} words")
            output = "\n".join(lines)
            
        # Write output
        file_manager.write_output(output, args.output)
        
        return 0
        
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
