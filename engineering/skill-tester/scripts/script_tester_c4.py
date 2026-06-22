# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import ScriptTestResult  # noqa: F401,E501


class ScriptTesterMixin4:
    def _test_output_formats(self, script_path: Path, result: ScriptTestResult):
        """Test output format compliance"""
        self.log_verbose("Testing output formats...")
        
        # Test if script supports JSON output
        json_support = False
        human_readable_support = False
        
        try:
            # Read script content to check for output format indicators
            content = script_path.read_text(encoding='utf-8')
            
            # Look for JSON-related code
            if any(indicator in content.lower() for indicator in ['json.dump', 'json.load', '"json"', '--json']):
                json_support = True
                
            # Look for human-readable output indicators
            if any(indicator in content for indicator in ['print(', 'format(', 'f"', "f'"]):
                human_readable_support = True
                
            # Try running with --json flag if it looks like it supports it
            if '--json' in content:
                try:
                    process = subprocess.run(
                        [sys.executable, str(script_path), '--json', '--help'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=script_path.parent
                    )
                    if process.returncode == 0:
                        json_support = True
                except:
                    pass
                    
            # Evaluate dual output support
            if json_support and human_readable_support:
                result.add_test("output_formats", True, "Supports both JSON and human-readable output")
            elif json_support or human_readable_support:
                format_type = "JSON" if json_support else "human-readable"
                result.add_test("output_formats", False,
                               f"Supports only {format_type} output",
                               {"json_support": json_support, "human_readable_support": human_readable_support})
                result.add_warning("Consider adding dual output format support")
            else:
                result.add_test("output_formats", False, "No clear output format support detected")
                result.add_warning("Output format support is unclear")
                
        except Exception as e:
            result.add_test("output_formats", False, f"Error testing output formats: {str(e)}")
