"""File splitting utility for large task specifications.

This module provides functionality to split large markdown files into smaller,
independently evaluable chunks to work around OpenAI's rate limits.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any


def analyze_task_file(file_path: str) -> Dict[str, Any]:
    """Analyze file structure and suggest split points.
    
    Args:
        file_path: Path to the markdown file to analyze
        
    Returns:
        Dict containing:
        - total_lines: Total number of lines
        - sections: List of detected sections with metadata
        - estimated_tokens: Rough token estimate (lines * 4)
        - suggested_splits: List of suggested split points
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or too small
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        raise ValueError("File is empty or too small")
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    # Detect markdown sections
    sections = []
    current_section = None
    current_start = 1
    
    for i, line in enumerate(lines, 1):
        # Check for markdown headings (# or ##)
        if re.match(r'^#+\s+', line.strip()):
            # Close previous section
            if current_section is not None:
                current_section['end_line'] = i - 1
                current_section['line_count'] = current_section['end_line'] - current_section['start_line'] + 1
                sections.append(current_section)
            
            # Start new section
            heading_level = len(line.lstrip().split()[0])  # Count # characters
            title = re.sub(r'^#+\s+', '', line.strip())
            current_section = {
                'title': title,
                'heading_level': heading_level,
                'start_line': i,
                'end_line': None,
                'line_count': 0
            }
            current_start = i
    
    # Close final section
    if current_section is not None:
        current_section['end_line'] = total_lines
        current_section['line_count'] = current_section['end_line'] - current_section['start_line'] + 1
        sections.append(current_section)
    
    # If no sections found, treat entire file as one section
    if not sections:
        sections = [{
            'title': 'Full Document',
            'heading_level': 1,
            'start_line': 1,
            'end_line': total_lines,
            'line_count': total_lines
        }]
    
    # Estimate tokens (rough approximation: 1 line ≈ 4 tokens)
    estimated_tokens = total_lines * 4
    
    # Suggest splits if file is large
    suggested_splits = []
    if total_lines > 500:
        # Suggest section-based splits
        suggested_splits = _suggest_section_splits(sections, max_lines=500)
    
    return {
        'total_lines': total_lines,
        'sections': sections,
        'estimated_tokens': estimated_tokens,
        'suggested_splits': suggested_splits
    }


def split_by_sections(content: str, max_lines: int = 500) -> List[Dict[str, Any]]:
    """Split file by markdown sections.
    
    Args:
        content: The markdown content to split
        max_lines: Maximum lines per split
        
    Returns:
        List of split dictionaries with metadata
    """
    lines = content.split('\n')
    total_lines = len(lines)
    
    if total_lines <= max_lines:
        return [{
            'content': content,
            'title': 'Full Document',
            'start_line': 1,
            'end_line': total_lines,
            'line_count': total_lines
        }]
    
    splits = []
    current_split_lines = []
    current_start = 1
    current_title = "Part"
    split_count = 1
    
    for i, line in enumerate(lines, 1):
        current_split_lines.append(line)
        
        # Check if we hit a section boundary and are near limit
        is_section_boundary = re.match(r'^#+\s+', line.strip())
        approaching_limit = len(current_split_lines) >= max_lines * 0.8
        
        if len(current_split_lines) >= max_lines or (is_section_boundary and approaching_limit):
            # Create split
            split_content = '\n'.join(current_split_lines)
            splits.append({
                'content': split_content,
                'title': f"Part {split_count}",
                'start_line': current_start,
                'end_line': i,
                'line_count': len(current_split_lines)
            })
            
            # Reset for next split
            current_split_lines = []
            current_start = i + 1
            split_count += 1
    
    # Handle remaining lines
    if current_split_lines:
        split_content = '\n'.join(current_split_lines)
        splits.append({
            'content': split_content,
            'title': f"Part {split_count}",
            'start_line': current_start,
            'end_line': total_lines,
            'line_count': len(current_split_lines)
        })
    
    return splits


