# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from changelog_generator_base import *  # noqa: F403,E402


class ConventionalCommit:
    """Represents a parsed conventional commit."""
    
    def __init__(self, raw_message: str, commit_hash: str = "", author: str = "", 
                 date: str = "", merge_info: Optional[str] = None):
        self.raw_message = raw_message
        self.commit_hash = commit_hash
        self.author = author
        self.date = date
        self.merge_info = merge_info
        
        # Parse the commit message
        self.type = ""
        self.scope = ""
        self.description = ""
        self.body = ""
        self.footers = []
        self.is_breaking = False
        self.breaking_change_description = ""
        
        self._parse_commit_message()
    
    def _parse_commit_message(self):
        """Parse conventional commit format."""
        lines = self.raw_message.split('\n')
        header = lines[0] if lines else ""
        
        # Parse header: type(scope): description
        header_pattern = r'^(\w+)(\([^)]+\))?(!)?:\s*(.+)$'
        match = re.match(header_pattern, header)
        
        if match:
            self.type = match.group(1).lower()
            scope_match = match.group(2)
            self.scope = scope_match[1:-1] if scope_match else ""  # Remove parentheses
            self.is_breaking = bool(match.group(3))  # ! indicates breaking change
            self.description = match.group(4).strip()
        else:
            # Fallback for non-conventional commits
            self.type = "chore"
            self.description = header
        
        # Parse body and footers
        if len(lines) > 1:
            body_lines = []
            footer_lines = []
            in_footer = False
            
            for line in lines[1:]:
                if not line.strip():
                    continue
                    
                # Check if this is a footer (KEY: value or KEY #value format)
                footer_pattern = r'^([A-Z-]+):\s*(.+)$|^([A-Z-]+)\s+#(\d+)$'
                if re.match(footer_pattern, line):
                    in_footer = True
                    footer_lines.append(line)
                    
                    # Check for breaking change
                    if line.startswith('BREAKING CHANGE:'):
                        self.is_breaking = True
                        self.breaking_change_description = line[16:].strip()
                else:
                    if in_footer:
                        # Continuation of footer
                        footer_lines.append(line)
                    else:
                        body_lines.append(line)
            
            self.body = '\n'.join(body_lines).strip()
            self.footers = footer_lines
    
    def extract_issue_references(self) -> List[str]:
        """Extract issue/PR references like #123, fixes #456, etc."""
        text = f"{self.description} {self.body} {' '.join(self.footers)}"
        
        # Common patterns for issue references
        patterns = [
            r'#(\d+)',  # Simple #123
            r'(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)',  # closes #123
            r'(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(\w+/\w+)?#(\d+)'  # fixes repo#123
        ]
        
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle tuple results from more complex patterns
                    ref = match[-1] if match[-1] else match[0]
                else:
                    ref = match
                if ref and ref not in references:
                    references.append(ref)
        
        return references
    
    def get_changelog_category(self) -> str:
        """Map commit type to changelog category."""
        category_map = {
            'feat': 'Added',
            'add': 'Added',
            'fix': 'Fixed',
            'bugfix': 'Fixed',
            'security': 'Security',
            'perf': 'Fixed',  # Performance improvements go to Fixed
            'refactor': 'Changed',
            'style': 'Changed',
            'docs': 'Changed',
            'test': None,  # Tests don't appear in user-facing changelog
            'ci': None,
            'build': None,
            'chore': None,
            'revert': 'Fixed',
            'remove': 'Removed',
            'deprecate': 'Deprecated'
        }
        
        return category_map.get(self.type, 'Changed')
