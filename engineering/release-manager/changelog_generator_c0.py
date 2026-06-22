# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from changelog_generator_base import *  # noqa: F403,E402
from changelog_generator_p0 import ConventionalCommit  # noqa: F401,E501


class ChangelogGeneratorMixin0:
    """Main changelog generator class."""
    def __init__(self):
        self.commits: List[ConventionalCommit] = []
        self.version = "Unreleased"
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.base_url = ""
    def parse_git_log_output(self, git_log_text: str):
        """Parse git log output into ConventionalCommit objects."""
        # Try to detect format based on patterns in the text
        lines = git_log_text.strip().split('\n')
        
        if not lines or not lines[0]:
            return
            
        # Format 1: Simple oneline format (hash message)
        oneline_pattern = r'^([a-f0-9]{7,40})\s+(.+)$'
        
        # Format 2: Full format with metadata
        full_pattern = r'^commit\s+([a-f0-9]+)'
        
        current_commit = None
        commit_buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a new commit (oneline format)
            oneline_match = re.match(oneline_pattern, line)
            if oneline_match:
                # Process previous commit
                if current_commit:
                    self.commits.append(current_commit)
                
                # Start new commit
                commit_hash = oneline_match.group(1)
                message = oneline_match.group(2)
                current_commit = ConventionalCommit(message, commit_hash)
                continue
            
            # Check if this is a new commit (full format)
            full_match = re.match(full_pattern, line)
            if full_match:
                # Process previous commit
                if current_commit:
                    commit_message = '\n'.join(commit_buffer).strip()
                    if commit_message:
                        current_commit = ConventionalCommit(commit_message, current_commit.commit_hash, 
                                                          current_commit.author, current_commit.date)
                    self.commits.append(current_commit)
                
                # Start new commit
                commit_hash = full_match.group(1)
                current_commit = ConventionalCommit("", commit_hash)
                commit_buffer = []
                continue
            
            # Parse metadata lines in full format
            if current_commit and not current_commit.raw_message:
                if line.startswith('Author:'):
                    current_commit.author = line[7:].strip()
                elif line.startswith('Date:'):
                    current_commit.date = line[5:].strip()
                elif line.startswith('Merge:'):
                    current_commit.merge_info = line[6:].strip()
                elif line.startswith('    '):
                    # Commit message line (indented)
                    commit_buffer.append(line[4:])  # Remove 4-space indent
            
        # Process final commit
        if current_commit:
            if commit_buffer:
                commit_message = '\n'.join(commit_buffer).strip()
                current_commit = ConventionalCommit(commit_message, current_commit.commit_hash,
                                                  current_commit.author, current_commit.date)
            self.commits.append(current_commit)
    def parse_json_commits(self, json_data: Union[str, List[Dict]]):
        """Parse commits from JSON format."""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        for commit_data in data:
            commit = ConventionalCommit(
                raw_message=commit_data.get('message', ''),
                commit_hash=commit_data.get('hash', ''),
                author=commit_data.get('author', ''),
                date=commit_data.get('date', '')
            )
            self.commits.append(commit)
    def group_commits_by_category(self) -> Dict[str, List[ConventionalCommit]]:
        """Group commits by changelog category."""
        categories = defaultdict(list)
        
        for commit in self.commits:
            category = commit.get_changelog_category()
            if category:  # Skip None categories (internal changes)
                categories[category].append(commit)
        
        return dict(categories)
