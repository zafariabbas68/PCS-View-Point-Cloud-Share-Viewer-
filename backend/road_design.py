
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RoadDesign:
    """Road design tools - similar to Aplitop's road design"""

    @staticmethod
    def calculate_superelevation(speed: float, radius: float, pavement: float = 0.02) -> dict:
        """Calculate superelevation based on speed and radius"""
        try:
            # Standard formula for superelevation
            g = 9.81
            v = speed / 3.6  # km/h to m/s

            # Superelevation = (v²)/(g*R) - pavement friction
            e = (v ** 2) / (g * radius) - pavement

            # Limit to reasonable values
            e = max(min(e, 0.08), -0.08)  # 8% max superelevation

            return {
                "success": True,
                "speed": speed,
                "radius": radius,
                "superelevation": round(e * 100, 2),  # as percentage
                "superelevation_ratio": round(e, 4),
                "pavement_friction": pavement
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def design_template(width: float, lanes: int, shoulder: float = 0.5) -> dict:
        """Design road template"""
        try:
            lane_width = width / lanes

            template = {
                "success": True,
                "total_width": width,
                "lanes": lanes,
                "lane_width": round(lane_width, 3),
                "shoulder_width": shoulder,
                "elements": []
            }

            # Left side
            template["elements"].append({
                "side": "left",
                "type": "shoulder",
                "width": shoulder
            })

            for i in range(lanes):
                template["elements"].append({
                    "side": "left",
                    "type": "lane",
                    "width": lane_width,
                    "lane_number": i + 1
                })

            # Right side (mirror)
            for i in range(lanes):
                template["elements"].append({
                    "side": "right",
                    "type": "lane",
                    "width": lane_width,
                    "lane_number": i + 1
                })

            template["elements"].append({
                "side": "right",
                "type": "shoulder",
                "width": shoulder
            })

            return template
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def calculate_earthwork_volume(cross_sections: list) -> dict:
        """Calculate earthwork volumes using average end area method"""
        try:
            if len(cross_sections) < 2:
                return {"success": False, "error": "Need at least 2 cross sections"}

            total_cut = 0
            total_fill = 0

            for i in range(len(cross_sections) - 1):
                cs1 = cross_sections[i]
                cs2 = cross_sections[i + 1]
                distance = cs2.get("station", 0) - cs1.get("station", 0)

                cut_area1 = cs1.get("cut_area", 0)
                fill_area1 = cs1.get("fill_area", 0)
                cut_area2 = cs2.get("cut_area", 0)
                fill_area2 = cs2.get("fill_area", 0)

                # Average end area method
                cut_volume = (cut_area1 + cut_area2) / 2 * distance
                fill_volume = (fill_area1 + fill_area2) / 2 * distance

                total_cut += cut_volume
                total_fill += fill_volume

            return {
                "success": True,
                "total_cut_volume": round(total_cut, 3),
                "total_fill_volume": round(total_fill, 3),
                "net_volume": round(total_fill - total_cut, 3),
                "num_sections": len(cross_sections)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

