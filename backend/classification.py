import numpy as np
import open3d as o3d
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PointCloudClassifier:
    """Point cloud classification engine similar to Cube-3d"""
    
    @staticmethod
    def classify_by_height(pcd_file: Path, height_thresholds: list = None) -> dict:
        """Classify points by height/elevation"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            points = np.asarray(pcd.points)
            
            if height_thresholds is None:
                height_thresholds = [-2, 0, 2, 5, 10]
            
            z_values = points[:, 2]
            min_z, max_z = z_values.min(), z_values.max()
            
            classifications = {}
            colors = []
            
            for i, point in enumerate(points):
                z = point[2]
                if z < height_thresholds[1]:
                    classification = "low_vegetation"
                    color = [0, 255, 0]  # Green
                elif z < height_thresholds[2]:
                    classification = "medium_vegetation"
                    color = [0, 200, 0]
                elif z < height_thresholds[3]:
                    classification = "high_vegetation"
                    color = [0, 150, 0]
                elif z < height_thresholds[4]:
                    classification = "building"
                    color = [255, 0, 0]  # Red
                else:
                    classification = "other"
                    color = [255, 255, 0]  # Yellow
                
                classifications[i] = classification
                colors.append(color)
            
            return {
                "success": True,
                "total_points": len(points),
                "classifications": {
                    "low_vegetation": sum(1 for c in classifications.values() if c == "low_vegetation"),
                    "medium_vegetation": sum(1 for c in classifications.values() if c == "medium_vegetation"),
                    "high_vegetation": sum(1 for c in classifications.values() if c == "high_vegetation"),
                    "building": sum(1 for c in classifications.values() if c == "building"),
                    "other": sum(1 for c in classifications.values() if c == "other")
                },
                "colored_points": colors[:1000]  # Sample for preview
            }
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def classify_by_intensity(pcd_file: Path) -> dict:
        """Classify points by intensity (if available)"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            points = np.asarray(pcd.points)
            
            # Check if intensity data exists (custom attribute)
            has_intensity = hasattr(pcd, 'intensity')
            
            if not has_intensity:
                return {
                    "success": False,
                    "error": "No intensity data available in point cloud"
                }
            
            intensities = np.asarray(pcd.intensity)
            classifications = {
                "low_intensity": int(np.sum(intensities < 33)),
                "medium_intensity": int(np.sum((intensities >= 33) & (intensities < 66))),
                "high_intensity": int(np.sum(intensities >= 66))
            }
            
            return {
                "success": True,
                "classifications": classifications,
                "total_points": len(points)
            }
        except Exception as e:
            logger.error(f"Intensity classification error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def ground_classification(pcd_file: Path) -> dict:
        """Classify ground vs non-ground points"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            
            # Use statistical outlier removal for ground filtering
            cl, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
            ground_points = pcd.select_by_index(ind)
            non_ground_points = pcd.select_by_index(ind, invert=True)
            
            return {
                "success": True,
                "ground_points": len(ground_points.points),
                "non_ground_points": len(non_ground_points.points),
                "total_points": len(pcd.points),
                "ground_percentage": round(len(ground_points.points) / len(pcd.points) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Ground classification error: {str(e)}")
            return {"success": False, "error": str(e)}
