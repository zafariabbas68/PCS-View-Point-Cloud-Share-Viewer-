
import numpy as np
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SurveyCalculator:
    """Survey calculations - similar to Aplitop's surveying module"""

    @staticmethod
    def calculate_coordinates(station: dict, observations: list) -> dict:
        """Calculate coordinates from station observations"""
        try:
            # Station setup
            station_x = station.get('x', 0)
            station_y = station.get('y', 0)
            station_z = station.get('z', 0)

            results = []

            for obs in observations:
                # Calculate point coordinates
                distance = obs.get('distance', 0)
                angle = np.radians(obs.get('angle', 0))
                vertical = np.radians(obs.get('vertical', 0))
                height = obs.get('height', 0)

                # Calculate horizontal distance
                horiz_dist = distance * np.cos(vertical)
                dx = horiz_dist * np.sin(angle)
                dy = horiz_dist * np.cos(angle)
                dz = distance * np.sin(vertical)

                point = {
                    "point_id": obs.get('point_id'),
                    "x": round(station_x + dx, 3),
                    "y": round(station_y + dy, 3),
                    "z": round(station_z + dz + height, 3),
                    "distance": round(distance, 3),
                    "angle": round(np.degrees(angle), 3),
                    "vertical": round(np.degrees(vertical), 3)
                }
                results.append(point)

            return {
                "success": True,
                "station": station,
                "points": results,
                "num_points": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def traverse_calculation(stations: list) -> dict:
        """Calculate traverse coordinates"""
        try:
            if len(stations) < 2:
                return {"success": False, "error": "Need at least 2 stations"}

            results = []
            cumulative_x = stations[0].get('x', 0)
            cumulative_y = stations[0].get('y', 0)

            for i, station in enumerate(stations):
                if i > 0:
                    prev = stations[i - 1]
                    dx = station.get('x', 0) - prev.get('x', 0)
                    dy = station.get('y', 0) - prev.get('y', 0)
                    cumulative_x += dx
                    cumulative_y += dy

                results.append({
                    "station_id": station.get('id', i),
                    "x": round(cumulative_x, 3),
                    "y": round(cumulative_y, 3),
                    "z": round(station.get('z', 0), 3)
                })

            return {
                "success": True,
                "stations": results,
                "num_stations": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

