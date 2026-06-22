# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import ScriptTestResult  # noqa: F401,E501


class ScriptTesterMixin3:
    def _test_help_functionality(self, script_path: Path, result: ScriptTestResult):
        """Test --help functionality"""
        self.log_verbose("Testing help functionality...")
        
        try:
            # Test --help flag
            process = subprocess.run(
                [sys.executable, str(script_path), '--help'],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=script_path.parent
            )
            
            if process.returncode == 0:
                help_output = process.stdout
                
                # Check for reasonable help content
                help_indicators = ['usage:', 'positional arguments:', 'optional arguments:', 
                                 'options:', 'description:', 'help']
                has_help_content = any(indicator in help_output.lower() for indicator in help_indicators)
                
                if has_help_content and len(help_output.strip()) > 50:
                    result.add_test("help_functionality", True, "Provides comprehensive help text")
                else:
                    result.add_test("help_functionality", False, 
                                   "Help text is too brief or missing key sections",
                                   {"help_output": help_output})
                    result.add_warning("Help text could be more comprehensive")
                    
            else:
                result.add_test("help_functionality", False, 
                               f"Help command failed with exit code {process.returncode}",
                               {"stderr": process.stderr})
                result.add_error("--help flag does not work properly")
                
        except subprocess.TimeoutExpired:
            result.add_test("help_functionality", False, "Help command timed out")
            
        except Exception as e:
            result.add_test("help_functionality", False, f"Help test error: {str(e)}")
    def _test_sample_data_processing(self, script_path: Path, result: ScriptTestResult):
        """Test script against sample data if available"""
        self.log_verbose("Testing sample data processing...")
        
        assets_dir = self.skill_path / "assets"
        if not assets_dir.exists():
            result.add_test("sample_data_processing", True, "No sample data to test (assets dir missing)")
            return
            
        # Look for sample input files
        sample_files = list(assets_dir.rglob("*sample*")) + list(assets_dir.rglob("*test*"))
        sample_files = [f for f in sample_files if f.is_file() and not f.name.startswith('.')]
        
        if not sample_files:
            result.add_test("sample_data_processing", True, "No sample data files found to test")
            return
            
        tested_files = 0
        successful_tests = 0
        
        for sample_file in sample_files[:3]:  # Test up to 3 sample files
            try:
                self.log_verbose(f"Testing with sample file: {sample_file.name}")
                
                # Try to run script with the sample file as input
                process = subprocess.run(
                    [sys.executable, str(script_path), str(sample_file)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=script_path.parent
                )
                
                tested_files += 1
                
                if process.returncode == 0:
                    successful_tests += 1
                else:
                    self.log_verbose(f"Sample test failed for {sample_file.name}: {process.stderr}")
                    
            except subprocess.TimeoutExpired:
                tested_files += 1
                result.add_warning(f"Sample data test timed out for {sample_file.name}")
            except Exception as e:
                tested_files += 1
                self.log_verbose(f"Sample test error for {sample_file.name}: {str(e)}")
                
        if tested_files == 0:
            result.add_test("sample_data_processing", True, "No testable sample data found")
        elif successful_tests == tested_files:
            result.add_test("sample_data_processing", True, 
                           f"Successfully processed all {tested_files} sample files")
        elif successful_tests > 0:
            result.add_test("sample_data_processing", False,
                           f"Processed {successful_tests}/{tested_files} sample files",
                           {"success_rate": successful_tests / tested_files})
            result.add_warning("Some sample data processing failed")
        else:
            result.add_test("sample_data_processing", False, 
                           "Failed to process any sample data files")
            result.add_error("Script cannot process sample data")
