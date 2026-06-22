# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402


class PythonASTAnalyzer(ast.NodeVisitor):
    """AST analyzer for Python-specific debt detection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.debt_items = []
        self.current_file = ""
        self.lines = []
        self.function_stack = []
    
    def analyze(self, tree: ast.AST, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze Python AST for tech debt."""
        self.debt_items = []
        self.current_file = file_path
        self.lines = lines
        self.function_stack = []
        
        self.visit(tree)
        return self.debt_items
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function definitions."""
        self.function_stack.append(node.name)
        
        # Calculate function length
        func_length = node.end_lineno - node.lineno + 1
        if func_length > self.config["max_function_length"]:
            self._add_debt(
                "large_function",
                f"Function '{node.name}' is too long: {func_length} lines",
                node.lineno,
                "medium",
                {"function_name": node.name, "length": func_length}
            )
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            self._add_debt(
                "missing_docstring",
                f"Function '{node.name}' missing docstring",
                node.lineno,
                "low",
                {"function_name": node.name}
            )
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_complexity(node)
        if complexity > self.config["max_complexity"]:
            self._add_debt(
                "high_complexity",
                f"Function '{node.name}' has high complexity: {complexity}",
                node.lineno,
                "high",
                {"function_name": node.name, "complexity": complexity}
            )
        
        # Check parameter count
        param_count = len(node.args.args)
        if param_count > 5:
            self._add_debt(
                "too_many_parameters",
                f"Function '{node.name}' has too many parameters: {param_count}",
                node.lineno,
                "medium",
                {"function_name": node.name, "parameter_count": param_count}
            )
        
        self.generic_visit(node)
        self.function_stack.pop()
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definitions."""
        # Check for missing docstring
        if not ast.get_docstring(node):
            self._add_debt(
                "missing_docstring",
                f"Class '{node.name}' missing docstring",
                node.lineno,
                "low",
                {"class_name": node.name}
            )
        
        # Check for too many methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            self._add_debt(
                "large_class",
                f"Class '{node.name}' has too many methods: {len(methods)}",
                node.lineno,
                "medium",
                {"class_name": node.name, "method_count": len(methods)}
            )
        
        self.generic_visit(node)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _add_debt(self, debt_type: str, description: str, line_number: int,
                 severity: str, metadata: Dict[str, Any]):
        """Add a debt item to the collection."""
        item = {
            "id": f"DEBT-{len(self.debt_items) + 1:04d}",
            "type": debt_type,
            "description": description,
            "file_path": self.current_file,
            "line_number": line_number,
            "severity": severity,
            "metadata": metadata,
            "detected_date": datetime.now().isoformat(),
            "status": "identified"
        }
        self.debt_items.append(item)
