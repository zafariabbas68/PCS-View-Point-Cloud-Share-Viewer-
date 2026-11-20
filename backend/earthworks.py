
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Earthworks:

    @staticmethod
    def calculate_volume_by_surfaces(current_points: np.ndarray, design_points: np.ndarray) -> dict:
        """Calculate volume between two surfaces"""
        try:
            if len(current_points) == 0 or len(design_points) == 0:
                return {"success": False, "error": "Empty point sets"}

            # Create grid
            min_x = min(current_points[:, 0].min(), design_points[:, 0].min())
            max_x = max(current_points[:, 0].max(), design_points[:, 0].max())
            min_y = min(current_points[:, 1].min(), design_points[:, 1].min())
            max_y = max(current_points[:, 1].max(), design_points[:, 1].max())

            grid_size = 0.5
            x_bins = int((max_x - min_x) / grid_size) + 1
            y_bins = int((max_y - min_y) / grid_size) + 1

            # Create height maps
            current_height = np.full((x_bins, y_bins), -np.inf)
            design_height = np.full((x_bins, y_bins), -np.inf)

            # Fill current surface
            for point in current_points:
                xi = int((point[0] - min_x) / grid_size)
                yi = int((point[1] - min_y) / grid_size)
                if 0 <= xi < x_bins and 0 <= yi < y_bins:
                    if point[2] > current_height[xi, yi]:
                        current_height[xi, yi] = point[2]

            # Fill design surface
            for point in design_points:
                xi = int((point[0] - min_x) / grid_size)
                yi = int((point[1] - min_y) / grid_size)
                if 0 <= xi < x_bins and 0 <= yi < y_bins:
                    if point[2] > design_height[xi, yi]:
                        design_height[xi, yi] = point[2]

            # Calculate volumes
            cut_volume = 0
            fill_volume = 0
            valid_cells = 0

            for i in range(x_bins):
                for j in range(y_bins):
                    if current_height[i, j] > -np.inf and design_height[i, j] > -np.inf:
                        diff = current_height[i, j] - design_height[i, j]
                        cell_area = grid_size * grid_size
                        if diff > 0:
                            cut_volume += diff * cell_area
                        else:
                            fill_volume += abs(diff) * cell_area
                        valid_cells += 1

            return {
                "success": True,
                "cut_volume": round(cut_volume, 3),
                "fill_volume": round(fill_volume, 3),
                "net_volume": round(fill_volume - cut_volume, 3),
                "grid_size": grid_size,
                "valid_cells": valid_cells,
                "area_sqm": round(valid_cells * grid_size * grid_size, 3)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def calculate_volume_by_esplanade(points: np.ndarray, elevation: float) -> dict:
        """Calculate volume for esplanade at given elevation"""
        try:
            if len(points) == 0:
                return {"success": False, "error": "No points"}

            # Calculate cut and fill relative to esplanade
            cut_volume = 0
            fill_volume = 0
            area = 0

            # Create grid
            min_x, max_x = points[:, 0].min(), points[:, 0].max()
            min_y, max_y = points[:, 1].min(), points[:, 1].max()

            grid_size = 0.5
            x_bins = int((max_x - min_x) / grid_size) + 1
            y_bins = int((max_y - min_y) / grid_size) + 1

            height_map = np.full((x_bins, y_bins), -np.inf)

            for point in points:
                xi = int((point[0] - min_x) / grid_size)
                yi = int((point[1] - min_y) / grid_size)
                if 0 <= xi < x_bins and 0 <= yi < y_bins:
                    if point[2] > height_map[xi, yi]:
                        height_map[xi, yi] = point[2]

            for i in range(x_bins):
                for j in range(y_bins):
                    if height_map[i, j] > -np.inf:
                        diff = height_map[i, j] - elevation
                        cell_area = grid_size * grid_size
                        area += cell_area
                        if diff > 0:
                            cut_volume += diff * cell_area
                        else:
                            fill_volume += abs(diff) * cell_area

            return {
                "success": True,
                "esplanade_elevation": elevation,
                "cut_volume": round(cut_volume, 3),
                "fill_volume": round(fill_volume, 3),
                "net_volume": round(fill_volume - cut_volume, 3),
                "area_sqm": round(area, 3),
                "grid_size": grid_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

