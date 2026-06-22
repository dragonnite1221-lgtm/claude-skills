# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from changelog_generator_base import *  # noqa: F403,E402


class ChangelogGeneratorMixin2:
    def generate_release_summary(self) -> Dict:
        """Generate summary statistics for the release."""
        if not self.commits:
            return {
                'version': self.version,
                'date': self.date,
                'total_commits': 0,
                'by_type': {},
                'by_author': {},
                'breaking_changes': 0,
                'notable_changes': 0
            }
        
        # Count by type
        type_counts = Counter(commit.type for commit in self.commits)
        
        # Count by author
        author_counts = Counter(commit.author for commit in self.commits if commit.author)
        
        # Count breaking changes
        breaking_count = sum(1 for commit in self.commits if commit.is_breaking)
        
        # Count notable changes (excluding chore, ci, build, test)
        notable_types = {'feat', 'fix', 'security', 'perf', 'refactor', 'remove', 'deprecate'}
        notable_count = sum(1 for commit in self.commits if commit.type in notable_types)
        
        return {
            'version': self.version,
            'date': self.date,
            'total_commits': len(self.commits),
            'by_type': dict(type_counts.most_common()),
            'by_author': dict(author_counts.most_common(10)),  # Top 10 contributors
            'breaking_changes': breaking_count,
            'notable_changes': notable_count,
            'scopes': list(set(commit.scope for commit in self.commits if commit.scope)),
            'issue_references': len(set().union(*(commit.extract_issue_references() for commit in self.commits)))
        }
    def generate_json_output(self) -> str:
        """Generate JSON representation of the changelog data."""
        grouped_commits = self.group_commits_by_category()
        
        # Convert commits to serializable format
        json_data = {
            'version': self.version,
            'date': self.date,
            'summary': self.generate_release_summary(),
            'categories': {}
        }
        
        for category, commits in grouped_commits.items():
            json_data['categories'][category] = []
            for commit in commits:
                commit_data = {
                    'type': commit.type,
                    'scope': commit.scope,
                    'description': commit.description,
                    'hash': commit.commit_hash,
                    'author': commit.author,
                    'date': commit.date,
                    'breaking': commit.is_breaking,
                    'breaking_description': commit.breaking_change_description,
                    'issue_references': commit.extract_issue_references()
                }
                json_data['categories'][category].append(commit_data)
        
        return json.dumps(json_data, indent=2)
