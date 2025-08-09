#!/usr/bin/env python3
#====== Log Viewer/LogViewer.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Log Viewer MVP - A configurable log parser and viewer
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys
from pathlib import Path


class FieldType(Enum):
    """Supported field types for log categories"""
    DATETIME = "datetime"
    STRING = "string"
    NUMBER = "number"


@dataclass
class LogCategory:
    """Represents a log category from configuration"""
    name: str
    type: str
    order: int
    description: str = ""
    ColourType: str = ""
    Colouring: str = "Text"  # "Text" or "Background"
    ColourMap: Dict[str, str] = field(default_factory=dict)
    
    def get_field_type(self) -> FieldType:
        return FieldType(self.type)
    
    def has_color_config(self) -> bool:
        """Check if this category has color configuration"""
        return bool(self.ColourType and self.ColourMap)
    
    def get_color_for_value(self, value: Any) -> Optional[str]:
        """Get RGB color string for a given value"""
        if not self.has_color_config():
            return None
        
        if self.ColourType == "WholeLine":
            # Direct value matching - supports arrays of values
            str_value = str(value)
            for color, match_value in self.ColourMap.items():
                if self._value_matches(str_value, match_value):
                    return self._rgb_string_to_hex(color)
        
        elif self.ColourType == "LineNumber":
            # Direct value matching for line number coloring - supports arrays of values
            str_value = str(value)
            for color, match_value in self.ColourMap.items():
                if self._value_matches(str_value, match_value):
                    return self._rgb_string_to_hex(color)
        
        elif self.ColourType == "SpecificValue":
            # Range and specific value matching - supports arrays for strings
            if isinstance(value, (int, float)):
                num_value = float(value)
                for color, range_spec in self.ColourMap.items():
                    if self._value_in_range(num_value, range_spec):
                        return self._rgb_string_to_hex(color)
            else:
                # String-based specific value matching with array support
                str_value = str(value)
                for color, match_value in self.ColourMap.items():
                    if self._value_matches(str_value, match_value):
                        return self._rgb_string_to_hex(color)
        
        return None
    
    def _value_matches(self, value: str, match_spec: str) -> bool:
        """Check if value matches specification - supports arrays (comma-separated values)"""
        # Split match_spec by comma to support arrays of values
        match_values = [v.strip() for v in match_spec.split(',') if v.strip()]
        
        # Check if the value matches any of the specified values
        return value in match_values
    
    def _rgb_string_to_hex(self, rgb_string: str) -> str:
        """Convert '122,44,75' to '#7A2C4B'"""
        try:
            r, g, b = map(int, rgb_string.split(','))
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return "#000000"  # Default to black on error
    
    def _value_in_range(self, value: float, range_spec: str) -> bool:
        """Check if value matches range specification like '1-20, 50-65'"""
        ranges = [r.strip() for r in range_spec.split(',')]
        
        for range_part in ranges:
            if '-' in range_part:
                # Range like "1-20" or "50-65"
                try:
                    start, end = map(float, range_part.split('-'))
                    if start <= value <= end:
                        return True
                except ValueError:
                    continue
            else:
                # Single value
                try:
                    if float(range_part.strip()) == value:
                        return True
                except ValueError:
                    continue
        
        return False


@dataclass
class LogEntry:
    """Represents a parsed log entry"""
    raw_text: str
    line_number: int
    fields: Dict[str, Any] = field(default_factory=dict)
    is_multiline: bool = False
    source_file: Optional[str] = None  # Track source file for merged logs
    
    def get_field(self, name: str) -> Any:
        """Get field value by name"""
        return self.fields.get(name)
    
    def __str__(self):
        """String representation for display"""
        parts = []
        for key, value in self.fields.items():
            if isinstance(value, dict):
                value = f"{{{', '.join(f'{k}={v}' for k, v in value.items())}}}"
            elif isinstance(value, list):
                value = f"[{', '.join(str(v) for v in value)}]"
            parts.append(f"{key}: {value}")
        return " | ".join(parts)


