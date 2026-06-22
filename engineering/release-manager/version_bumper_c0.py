# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402
from version_bumper_p0 import BumpType, PreReleaseType  # noqa: F401,E501
from version_bumper_p1 import Version  # noqa: F401,E501
from version_bumper_p2 import ConventionalCommit  # noqa: F401,E501


class VersionBumperMixin0:
    """Main version bumping logic."""
    def __init__(self):
        self.current_version: Optional[Version] = None
        self.commits: List[ConventionalCommit] = []
        self.custom_rules: Dict[str, BumpType] = {}
        self.ignore_types: List[str] = ['test', 'ci', 'build', 'chore', 'docs', 'style']
    def set_current_version(self, version_str: str):
        """Set the current version."""
        self.current_version = Version.parse(version_str)
    def add_custom_rule(self, commit_type: str, bump_type: BumpType):
        """Add custom rule for commit type to bump type mapping."""
        self.custom_rules[commit_type] = bump_type
    def parse_commits_from_json(self, json_data: Union[str, List[Dict]]):
        """Parse commits from JSON format."""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        self.commits = []
        for commit_data in data:
            commit = ConventionalCommit.parse_message(
                message=commit_data.get('message', ''),
                commit_hash=commit_data.get('hash', ''),
                author=commit_data.get('author', ''),
                date=commit_data.get('date', '')
            )
            self.commits.append(commit)
    def parse_commits_from_git_log(self, git_log_text: str):
        """Parse commits from git log output."""
        lines = git_log_text.strip().split('\n')
        
        if not lines or not lines[0]:
            return
        
        # Simple oneline format (hash message)
        oneline_pattern = r'^([a-f0-9]{7,40})\s+(.+)$'
        
        self.commits = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = re.match(oneline_pattern, line)
            if match:
                commit_hash = match.group(1)
                message = match.group(2)
                commit = ConventionalCommit.parse_message(message, commit_hash)
                self.commits.append(commit)
    def determine_bump_type(self) -> BumpType:
        """Determine version bump type based on commits."""
        if not self.commits:
            return BumpType.NONE
        
        has_breaking = False
        has_feature = False
        has_fix = False
        
        for commit in self.commits:
            # Check for breaking changes
            if commit.is_breaking:
                has_breaking = True
                continue
            
            # Apply custom rules first
            if commit.type in self.custom_rules:
                bump_type = self.custom_rules[commit.type]
                if bump_type == BumpType.MAJOR:
                    has_breaking = True
                elif bump_type == BumpType.MINOR:
                    has_feature = True
                elif bump_type == BumpType.PATCH:
                    has_fix = True
                continue
            
            # Standard rules
            if commit.type in ['feat', 'add']:
                has_feature = True
            elif commit.type in ['fix', 'security', 'perf', 'bugfix']:
                has_fix = True
            # Ignore types in ignore_types list
        
        # Determine bump type by priority
        if has_breaking:
            return BumpType.MAJOR
        elif has_feature:
            return BumpType.MINOR
        elif has_fix:
            return BumpType.PATCH
        else:
            return BumpType.NONE
    def recommend_version(self, prerelease_type: Optional[PreReleaseType] = None) -> Version:
        """Recommend new version based on commits."""
        if not self.current_version:
            raise ValueError("Current version not set")
        
        bump_type = self.determine_bump_type()
        return self.current_version.bump(bump_type, prerelease_type)