def split_by_phases(content: str) -> List[Dict[str, Any]]:
    """Split file by implementation phases.
    
    Args:
        content: The markdown content to split
        
    Returns:
        List of split dictionaries, one per phase
    """
    lines = content.split('\n')
    splits = []
    current_split_lines = []
    current_phase = None
    current_start = 1
    
    for i, line in enumerate(lines, 1):
        # Check for phase markers
        phase_match = re.search(r'#+\s+Phase\s+(\d+)', line, re.IGNORECASE)
        
        if phase_match:
            # Close previous split
            if current_split_lines:
                split_content = '\n'.join(current_split_lines)
                title = f"Phase {current_phase}" if current_phase else "Overview"
                splits.append({
                    'content': split_content,
                    'title': title,
                    'phase_number': current_phase,
                    'start_line': current_start,
                    'end_line': i - 1,
                    'line_count': len(current_split_lines)
                })
            
            # Start new split
            current_phase = int(phase_match.group(1))
            current_split_lines = [line]
            current_start = i
        else:
            current_split_lines.append(line)
    
    # Handle final split
    if current_split_lines:
        split_content = '\n'.join(current_split_lines)
        title = f"Phase {current_phase}" if current_phase else "Full Document"
        phase_info = {'phase_number': current_phase} if current_phase else {}
        splits.append({
            'content': split_content,
            'title': title,
            'start_line': current_start,
            'end_line': len(lines),
            'line_count': len(current_split_lines),
            **phase_info
        })
    
    # If no phases found, return entire content
    if not splits:
        splits = [{
            'content': content,
            'title': 'Full Document',
            'start_line': 1,
            'end_line': len(lines),
            'line_count': len(lines)
        }]
    
    return splits


def split_at_lines(content: str, line_numbers: List[int]) -> List[Dict[str, Any]]:
    """Split at specified line numbers.
    
    Args:
        content: The content to split
        line_numbers: Line numbers where splits should occur
        
    Returns:
        List of split dictionaries
    """
    lines = content.split('\n')
    total_lines = len(lines)
    
    if not line_numbers:
        return [{
            'content': content,
            'title': 'Full Document',
            'start_line': 1,
            'end_line': total_lines,
            'line_count': total_lines
        }]
    
    # Sort and deduplicate line numbers
    split_points = sorted(set(line_numbers))
    
    splits = []
    current_start = 1
    
    for split_line in split_points:
        if split_line >= total_lines:
            continue
            
        # Create split from current_start to split_line
        split_lines = lines[current_start - 1:split_line]
        split_content = '\n'.join(split_lines)
        
        splits.append({
            'content': split_content,
            'title': f"Lines {current_start}-{split_line}",
            'start_line': current_start,
            'end_line': split_line,
            'line_count': len(split_lines)
        })
        
        current_start = split_line + 1
    
    # Handle remaining lines after final split
    if current_start <= total_lines:
        remaining_lines = lines[current_start - 1:]
        split_content = '\n'.join(remaining_lines)
        
        splits.append({
            'content': split_content,
            'title': f"Lines {current_start}-{total_lines}",
            'start_line': current_start,
            'end_line': total_lines,
            'line_count': len(remaining_lines)
        })
    
    return splits


def generate_split_files(original: str, splits: List[Dict[str, Any]], output_dir: str) -> List[str]:
    """Generate split files with metadata and cross-references.
    
    Args:
        original: Original filename
        splits: List of split dictionaries
        output_dir: Directory to write split files
        
    Returns:
        List of created file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    
    created_files = []
    original_name = Path(original).stem
    original_ext = Path(original).suffix
    
    for i, split in enumerate(splits, 1):
        # Generate filename
        filename = f"{original_name}-part{i}{original_ext}"
        file_path = os.path.join(output_dir, filename)
        
        # Create content with metadata header
        metadata_header = f"""<!-- Split from {original} -->
<!-- Part {i} of {len(splits)} -->
<!-- Lines {split['start_line']}-{split['end_line']} ({split['line_count']} lines) -->

"""
        
        full_content = metadata_header + split['content']
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        created_files.append(file_path)
    
    return created_files


def _suggest_section_splits(sections: List[Dict[str, Any]], max_lines: int = 500) -> List[Dict[str, Any]]:
    """Suggest optimal split points based on sections.
    
    Args:
        sections: List of section metadata
        max_lines: Maximum lines per split
        
    Returns:
        List of suggested split configurations
    """
    suggestions = []
    current_chunk_lines = 0
    current_chunk_sections = []
    
    for section in sections:
        section_lines = section['line_count']
        
        # If adding this section would exceed limit, finish current chunk
        if current_chunk_lines + section_lines > max_lines and current_chunk_sections:
            suggestions.append({
                'sections': current_chunk_sections.copy(),
                'total_lines': current_chunk_lines,
                'start_line': current_chunk_sections[0]['start_line'],
                'end_line': current_chunk_sections[-1]['end_line']
            })
            
            # Start new chunk
            current_chunk_sections = [section]
            current_chunk_lines = section_lines
        else:
            # Add section to current chunk
            current_chunk_sections.append(section)
            current_chunk_lines += section_lines
    
    # Add final chunk
    if current_chunk_sections:
        suggestions.append({
            'sections': current_chunk_sections,
            'total_lines': current_chunk_lines,
            'start_line': current_chunk_sections[0]['start_line'],
            'end_line': current_chunk_sections[-1]['end_line']
        })
    
    return suggestions