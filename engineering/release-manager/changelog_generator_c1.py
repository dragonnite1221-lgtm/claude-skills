# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from changelog_generator_base import *  # noqa: F403,E402
from changelog_generator_p0 import ConventionalCommit  # noqa: F401,E501


class ChangelogGeneratorMixin1:
    def generate_markdown_changelog(self, include_unreleased: bool = True) -> str:
        """Generate Keep a Changelog format markdown."""
        grouped_commits = self.group_commits_by_category()
        
        if not grouped_commits:
            return "No notable changes.\n"
        
        # Start with header
        changelog = []
        if include_unreleased and self.version == "Unreleased":
            changelog.append(f"## [{self.version}]")
        else:
            changelog.append(f"## [{self.version}] - {self.date}")
        
        changelog.append("")
        
        # Order categories logically
        category_order = ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security']
        
        # Separate breaking changes
        breaking_changes = [commit for commit in self.commits if commit.is_breaking]
        
        # Add breaking changes section first if any exist
        if breaking_changes:
            changelog.append("### Breaking Changes")
            for commit in breaking_changes:
                line = self._format_commit_line(commit, show_breaking=True)
                changelog.append(f"- {line}")
            changelog.append("")
        
        # Add regular categories
        for category in category_order:
            if category not in grouped_commits:
                continue
                
            changelog.append(f"### {category}")
            
            # Group by scope for better organization
            scoped_commits = defaultdict(list)
            for commit in grouped_commits[category]:
                scope = commit.scope if commit.scope else "general"
                scoped_commits[scope].append(commit)
            
            # Sort scopes, with 'general' last
            scopes = sorted(scoped_commits.keys())
            if "general" in scopes:
                scopes.remove("general")
                scopes.append("general")
            
            for scope in scopes:
                if len(scoped_commits) > 1 and scope != "general":
                    changelog.append(f"#### {scope.title()}")
                
                for commit in scoped_commits[scope]:
                    line = self._format_commit_line(commit)
                    changelog.append(f"- {line}")
            
            changelog.append("")
        
        return '\n'.join(changelog)
    def _format_commit_line(self, commit: ConventionalCommit, show_breaking: bool = False) -> str:
        """Format a single commit line for the changelog."""
        # Start with description
        line = commit.description.capitalize()
        
        # Add scope if present and not already in description
        if commit.scope and commit.scope.lower() not in line.lower():
            line = f"{commit.scope}: {line}"
        
        # Add issue references
        issue_refs = commit.extract_issue_references()
        if issue_refs:
            refs_str = ', '.join(f"#{ref}" for ref in issue_refs)
            line += f" ({refs_str})"
        
        # Add commit hash if available
        if commit.commit_hash:
            short_hash = commit.commit_hash[:7]
            line += f" [{short_hash}]"
            
            if self.base_url:
                line += f"({self.base_url}/commit/{commit.commit_hash})"
        
        # Add breaking change indicator
        if show_breaking and commit.breaking_change_description:
            line += f" - {commit.breaking_change_description}"
        elif commit.is_breaking and not show_breaking:
            line += " ⚠️ BREAKING"
        
        return line
