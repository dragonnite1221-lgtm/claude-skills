# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402
from question_bank_generator_p2 import format_human_readable  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive interview question banks with scoring criteria")
    parser.add_argument("--role", type=str, help="Job role title (e.g., 'Frontend Engineer')")
    parser.add_argument("--level", type=str, default="senior", help="Experience level (junior, mid, senior, staff, principal)")
    parser.add_argument("--competencies", type=str, help="Comma-separated list of competencies to focus on")
    parser.add_argument("--question-types", type=str, help="Comma-separated list of question types (technical, behavioral, situational)")
    parser.add_argument("--num-questions", type=int, default=20, help="Number of questions to generate")
    parser.add_argument("--input", type=str, help="Input JSON file with role requirements")
    parser.add_argument("--output", type=str, help="Output directory or file path")
    parser.add_argument("--format", choices=["json", "text", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    generator = QuestionBankGenerator()
    
    # Handle input
    if args.input:
        try:
            with open(args.input, 'r') as f:
                role_data = json.load(f)
            role = role_data.get('role') or role_data.get('title', '')
            level = role_data.get('level', 'senior')
            competencies = role_data.get('competencies')
            question_types = role_data.get('question_types')
            num_questions = role_data.get('num_questions', 20)
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)
    else:
        if not args.role:
            print("Error: --role is required when not using --input")
            sys.exit(1)
        
        role = args.role
        level = args.level
        competencies = args.competencies.split(',') if args.competencies else None
        question_types = args.question_types.split(',') if args.question_types else None
        num_questions = args.num_questions
    
    # Generate question bank
    try:
        question_bank = generator.generate_question_bank(
            role=role,
            level=level,
            competencies=competencies,
            question_types=question_types,
            num_questions=num_questions
        )
        
        # Handle output
        if args.output:
            output_path = args.output
            if os.path.isdir(output_path):
                safe_role = "".join(c for c in role.lower() if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                base_filename = f"{safe_role}_{level}_questions"
                json_path = os.path.join(output_path, f"{base_filename}.json")
                text_path = os.path.join(output_path, f"{base_filename}.txt")
            else:
                json_path = output_path if output_path.endswith('.json') else f"{output_path}.json"
                text_path = output_path.replace('.json', '.txt') if output_path.endswith('.json') else f"{output_path}.txt"
        else:
            safe_role = "".join(c for c in role.lower() if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            base_filename = f"{safe_role}_{level}_questions"
            json_path = f"{base_filename}.json"
            text_path = f"{base_filename}.txt"
        
        # Write outputs
        if args.format in ["json", "both"]:
            with open(json_path, 'w') as f:
                json.dump(question_bank, f, indent=2, default=str)
            print(f"JSON output written to: {json_path}")
        
        if args.format in ["text", "both"]:
            with open(text_path, 'w') as f:
                f.write(format_human_readable(question_bank))
            print(f"Text output written to: {text_path}")
        
        # Print summary
        print(f"\nQuestion Bank Summary:")
        print(f"Role: {question_bank['role']} ({question_bank['level'].title()})")
        print(f"Total Questions: {question_bank['total_questions']}")
        print(f"Competencies Covered: {len(question_bank['competencies'])}")
        print(f"Question Types: {', '.join(question_bank['question_types'])}")
        
    except Exception as e:
        print(f"Error generating question bank: {e}")
        sys.exit(1)
