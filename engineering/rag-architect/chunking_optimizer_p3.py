# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chunking_optimizer_base import *  # noqa: F403,E402
# fmt: off
from chunking_optimizer_p1 import ChunkingStrategy  # noqa: E402,E501
# fmt: on


class SemanticChunker(ChunkingStrategy):
    """Heading-aware semantic chunking."""
    
    def __init__(self, max_size: int = 1500, heading_weight: float = 2.0):
        config = {'max_size': max_size, 'heading_weight': heading_weight}
        super().__init__('semantic_heading', config)
        self.max_size = max_size
        self.heading_weight = heading_weight
        
        # Markdown and plain text heading patterns
        self.heading_patterns = [
            re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE),  # Markdown headers
            re.compile(r'^(.+)\n[=-]+\s*$', re.MULTILINE),  # Underlined headers
            re.compile(r'^\d+\.\s*(.+)$', re.MULTILINE),   # Numbered sections
        ]
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        sections = self._identify_sections(text)
        chunks = []
        chunk_id = 0
        
        for section in sections:
            section_chunks = self._chunk_section(section, chunk_id)
            chunks.extend(section_chunks)
            chunk_id += len(section_chunks)
        
        return chunks
    
    def _identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify sections based on headings."""
        sections = []
        lines = text.split('\n')
        current_section = {'heading': 'Introduction', 'content': '', 'level': 0}
        
        for line in lines:
            is_heading = False
            heading_level = 0
            heading_text = line.strip()
            
            # Check for markdown headers
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:
                    heading_text = line.strip('#').strip()
                    heading_level = level
                    is_heading = True
            
            # Check for underlined headers  
            elif len(sections) > 0 and line.strip() and all(c in '=-' for c in line.strip()):
                # Previous line might be heading
                if current_section['content']:
                    content_lines = current_section['content'].strip().split('\n')
                    if content_lines:
                        potential_heading = content_lines[-1].strip()
                        if len(potential_heading) > 0 and len(potential_heading) < 100:
                            # Treat as heading
                            current_section['content'] = '\n'.join(content_lines[:-1])
                            sections.append(current_section)
                            current_section = {
                                'heading': potential_heading,
                                'content': '',
                                'level': 1 if '=' in line else 2
                            }
                            continue
            
            if is_heading:
                if current_section['content'].strip():
                    sections.append(current_section)
                current_section = {
                    'heading': heading_text,
                    'content': '',
                    'level': heading_level
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _chunk_section(self, section: Dict[str, Any], start_id: int) -> List[Dict[str, Any]]:
        """Chunk a single section."""
        content = section['content'].strip()
        if not content:
            return []
        
        heading = section['heading']
        chunks = []
        
        # If section is small enough, return as single chunk
        if len(content) <= self.max_size:
            chunks.append({
                'id': start_id,
                'text': f"{heading}\n\n{content}" if heading else content,
                'start': 0,
                'end': len(content),
                'size': len(content),
                'heading': heading,
                'level': section['level']
            })
            return chunks
        
        # Split large sections by paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        current_chunk = []
        current_size = len(heading) + 2 if heading else 0  # Account for heading
        chunk_id = start_id
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            if current_size + paragraph_size > self.max_size and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                if heading and chunk_id == start_id:
                    chunk_text = f"{heading}\n\n{chunk_text}"
                
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'start': 0,
                    'end': len(chunk_text),
                    'size': len(chunk_text),
                    'heading': heading if chunk_id == start_id else f"{heading} (continued)",
                    'level': section['level']
                })
                chunk_id += 1
                current_chunk = [paragraph]
                current_size = paragraph_size
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size + 2  # Account for newlines
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            if heading and chunk_id == start_id:
                chunk_text = f"{heading}\n\n{chunk_text}"
            elif heading:
                chunk_text = f"{heading} (continued)\n\n{chunk_text}"
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start': 0,
                'end': len(chunk_text),
                'size': len(chunk_text),
                'heading': heading if chunk_id == start_id else f"{heading} (continued)",
                'level': section['level']
            })
        
        return chunks
