# ruff: noqa: E501
#!/usr/bin/env python3
"""
2.5D Asset Inspector
Usage: python scripts/inspect-assets.py image1.png image2.jpg ...
   or: python scripts/inspect-assets.py path/to/folder/

Checks each image and reports:
- Format and mode
- Whether it has a real transparent background
- Background type if not transparent (dark, light, complex)
- Recommended depth level based on image characteristics
- Whether the background is likely a problem (product shot vs scene/artwork)

The AI reads this output and uses it to inform the user.
The script NEVER modifies images — inspect only.
"""

import sys
import os

__all__ = ['os', 'sys']
