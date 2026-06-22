# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from design_token_generator_base import *  # noqa: F403,E402


class DesignTokenGeneratorMixin0:
    """Generate comprehensive design system tokens"""
    def __init__(self):
        self.base_unit = 8  # 8pt grid system
        self.type_scale_ratio = 1.25  # Major third
        self.base_font_size = 16
    def generate_complete_system(self, brand_color: str = "#0066CC", 
                                style: str = "modern") -> Dict:
        """Generate complete design token system"""
        
        tokens = {
            'meta': {
                'version': '1.0.0',
                'style': style,
                'generated': 'auto-generated'
            },
            'colors': self.generate_color_palette(brand_color),
            'typography': self.generate_typography_system(style),
            'spacing': self.generate_spacing_system(),
            'sizing': self.generate_sizing_tokens(),
            'borders': self.generate_border_tokens(style),
            'shadows': self.generate_shadow_tokens(style),
            'animation': self.generate_animation_tokens(),
            'breakpoints': self.generate_breakpoints(),
            'z-index': self.generate_z_index_scale()
        }
        
        return tokens
    def generate_color_palette(self, brand_color: str) -> Dict:
        """Generate comprehensive color palette from brand color"""
        
        # Convert hex to RGB
        brand_rgb = self._hex_to_rgb(brand_color)
        brand_hsv = colorsys.rgb_to_hsv(*[c/255 for c in brand_rgb])
        
        palette = {
            'primary': self._generate_color_scale(brand_color, 'primary'),
            'secondary': self._generate_color_scale(
                self._adjust_hue(brand_color, 180), 'secondary'
            ),
            'neutral': self._generate_neutral_scale(),
            'semantic': {
                'success': {
                    'base': '#10B981',
                    'light': '#34D399',
                    'dark': '#059669',
                    'contrast': '#FFFFFF'
                },
                'warning': {
                    'base': '#F59E0B',
                    'light': '#FBBD24',
                    'dark': '#D97706',
                    'contrast': '#FFFFFF'
                },
                'error': {
                    'base': '#EF4444',
                    'light': '#F87171',
                    'dark': '#DC2626',
                    'contrast': '#FFFFFF'
                },
                'info': {
                    'base': '#3B82F6',
                    'light': '#60A5FA',
                    'dark': '#2563EB',
                    'contrast': '#FFFFFF'
                }
            },
            'surface': {
                'background': '#FFFFFF',
                'foreground': '#111827',
                'card': '#FFFFFF',
                'overlay': 'rgba(0, 0, 0, 0.5)',
                'divider': '#E5E7EB'
            }
        }
        
        return palette
    def _generate_color_scale(self, base_color: str, name: str) -> Dict:
        """Generate color scale from base color"""
        
        scale = {}
        rgb = self._hex_to_rgb(base_color)
        h, s, v = colorsys.rgb_to_hsv(*[c/255 for c in rgb])
        
        # Generate scale from 50 to 900
        steps = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
        
        for step in steps:
            # Adjust lightness based on step
            factor = (1000 - step) / 1000
            new_v = 0.95 if step < 500 else v * (1 - (step - 500) / 500)
            new_s = s * (0.3 + 0.7 * (step / 900))
            
            new_rgb = colorsys.hsv_to_rgb(h, new_s, new_v)
            scale[str(step)] = self._rgb_to_hex([int(c * 255) for c in new_rgb])
        
        scale['DEFAULT'] = base_color
        return scale
