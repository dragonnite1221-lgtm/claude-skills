# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402
from version_bumper_p0 import BumpType, PreReleaseType  # noqa: F401,E501


@dataclass
class Version:
    """Semantic version representation."""
    major: int
    minor: int
    patch: int
    prerelease_type: Optional[PreReleaseType] = None
    prerelease_number: Optional[int] = None
    
    @classmethod
    def parse(cls, version_str: str) -> 'Version':
        """Parse version string into Version object."""
        # Remove 'v' prefix if present
        clean_version = version_str.lstrip('v')
        
        # Pattern for semantic versioning with optional pre-release
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-(\w+)\.?(\d+)?)?$'
        match = re.match(pattern, clean_version)
        
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        
        major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
        
        prerelease_type = None
        prerelease_number = None
        
        if match.group(4):  # Pre-release identifier
            prerelease_str = match.group(4).lower()
            try:
                prerelease_type = PreReleaseType(prerelease_str)
            except ValueError:
                # Handle variations like 'alpha1' -> 'alpha'
                if prerelease_str.startswith('alpha'):
                    prerelease_type = PreReleaseType.ALPHA
                elif prerelease_str.startswith('beta'):
                    prerelease_type = PreReleaseType.BETA
                elif prerelease_str.startswith('rc'):
                    prerelease_type = PreReleaseType.RC
                else:
                    raise ValueError(f"Unknown pre-release type: {prerelease_str}")
            
            if match.group(5):
                prerelease_number = int(match.group(5))
            else:
                # Extract number from combined string like 'alpha1'
                number_match = re.search(r'(\d+)$', prerelease_str)
                if number_match:
                    prerelease_number = int(number_match.group(1))
                else:
                    prerelease_number = 1  # Default to 1
        
        return cls(major, minor, patch, prerelease_type, prerelease_number)
    
    def to_string(self, include_v_prefix: bool = False) -> str:
        """Convert version to string representation."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        
        if self.prerelease_type:
            if self.prerelease_number is not None:
                base += f"-{self.prerelease_type.value}.{self.prerelease_number}"
            else:
                base += f"-{self.prerelease_type.value}"
        
        return f"v{base}" if include_v_prefix else base
    
    def bump(self, bump_type: BumpType, prerelease_type: Optional[PreReleaseType] = None) -> 'Version':
        """Create new version with specified bump."""
        if bump_type == BumpType.NONE:
            return Version(self.major, self.minor, self.patch, self.prerelease_type, self.prerelease_number)
        
        new_major = self.major
        new_minor = self.minor  
        new_patch = self.patch
        new_prerelease_type = None
        new_prerelease_number = None
        
        # Handle pre-release versions
        if prerelease_type:
            if bump_type == BumpType.MAJOR:
                new_major += 1
                new_minor = 0
                new_patch = 0
            elif bump_type == BumpType.MINOR:
                new_minor += 1
                new_patch = 0
            elif bump_type == BumpType.PATCH:
                new_patch += 1
            
            new_prerelease_type = prerelease_type
            new_prerelease_number = 1
        
        # Handle existing pre-release -> next pre-release
        elif self.prerelease_type:
            # If we're already in pre-release, increment or promote
            if prerelease_type is None:
                # Promote to stable release
                # Don't change version numbers, just remove pre-release
                pass
            else:
                # Move to next pre-release type or increment
                if prerelease_type == self.prerelease_type:
                    # Same pre-release type, increment number
                    new_prerelease_type = self.prerelease_type
                    new_prerelease_number = (self.prerelease_number or 0) + 1
                else:
                    # Different pre-release type
                    new_prerelease_type = prerelease_type
                    new_prerelease_number = 1
        
        # Handle stable version bumps
        else:
            if bump_type == BumpType.MAJOR:
                new_major += 1
                new_minor = 0
                new_patch = 0
            elif bump_type == BumpType.MINOR:
                new_minor += 1
                new_patch = 0
            elif bump_type == BumpType.PATCH:
                new_patch += 1
        
        return Version(new_major, new_minor, new_patch, new_prerelease_type, new_prerelease_number)
