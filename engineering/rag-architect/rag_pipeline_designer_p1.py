# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402
from rag_pipeline_designer_p0 import load_requirements, print_design_summary, save_design  # noqa: F401,E501


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='Design RAG pipeline based on requirements')
    parser.add_argument('requirements', help='JSON file containing system requirements')
    parser.add_argument('--output', '-o', help='Output file for pipeline design (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        # Load requirements
        print("Loading requirements...")
        requirements = load_requirements(args.requirements)
        
        # Design pipeline
        designer = RAGPipelineDesigner()
        design = designer.design_pipeline(requirements)
        
        # Save design
        if args.output:
            save_design(design, args.output)
            print(f"Pipeline design saved to {args.output}")
        
        # Print summary
        print_design_summary(design)
        
        if args.verbose:
            print(f"\n📋 Configuration Templates:")
            for component_type, config in design.config_templates.items():
                print(f"\n  {component_type.upper()}:")
                print(f"    {json.dumps(config, indent=4)}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0
