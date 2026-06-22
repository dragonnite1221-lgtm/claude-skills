# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin2:
    def _parse_events(self, events_data: List[Dict]) -> List[Event]:
        """Parse raw event data into normalized Event objects."""
        events = []
        
        for event_dict in events_data:
            try:
                # Parse timestamp
                timestamp_str = event_dict.get("timestamp", event_dict.get("time", ""))
                if not timestamp_str:
                    continue
                
                timestamp = self._parse_timestamp(timestamp_str)
                if not timestamp:
                    continue
                
                # Extract other fields
                source = event_dict.get("source", "unknown")
                event_type = self._classify_event_type(event_dict)
                message = event_dict.get("message", event_dict.get("description", ""))
                severity = self._parse_severity(event_dict.get("severity", event_dict.get("level", "unknown")))
                actor = event_dict.get("actor", event_dict.get("user", "system"))
                
                # Extract metadata
                metadata = {k: v for k, v in event_dict.items() 
                           if k not in ["timestamp", "time", "source", "type", "message", "severity", "actor"]}
                
                event = Event(
                    timestamp=timestamp,
                    source=source,
                    type=event_type,
                    message=message,
                    severity=severity,
                    actor=actor,
                    metadata=metadata
                )
                
                events.append(event)
                
            except Exception as e:
                # Skip invalid events but log them
                continue
        
        return events
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse various timestamp formats."""
        # Common timestamp formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO with microseconds
            "%Y-%m-%dT%H:%M:%SZ",     # ISO without microseconds
            "%Y-%m-%d %H:%M:%S",      # Standard format
            "%m/%d/%Y %H:%M:%S",      # US format
            "%d/%m/%Y %H:%M:%S",      # EU format
            "%Y-%m-%d %H:%M:%S.%f",   # With microseconds
            "%Y%m%d_%H%M%S",          # Compact format
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                # Ensure timezone awareness
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        
        # Try parsing as Unix timestamp
        try:
            timestamp_float = float(timestamp_str)
            return datetime.fromtimestamp(timestamp_float, tz=timezone.utc)
        except ValueError:
            pass
        
        return None
    def _classify_event_type(self, event_dict: Dict) -> str:
        """Classify event type based on source and content."""
        source = event_dict.get("source", "").lower()
        message = event_dict.get("message", "").lower()
        event_type = event_dict.get("type", "").lower()
        
        # Check explicit type first
        if event_type in self.event_types:
            return event_type
        
        # Classify based on source and content
        for type_name, type_info in self.event_types.items():
            # Check source patterns
            if any(src in source for src in type_info["sources"]):
                return type_name
            
            # Check message indicators
            if any(indicator in message for indicator in type_info["indicators"]):
                return type_name
        
        return "unknown"
    def _parse_severity(self, severity_str: str) -> int:
        """Parse severity string to numeric value."""
        severity_clean = str(severity_str).lower().strip()
        return self.severity_mapping.get(severity_clean, 0)
