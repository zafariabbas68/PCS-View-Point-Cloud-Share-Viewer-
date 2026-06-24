
import numpy as np
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class AlignmentManager:
    """Alignment management - similar to Aplitop's alignment tools"""

    @staticmethod
    def create_alignment(points: list, name: str) -> dict:
        """Create a new alignment from points"""
        try:
            if len(points) < 2:
                return {"success": False, "error": "Need at least 2 points"}

            # Calculate alignment properties
            total_length = 0
            segments = []

            for i in range(len(points) - 1):
                dx = points[i + 1][0] - points[i][0]
                dy = points[i + 1][1] - points[i][1]
                length = np.sqrt(dx * dx + dy * dy)
                angle = np.arctan2(dy, dx)
                segments.append({
                    "start": points[i],
                    "end": points[i + 1],
                    "length": round(length, 3),
                    "angle": round(np.degrees(angle), 3)
                })
                total_length += length

            return {
                "success": True,
                "name": name,
                "points": points,
                "segments": segments,
                "total_length": round(total_length, 3),
                "num_segments": len(segments)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def import_alignment(file_path: Path) -> dict:
        """Import alignment from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def export_alignment(alignment_data: dict, file_path: Path) -> dict:
        """Export alignment to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(alignment_data, f, indent=2)
            return {"success": True, "path": str(file_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

