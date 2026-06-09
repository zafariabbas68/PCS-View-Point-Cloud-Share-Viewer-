import numpy as np
import open3d as o3d
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class OrthophotoGenerator:
    """Orthophoto generation engine similar to Cube-3d"""
    
    @staticmethod
    def generate_orthophoto(pcd_file: Path, resolution: float = 0.1) -> dict:
        """Generate orthophoto from point cloud"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            points = np.asarray(pcd.points)
            
            # Get bounds
            min_bound = points.min(axis=0)
            max_bound = points.max(axis=0)
            
            # Calculate grid size
            x_range = max_bound[0] - min_bound[0]
            y_range = max_bound[1] - min_bound[1]
            
            cols = int(x_range / resolution) + 1
            rows = int(y_range / resolution) + 1
            
            # Create height map
            height_map = np.full((rows, cols), -np.inf)
            
            # Project points to grid
            for point in points:
                col = int((point[0] - min_bound[0]) / resolution)
                row = int((point[1] - min_bound[1]) / resolution)
                
                if 0 <= col < cols and 0 <= row < rows:
                    if point[2] > height_map[row, col]:
                        height_map[row, col] = point[2]
            
            # Normalize height map for visualization
            valid_mask = height_map > -np.inf
            if np.any(valid_mask):
                min_height = height_map[valid_mask].min()
                max_height = height_map[valid_mask].max()
                
                if max_height > min_height:
                    normalized = (height_map - min_height) / (max_height - min_height)
                else:
                    normalized = np.zeros_like(height_map)
            else:
                normalized = np.zeros_like(height_map)
            
            normalized[~valid_mask] = 0
            
            # Convert to image
            img_array = (normalized * 255).astype(np.uint8)
            img = Image.fromarray(img_array, mode='L')
            
            # Save orthophoto
            ortho_path = pcd_file.parent / f"{pcd_file.stem}_orthophoto.png"
            img.save(ortho_path)
            
            return {
                "success": True,
                "orthophoto_path": str(ortho_path),
                "resolution_m": resolution,
                "width_pixels": cols,
                "height_pixels": rows,
                "area_sqm": x_range * y_range
            }
            
        except Exception as e:
            logger.error(f"Orthophoto generation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def generate_contour_lines(pcd_file: Path, interval: float = 1.0) -> dict:
        """Generate contour lines from point cloud"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            points = np.asarray(pcd.points)
            
            z_values = points[:, 2]
            min_z = np.floor(z_values.min())
            max_z = np.ceil(z_values.max())
            
            contour_levels = np.arange(min_z, max_z + interval, interval)
            
            return {
                "success": True,
                "min_elevation": float(min_z),
                "max_elevation": float(max_z),
                "contour_interval": interval,
                "number_of_contours": len(contour_levels),
                "contour_levels": contour_levels.tolist()
            }
        except Exception as e:
            logger.error(f"Contour generation error: {str(e)}")
            return {"success": False, "error": str(e)}
