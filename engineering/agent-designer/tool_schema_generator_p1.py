# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ToolDescription  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Tool Schema Generator for AI Agents")
    parser.add_argument("input_file", help="JSON file with tool descriptions")
    parser.add_argument("-o", "--output", help="Output file prefix (default: tool_schemas)")
    parser.add_argument("--format", choices=["json", "both"], default="both", 
                       help="Output format")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate generated schemas")
    
    args = parser.parse_args()
    
    try:
        # Load tool descriptions
        with open(args.input_file, 'r') as f:
            tools_data = json.load(f)
        
        # Parse tool descriptions
        tool_descriptions = []
        for tool_data in tools_data.get("tools", []):
            tool_desc = ToolDescription(**tool_data)
            tool_descriptions.append(tool_desc)
        
        # Generate schemas
        generator = ToolSchemaGenerator()
        schemas = []
        
        for description in tool_descriptions:
            schema = generator.generate_tool_schema(description)
            schemas.append(schema)
            print(f"Generated schema for: {schema.name}")
        
        # Prepare output
        output_data = {
            "tool_schemas": [asdict(schema) for schema in schemas],
            "metadata": {
                "generated_by": "tool_schema_generator.py",
                "input_file": args.input_file,
                "tool_count": len(schemas),
                "generation_timestamp": "2024-01-15T10:30:00Z",
                "schema_version": "1.0"
            },
            "validation_summary": {
                "total_tools": len(schemas),
                "total_parameters": sum(schema.metadata["input_parameters"] for schema in schemas),
                "total_validation_rules": sum(len(schema.validation_rules) for schema in schemas),
                "total_examples": sum(len(schema.examples) for schema in schemas)
            }
        }
        
        # Output files
        output_prefix = args.output or "tool_schemas"
        
        if args.format in ["json", "both"]:
            with open(f"{output_prefix}.json", 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"JSON output written to {output_prefix}.json")
        
        if args.format == "both":
            # Generate separate files for different formats
            
            # OpenAI format
            openai_schemas = {
                "functions": [schema.openai_schema for schema in schemas]
            }
            with open(f"{output_prefix}_openai.json", 'w') as f:
                json.dump(openai_schemas, f, indent=2)
            print(f"OpenAI schemas written to {output_prefix}_openai.json")
            
            # Anthropic format
            anthropic_schemas = {
                "tools": [schema.anthropic_schema for schema in schemas]
            }
            with open(f"{output_prefix}_anthropic.json", 'w') as f:
                json.dump(anthropic_schemas, f, indent=2)
            print(f"Anthropic schemas written to {output_prefix}_anthropic.json")
            
            # Validation rules
            validation_data = {
                "validation_rules": {schema.name: schema.validation_rules for schema in schemas}
            }
            with open(f"{output_prefix}_validation.json", 'w') as f:
                json.dump(validation_data, f, indent=2)
            print(f"Validation rules written to {output_prefix}_validation.json")
            
            # Usage examples
            examples_data = {
                "examples": {schema.name: schema.examples for schema in schemas}
            }
            with open(f"{output_prefix}_examples.json", 'w') as f:
                json.dump(examples_data, f, indent=2)
            print(f"Usage examples written to {output_prefix}_examples.json")
        
        # Print summary
        print(f"\nSchema Generation Summary:")
        print(f"Tools processed: {len(schemas)}")
        print(f"Total input parameters: {sum(schema.metadata['input_parameters'] for schema in schemas)}")
        print(f"Total validation rules: {sum(len(schema.validation_rules) for schema in schemas)}")
        print(f"Total examples generated: {sum(len(schema.examples) for schema in schemas)}")
        
        # Validation if requested
        if args.validate:
            print("\nValidation Results:")
            for schema in schemas:
                validation_errors = []
                
                # Basic validation checks
                if not schema.openai_schema.get("parameters", {}).get("properties"):
                    validation_errors.append("Missing input parameters")
                
                if not schema.examples:
                    validation_errors.append("No usage examples")
                
                if not schema.validation_rules:
                    validation_errors.append("No validation rules defined")
                
                if validation_errors:
                    print(f"  {schema.name}: {', '.join(validation_errors)}")
                else:
                    print(f"  {schema.name}: ✓ Valid")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