class ConfigManager:
    """Manages log viewer configuration"""
    
    def __init__(self, config_path: str = None, config_dict: Dict = None):
        """Initialize with either a config file path or dictionary"""
        if config_path:
            self.config = self._load_config_file(config_path)
        elif config_dict:
            self.config = config_dict
        else:
            raise ValueError("Either config_path or config_dict must be provided")
        
        self._validate_config()
        self._parse_categories()
    
    def _load_config_file(self, path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _validate_config(self):
        """Validate configuration structure"""
        if 'logViewerConfig' not in self.config:
            raise ValueError("Missing 'logViewerConfig' in configuration")
        
        lvc = self.config['logViewerConfig']
        if 'delimiters' not in lvc:
            raise ValueError("Missing 'delimiters' in configuration")
        if 'categories' not in lvc:
            raise ValueError("Missing 'categories' in configuration")
    
    def _parse_categories(self):
        """Parse and sort categories by order"""
        self.categories = []
        for i, cat_dict in enumerate(self.config['logViewerConfig']['categories']):
            # If no order field, use the array index
            if 'order' not in cat_dict:
                cat_dict['order'] = i + 1
            self.categories.append(LogCategory(**cat_dict))
        self.categories.sort(key=lambda x: x.order)
    
    @property
    def delimiters(self) -> Dict[str, str]:
        """Get delimiter configuration"""
        return self.config['logViewerConfig']['delimiters']
    
    def get_category_by_name(self, name: str) -> Optional[LogCategory]:
        """Get category by name"""
        for cat in self.categories:
            if cat.name == name:
                return cat
        return None


class LogParser:
    """Parses log entries based on configuration"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.delimiters = config_manager.delimiters
    
    def parse_file(self, file_path: str) -> List[LogEntry]:
        """Parse entire log file without locking it"""
        # Open file with share mode to allow other processes to read/write
        # Using 'r' mode with buffering=1 for line buffering
        import io
        
        # Read file without exclusive lock - allows other processes to access it
        try:
            # Try Windows-specific approach first for better compatibility
            import os
            if os.name == 'nt':  # Windows
                # Open with FILE_SHARE_READ | FILE_SHARE_WRITE flags
                import msvcrt
                with open(file_path, 'r', encoding='utf-8', buffering=1) as f:
                    # Ensure file is not locked
                    try:
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    except:
                        pass  # File might be in use, but we can still try to read
                    content = f.read()
            else:
                # Unix/Linux - files are not locked by default
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except IOError as e:
            # If file is locked or being written to, try again with a small delay
            import time
            time.sleep(0.1)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                # Return empty list if file cannot be read
                return []
        
        # Check if logs use start/end delimiters for multi-line
        if self.delimiters.get('logStartDelimiter') and self.delimiters.get('logEndDelimiter'):
            logs = self._parse_multiline_logs(content)
        else:
            logs = self._parse_single_line_logs(content)
        
        # Set source file for all entries
        for log in logs:
            log.source_file = file_path
        
        return logs
    
    def _parse_multiline_logs(self, content: str) -> List[LogEntry]:
        """Parse logs that may span multiple lines using delimiters"""
        logs = []
        start_delim_list = self.delimiters['logStartDelimiter']
        end_delim_list = self.delimiters['logEndDelimiter']
        
        # Handle delimiters as arrays - use first delimiter if it's an array
        start_delim = start_delim_list[0] if isinstance(start_delim_list, list) and start_delim_list else start_delim_list
        end_delim = end_delim_list[0] if isinstance(end_delim_list, list) and end_delim_list else end_delim_list
        
        # Find all log entries between delimiters
        pattern = re.escape(start_delim) + r'(.*?)' + re.escape(end_delim)
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for i, match in enumerate(matches, 1):
            log_text = match.group(1).strip()
            entry = self._parse_log_entry(log_text, i, is_multiline='\n' in log_text)
            if entry:
                logs.append(entry)
        
        # If no delimiters found, try line-by-line parsing
        if not logs:
            return self._parse_single_line_logs(content)
        
        return logs
    
    def _parse_single_line_logs(self, content: str) -> List[LogEntry]:
        """Parse logs where each line is a separate entry"""
        logs = []
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                entry = self._parse_log_entry(line.strip(), i)
                if entry:
                    logs.append(entry)
        
        return logs
    
    def _parse_log_entry(self, text: str, line_number: int, is_multiline: bool = False) -> Optional[LogEntry]:
        """Parse a single log entry"""
        if not text:
            return None
        
        entry = LogEntry(raw_text=text, line_number=line_number, is_multiline=is_multiline)
        
        # Split by category separator
        separator_list = self.delimiters['categorySeparator']
        separator = separator_list[0] if isinstance(separator_list, list) and separator_list else separator_list
        parts = text.split(separator)
        
        # Parse each category in order
        for i, category in enumerate(self.config.categories):
            if i < len(parts):
                value = self._parse_field(parts[i].strip(), category)
                entry.fields[category.name] = value
        
        return entry
    
    def _parse_field(self, value: str, category: LogCategory) -> Any:
        """Parse field based on its type"""
        field_type = category.get_field_type()
        
        if field_type == FieldType.DATETIME:
            return self._parse_datetime(value)
        elif field_type == FieldType.NUMBER:
            return self._parse_number(value)
        else:  # STRING or other types
            # Check if value is contained within delimiters
            return self._parse_container_value(value)
    
    def _parse_datetime(self, value: str) -> str:
        """Parse datetime field (keep as string for MVP)"""
        # For MVP, just return the string. 
        # Could enhance with actual datetime parsing later
        return value
    
    def _parse_number(self, value: str) -> Optional[float]:
        """Parse number field"""
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_container_value(self, value: str) -> Any:
        """Parse value that may be contained within delimiters"""
        if not value:
            return value
        
        # Check if value is wrapped in container delimiters
        container_start_list = self.delimiters.get('ContainerStartDelimiter', ['('])
        container_end_list = self.delimiters.get('ContainerEndDelimiter', [')'])
        
        # Check each possible container delimiter
        inner_value = None
        for start_delim, end_delim in zip(
            container_start_list if isinstance(container_start_list, list) else [container_start_list],
            container_end_list if isinstance(container_end_list, list) else [container_end_list]
        ):
            if value.startswith(start_delim) and value.endswith(end_delim):
                # Remove container delimiters
                inner_value = value[len(start_delim):-len(end_delim)].strip()
                break
        
        if inner_value is None:
            # No matching container delimiters found, use original value
            inner_value = value
        
        # Try to parse as structured data (key-value pairs)
        kv_sep_list = self.delimiters['keyValueSeparator']
        kv_sep = kv_sep_list[0] if isinstance(kv_sep_list, list) and kv_sep_list else kv_sep_list
        arr_sep_list = self.delimiters['arrayElementSeparator']
        arr_sep = arr_sep_list[0] if isinstance(arr_sep_list, list) and arr_sep_list else arr_sep_list
        
        if kv_sep in inner_value:
            return self._parse_structured_data(inner_value)
        # Try to parse as array (comma-separated)
        elif arr_sep in inner_value:
            return self._parse_array_data(inner_value)
        # Return as string if no special structure detected
        else:
            return inner_value
    
    def _parse_structured_data(self, value: str) -> Dict[str, str]:
        """Parse structured data (key-value pairs)"""
        result = {}
        
        if not value:
            return result
        
        # Split by key-value pairs separator
        kv_separator_list = self.delimiters['keyValuePairsSeparator']
        kv_separator = kv_separator_list[0] if isinstance(kv_separator_list, list) and kv_separator_list else kv_separator_list
        pairs = value.split(kv_separator)
        
        # Parse each key-value pair
        kv_delim_list = self.delimiters['keyValueSeparator']
        kv_delim = kv_delim_list[0] if isinstance(kv_delim_list, list) and kv_delim_list else kv_delim_list
        for pair in pairs:
            if kv_delim in pair:
                key, val = pair.split(kv_delim, 1)
                result[key.strip()] = val.strip()
        
        return result
    
    def _parse_array_data(self, value: str) -> List[str]:
        """Parse array data (comma-separated values)"""
        if not value:
            return []
        
        separator_list = self.delimiters['arrayElementSeparator']
        separator = separator_list[0] if isinstance(separator_list, list) and separator_list else separator_list
        return [item.strip() for item in value.split(separator) if item.strip()]


class LogViewer:
    """Main log viewer application"""
    
    def __init__(self, config_path: str = None, config_dict: Dict = None):
        """Initialize log viewer with configuration"""
        self.config_manager = ConfigManager(config_path, config_dict)
        self.parser = LogParser(self.config_manager)
        self.logs: List[LogEntry] = []
        self.filtered_logs: List[LogEntry] = []
    
    def load_file(self, file_path: str) -> int:
        """Load and parse log file"""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")
        
        self.logs = self.parser.parse_file(file_path)
        self.filtered_logs = self.logs.copy()
        return len(self.logs)
    
    def display_logs(self, limit: int = None, detailed: bool = False):
        """Display loaded logs"""
        logs_to_display = self.filtered_logs[:limit] if limit else self.filtered_logs
        
        if not logs_to_display:
            print("No logs to display")
            return
        
        print(f"\n{'='*80}")
        print(f"Displaying {len(logs_to_display)} of {len(self.filtered_logs)} logs")
        print('='*80)
        
        for i, log in enumerate(logs_to_display, 1):
            if detailed:
                self._display_detailed(log, i)
            else:
                self._display_compact(log, i)
    
    def _display_compact(self, log: LogEntry, index: int):
        """Display log in compact format"""
        print(f"\n[{index}] Line {log.line_number}: {log}")
    
    def _display_detailed(self, log: LogEntry, index: int):
        """Display log in detailed format"""
        print(f"\n{'='*60}")
        print(f"Log Entry #{index} (Line {log.line_number})")
        print('-'*60)
        
        for category in self.config_manager.categories:
            value = log.get_field(category.name)
            if value is not None:
                if isinstance(value, dict):
                    print(f"{category.name}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                elif isinstance(value, list):
                    print(f"{category.name}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"{category.name}: {value}")
        
        if log.is_multiline:
            print("\n[Multi-line Entry]")
            print("Raw text:")
            print('-'*40)
            print(log.raw_text)
    
    def filter_by_field(self, field_name: str, value: Any, operator: str = "equals"):
        """Simple filtering by field value"""
        filtered = []
        
        for log in self.logs:
            field_value = log.get_field(field_name)
            
            if operator == "equals":
                if field_value == value:
                    filtered.append(log)
            elif operator == "contains":
                if value in str(field_value):
                    filtered.append(log)
            elif operator == "in_array" and isinstance(field_value, list):
                if value in field_value:
                    filtered.append(log)
            elif operator == "has_key" and isinstance(field_value, dict):
                if value in field_value:
                    filtered.append(log)
        
        self.filtered_logs = filtered
        return len(filtered)
    
    def reset_filters(self):
        """Reset filters to show all logs"""
        self.filtered_logs = self.logs.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded logs"""
        stats = {
            'total_logs': len(self.logs),
            'filtered_logs': len(self.filtered_logs),
            'categories': [cat.name for cat in self.config_manager.categories]
        }
        
        # Count by log level if present
        if 'LogLevel' in stats['categories']:
            levels = {}
            for log in self.logs:
                level = log.get_field('LogLevel')
                if level:
                    levels[level] = levels.get(level, 0) + 1
            stats['log_levels'] = levels
        
        return stats


def main():
    """CLI interface for testing"""
    # Example configuration
    config = {
        "logViewerConfig": {
            "delimiters": {
                "logStartDelimiter": "(",
                "logEndDelimiter": ")",
                "categorySeparator": "|",
                "keyValuePairsSeparator": ";",
                "keyValueSeparator": "=",
                "arrayElementSeparator": ","
            },
            "categories": [
                {"name": "Timestamp", "type": "datetime", "order": 1},
                {"name": "LogLevel", "type": "string", "order": 2},
                {"name": "Component", "type": "string", "order": 3},
                {"name": "Details", "type": "string", "order": 4},
                {"name": "Tags", "type": "string", "order": 5},
                {"name": "ErrorCode", "type": "number", "order": 6}
            ]
        }
    }
    
    # Create viewer
    viewer = LogViewer(config_dict=config)
    
    # Example usage
    print("Log Viewer MVP")
    print("-" * 40)
    
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
        try:
            count = viewer.load_file(log_file)
            print(f"Loaded {count} log entries from {log_file}")
            
            # Display stats
            stats = viewer.get_stats()
            print(f"\nStatistics:")
            print(f"  Total logs: {stats['total_logs']}")
            if 'log_levels' in stats:
                print(f"  Log levels: {stats['log_levels']}")
            
            # Display first 5 logs
            viewer.display_logs(limit=5, detailed=False)
            
            # Example filter
            print("\n\nFiltering for ERROR logs...")
            count = viewer.filter_by_field('LogLevel', 'ERROR')
            print(f"Found {count} ERROR logs")
            viewer.display_logs(limit=3, detailed=True)
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python log_viewer.py <log_file>")
        print("\nCreating sample log file for testing...")
        
        # Create a sample log file
        sample_logs = """2025-08-08 06:50:00|INFO|AuthService|(action=login;user=john.doe;status=success)|security,user_activity|0
2025-08-08 06:50:15|ERROR|DatabaseService|(action=query;table=users;error=connection_timeout)|database,critical|1001
2025-08-08 06:50:30|WARNING|CacheService|(action=evict;size=1024MB;reason=memory_pressure)|cache,performance|0
2025-08-08 06:51:00|INFO|APIGateway|(action=request;endpoint=/api/users;method=GET;status=200)|api,monitoring|0
2025-08-08 06:51:15|ERROR|PaymentService|(action=charge;amount=99.99;currency=USD;error=invalid_card)|payment,critical|2003
2025-08-08 06:51:30|DEBUG|AuthService|(action=validate_token;user=jane.smith;result=valid)|security,debug|0"""
        
        with open('sample_logs.txt', 'w') as f:
            f.write(sample_logs)
        
        print("Created 'sample_logs.txt'. Run: python log_viewer.py sample_logs.txt")


if __name__ == "__main__":
    main()