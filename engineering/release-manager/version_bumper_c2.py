# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402


class VersionBumperMixin2:
    def analyze_commits(self) -> Dict:
        """Provide detailed analysis of commits for version bumping."""
        if not self.commits:
            return {
                'total_commits': 0,
                'by_type': {},
                'breaking_changes': [],
                'features': [],
                'fixes': [],
                'ignored': []
            }
        
        analysis = {
            'total_commits': len(self.commits),
            'by_type': {},
            'breaking_changes': [],
            'features': [],
            'fixes': [],
            'ignored': []
        }
        
        type_counts = {}
        for commit in self.commits:
            type_counts[commit.type] = type_counts.get(commit.type, 0) + 1
            
            if commit.is_breaking:
                analysis['breaking_changes'].append({
                    'type': commit.type,
                    'scope': commit.scope,
                    'description': commit.description,
                    'breaking_description': commit.breaking_description,
                    'hash': commit.hash
                })
            elif commit.type in ['feat', 'add']:
                analysis['features'].append({
                    'scope': commit.scope,
                    'description': commit.description,
                    'hash': commit.hash
                })
            elif commit.type in ['fix', 'security', 'perf', 'bugfix']:
                analysis['fixes'].append({
                    'scope': commit.scope, 
                    'description': commit.description,
                    'hash': commit.hash
                })
            elif commit.type in self.ignore_types:
                analysis['ignored'].append({
                    'type': commit.type,
                    'scope': commit.scope,
                    'description': commit.description,
                    'hash': commit.hash
                })
        
        analysis['by_type'] = type_counts
        return analysis
