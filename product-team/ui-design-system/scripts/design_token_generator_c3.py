# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from design_token_generator_base import *  # noqa: F403,E402


class DesignTokenGeneratorMixin3:
    def generate_border_tokens(self, style: str) -> Dict:
        """Generate border tokens"""
        
        radius_values = {
            'modern': {
                'none': '0',
                'sm': '4px',
                'DEFAULT': '8px',
                'md': '12px',
                'lg': '16px',
                'xl': '24px',
                'full': '9999px'
            },
            'classic': {
                'none': '0',
                'sm': '2px',
                'DEFAULT': '4px',
                'md': '6px',
                'lg': '8px',
                'xl': '12px',
                'full': '9999px'
            },
            'playful': {
                'none': '0',
                'sm': '8px',
                'DEFAULT': '16px',
                'md': '20px',
                'lg': '24px',
                'xl': '32px',
                'full': '9999px'
            }
        }
        
        return {
            'radius': radius_values.get(style, radius_values['modern']),
            'width': {
                'none': '0',
                'thin': '1px',
                'DEFAULT': '1px',
                'medium': '2px',
                'thick': '4px'
            }
        }
    def generate_shadow_tokens(self, style: str) -> Dict:
        """Generate shadow tokens"""
        
        shadow_styles = {
            'modern': {
                'none': 'none',
                'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                'DEFAULT': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
            },
            'classic': {
                'none': 'none',
                'sm': '0 1px 2px rgba(0, 0, 0, 0.1)',
                'DEFAULT': '0 2px 4px rgba(0, 0, 0, 0.1)',
                'md': '0 4px 8px rgba(0, 0, 0, 0.1)',
                'lg': '0 8px 16px rgba(0, 0, 0, 0.1)',
                'xl': '0 16px 32px rgba(0, 0, 0, 0.1)'
            }
        }
        
        return shadow_styles.get(style, shadow_styles['modern'])
    def generate_animation_tokens(self) -> Dict:
        """Generate animation tokens"""
        
        return {
            'duration': {
                'instant': '0ms',
                'fast': '150ms',
                'DEFAULT': '250ms',
                'slow': '350ms',
                'slower': '500ms'
            },
            'easing': {
                'linear': 'linear',
                'ease': 'ease',
                'easeIn': 'ease-in',
                'easeOut': 'ease-out',
                'easeInOut': 'ease-in-out',
                'spring': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
            },
            'keyframes': {
                'fadeIn': {
                    'from': {'opacity': 0},
                    'to': {'opacity': 1}
                },
                'slideUp': {
                    'from': {'transform': 'translateY(10px)', 'opacity': 0},
                    'to': {'transform': 'translateY(0)', 'opacity': 1}
                },
                'scale': {
                    'from': {'transform': 'scale(0.95)'},
                    'to': {'transform': 'scale(1)'}
                }
            }
        }
