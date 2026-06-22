# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from design_token_generator_base import *  # noqa: F403,E402


class DesignTokenGeneratorMixin2:
    def _generate_text_styles(self) -> Dict:
        """Generate pre-composed text styles"""
        
        return {
            'h1': {
                'fontSize': '48px',
                'fontWeight': 700,
                'lineHeight': 1.2,
                'letterSpacing': '-0.02em'
            },
            'h2': {
                'fontSize': '36px',
                'fontWeight': 700,
                'lineHeight': 1.3,
                'letterSpacing': '-0.01em'
            },
            'h3': {
                'fontSize': '28px',
                'fontWeight': 600,
                'lineHeight': 1.4,
                'letterSpacing': '0'
            },
            'h4': {
                'fontSize': '24px',
                'fontWeight': 600,
                'lineHeight': 1.4,
                'letterSpacing': '0'
            },
            'h5': {
                'fontSize': '20px',
                'fontWeight': 600,
                'lineHeight': 1.5,
                'letterSpacing': '0'
            },
            'h6': {
                'fontSize': '16px',
                'fontWeight': 600,
                'lineHeight': 1.5,
                'letterSpacing': '0.01em'
            },
            'body': {
                'fontSize': '16px',
                'fontWeight': 400,
                'lineHeight': 1.5,
                'letterSpacing': '0'
            },
            'small': {
                'fontSize': '14px',
                'fontWeight': 400,
                'lineHeight': 1.5,
                'letterSpacing': '0'
            },
            'caption': {
                'fontSize': '12px',
                'fontWeight': 400,
                'lineHeight': 1.5,
                'letterSpacing': '0.01em'
            }
        }
    def generate_spacing_system(self) -> Dict:
        """Generate spacing system based on 8pt grid"""
        
        spacing = {}
        multipliers = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 24, 32, 40, 48, 56, 64]
        
        for i, mult in enumerate(multipliers):
            spacing[str(i)] = f'{int(self.base_unit * mult)}px'
        
        # Add semantic spacing
        spacing.update({
            'xs': spacing['1'],    # 4px
            'sm': spacing['2'],    # 8px
            'md': spacing['4'],    # 16px
            'lg': spacing['6'],    # 24px
            'xl': spacing['8'],    # 32px
            '2xl': spacing['12'],  # 48px
            '3xl': spacing['16']   # 64px
        })
        
        return spacing
    def generate_sizing_tokens(self) -> Dict:
        """Generate sizing tokens for components"""
        
        return {
            'container': {
                'sm': '640px',
                'md': '768px',
                'lg': '1024px',
                'xl': '1280px',
                '2xl': '1536px'
            },
            'components': {
                'button': {
                    'sm': {'height': '32px', 'paddingX': '12px'},
                    'md': {'height': '40px', 'paddingX': '16px'},
                    'lg': {'height': '48px', 'paddingX': '20px'}
                },
                'input': {
                    'sm': {'height': '32px', 'paddingX': '12px'},
                    'md': {'height': '40px', 'paddingX': '16px'},
                    'lg': {'height': '48px', 'paddingX': '20px'}
                },
                'icon': {
                    'sm': '16px',
                    'md': '20px',
                    'lg': '24px',
                    'xl': '32px'
                }
            }
        }
