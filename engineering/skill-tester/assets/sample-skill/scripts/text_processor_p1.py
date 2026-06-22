# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from text_processor_base import *  # noqa: F403,E402


class TextProcessor:
    """Core text processing functionality"""
    
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text and return statistics"""
        lines = text.split('\n')
        words = text.lower().split()
        
        # Calculate basic statistics
        stats = {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'total_characters': len(text),
            'lines': len(lines),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
        
        # Find most frequent word
        if words:
            word_counts = Counter(words)
            most_common = word_counts.most_common(1)[0]
            stats['most_frequent'] = {
                'word': most_common[0],
                'count': most_common[1]
            }
        else:
            stats['most_frequent'] = {'word': '', 'count': 0}
            
        return stats
        
    def transform_text(self, text: str, mode: str) -> str:
        """Transform text according to specified mode"""
        if mode == 'upper':
            return text.upper()
        elif mode == 'lower':
            return text.lower()
        elif mode == 'title':
            return text.title()
        elif mode == 'reverse':
            return text[::-1]
        else:
            raise ValueError(f"Unknown transformation mode: {mode}")
            
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single text file"""
        try:
            with open(file_path, 'r', encoding=self.encoding) as file:
                content = file.read()
                
            stats = self.analyze_text(content)
            stats['file'] = file_path
            stats['file_size'] = os.path.getsize(file_path)
            
            return stats
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Cannot decode file with {self.encoding} encoding: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied accessing file: {file_path}")
class OutputFormatter:
    """Handles dual output format generation"""
    
    @staticmethod
    def format_json(data: Dict[str, Any]) -> str:
        """Format data as JSON"""
        return json.dumps(data, indent=2, ensure_ascii=False)
        
    @staticmethod
    def format_human_readable(data: Dict[str, Any]) -> str:
        """Format data as human-readable text"""
        lines = []
        lines.append("=== TEXT ANALYSIS RESULTS ===")
        lines.append(f"File: {data.get('file', 'Unknown')}")
        lines.append(f"File size: {data.get('file_size', 0)} bytes")
        lines.append(f"Total words: {data.get('total_words', 0)}")
        lines.append(f"Unique words: {data.get('unique_words', 0)}")
        lines.append(f"Total characters: {data.get('total_characters', 0)}")
        lines.append(f"Lines: {data.get('lines', 0)}")
        lines.append(f"Average word length: {data.get('average_word_length', 0):.1f}")
        
        most_frequent = data.get('most_frequent', {})
        lines.append(f"Most frequent word: \"{most_frequent.get('word', '')}\" ({most_frequent.get('count', 0)} occurrences)")
        
        return "\n".join(lines)
