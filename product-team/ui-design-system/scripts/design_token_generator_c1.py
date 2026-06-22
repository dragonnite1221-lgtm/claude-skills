# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from design_token_generator_base import *  # noqa: F403,E402


class DesignTokenGeneratorMixin1:
    def _generate_neutral_scale(self) -> Dict:
        """Generate neutral color scale"""
        
        return {
            '50': '#F9FAFB',
            '100': '#F3F4F6',
            '200': '#E5E7EB',
            '300': '#D1D5DB',
            '400': '#9CA3AF',
            '500': '#6B7280',
            '600': '#4B5563',
            '700': '#374151',
            '800': '#1F2937',
            '900': '#111827',
            'DEFAULT': '#6B7280'
        }
    def generate_typography_system(self, style: str) -> Dict:
        """Generate typography system"""
        
        # Font families based on style
        font_families = {
            'modern': {
                'sans': 'Inter, system-ui, -apple-system, sans-serif',
                'serif': 'Merriweather, Georgia, serif',
                'mono': 'Fira Code, Monaco, monospace'
            },
            'classic': {
                'sans': 'Helvetica, Arial, sans-serif',
                'serif': 'Times New Roman, Times, serif',
                'mono': 'Courier New, monospace'
            },
            'playful': {
                'sans': 'Poppins, Roboto, sans-serif',
                'serif': 'Playfair Display, Georgia, serif',
                'mono': 'Source Code Pro, monospace'
            }
        }
        
        typography = {
            'fontFamily': font_families.get(style, font_families['modern']),
            'fontSize': self._generate_type_scale(),
            'fontWeight': {
                'thin': 100,
                'light': 300,
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700,
                'extrabold': 800,
                'black': 900
            },
            'lineHeight': {
                'none': 1,
                'tight': 1.25,
                'snug': 1.375,
                'normal': 1.5,
                'relaxed': 1.625,
                'loose': 2
            },
            'letterSpacing': {
                'tighter': '-0.05em',
                'tight': '-0.025em',
                'normal': '0',
                'wide': '0.025em',
                'wider': '0.05em',
                'widest': '0.1em'
            },
            'textStyles': self._generate_text_styles()
        }
        
        return typography
    def _generate_type_scale(self) -> Dict:
        """Generate modular type scale"""
        
        scale = {}
        sizes = ['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl']
        
        for i, size in enumerate(sizes):
            if size == 'base':
                scale[size] = f'{self.base_font_size}px'
            elif i < sizes.index('base'):
                factor = self.type_scale_ratio ** (sizes.index('base') - i)
                scale[size] = f'{round(self.base_font_size / factor)}px'
            else:
                factor = self.type_scale_ratio ** (i - sizes.index('base'))
                scale[size] = f'{round(self.base_font_size * factor)}px'
        
        return scale
