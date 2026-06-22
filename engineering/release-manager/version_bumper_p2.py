# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402


@dataclass
class ConventionalCommit:
    """Represents a parsed conventional commit for version analysis."""
    type: str
    scope: str
    description: str
    is_breaking: bool
    breaking_description: str
    hash: str = ""
    author: str = ""
    date: str = ""
    
    @classmethod
    def parse_message(cls, message: str, commit_hash: str = "", 
                     author: str = "", date: str = "") -> 'ConventionalCommit':
        """Parse conventional commit message."""
        lines = message.split('\n')
        header = lines[0] if lines else ""
        
        # Parse header: type(scope): description
        header_pattern = r'^(\w+)(\([^)]+\))?(!)?:\s*(.+)$'
        match = re.match(header_pattern, header)
        
        commit_type = "chore"
        scope = ""
        description = header
        is_breaking = False
        breaking_description = ""
        
        if match:
            commit_type = match.group(1).lower()
            scope_match = match.group(2)
            scope = scope_match[1:-1] if scope_match else ""
            is_breaking = bool(match.group(3))  # ! indicates breaking change
            description = match.group(4).strip()
        
        # Check for breaking change in body/footers
        if len(lines) > 1:
            body_text = '\n'.join(lines[1:])
            if 'BREAKING CHANGE:' in body_text:
                is_breaking = True
                breaking_match = re.search(r'BREAKING CHANGE:\s*(.+)', body_text)
                if breaking_match:
                    breaking_description = breaking_match.group(1).strip()
        
        return cls(commit_type, scope, description, is_breaking, breaking_description,
                  commit_hash, author, date)
