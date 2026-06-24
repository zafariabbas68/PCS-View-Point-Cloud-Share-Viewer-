
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """Profile generation - similar to Aplitop's profile tools"""

    @staticmethod
    def generate_longitudinal_profile(points: np.ndarray, interval: float = 1.0) -> dict:
        """Generate longitudinal profile from point cloud"""
        try:
            if len(points) < 2:
                return {"success": False, "error": "Not enough points"}

            # Sort points by X coordinate
            sorted_idx = np.argsort(points[:, 0])
            sorted_points = points[sorted_idx]

            # Calculate profile points
            profile = []
            distances = []
            current_dist = 0
            prev_point = sorted_points[0]

            for i in range(len(sorted_points)):
                if i > 0:
                    dx = sorted_points[i][0] - prev_point[0]
                    dy = sorted_points[i][1] - prev_point[1]
                    current_dist += np.sqrt(dx * dx + dy * dy)
                profile.append({
                    "distance": round(current_dist, 3),
                    "x": round(sorted_points[i][0], 3),
                    "y": round(sorted_points[i][1], 3),
                    "z": round(sorted_points[i][2], 3)
                })
                prev_point = sorted_points[i]

            return {
                "success": True,
                "profile": profile,
                "total_distance": round(current_dist, 3),
                "num_points": len(profile),
                "min_elevation": round(sorted_points[:, 2].min(), 3),
                "max_elevation": round(sorted_points[:, 2].max(), 3)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def generate_cross_section(points: np.ndarray, center: list, width: float = 20.0) -> dict:
        """Generate cross section at a specific point"""
        try:
            cx, cy = center[0], center[1]

            # Find points within width
            mask = (np.abs(points[:, 0] - cx) < width) & (np.abs(points[:, 1] - cy) < width)
            nearby = points[mask]

            if len(nearby) < 3:
                return {"success": False, "error": "Not enough points in section"}

            # Sort by distance from center
            distances = np.sqrt((nearby[:, 0] - cx) ** 2 + (nearby[:, 1] - cy) ** 2)
            sorted_idx = np.argsort(distances)
            sorted_points = nearby[sorted_idx]

            section = []
            for p in sorted_points[:100]:
                section.append({
                    "distance": round(np.sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2), 3),
                    "x": round(p[0], 3),
                    "y": round(p[1], 3),
                    "z": round(p[2], 3)
                })

            return {
                "success": True,
                "section": section,
                "center": center,
                "num_points": len(section),
                "width": width
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

