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
            
            if len(points) == 0:
                return {"success": False, "error": "No points in point cloud"}
            
            if height_thresholds is None:
                # Calculate percentiles for adaptive thresholds
                z_values = points[:, 2]
                height_thresholds = [
                    np.percentile(z_values, 10),
                    np.percentile(z_values, 30),
                    np.percentile(z_values, 60),
                    np.percentile(z_values, 85)
                ]
            
            classifications = {
                "low_vegetation": 0,
                "medium_vegetation": 0,
                "high_vegetation": 0,
                "building": 0,
                "other": 0
            }
            
            for point in points:
                z = point[2]
                if z < height_thresholds[1]:
                    classifications["low_vegetation"] += 1
                elif z < height_thresholds[2]:
                    classifications["medium_vegetation"] += 1
                elif z < height_thresholds[3]:
                    classifications["high_vegetation"] += 1
                else:
                    classifications["building"] += 1
            
            return {
                "success": True,
                "total_points": len(points),
                "classifications": classifications,
                "thresholds": {
                    "low": round(height_thresholds[1], 2),
                    "medium": round(height_thresholds[2], 2),
                    "high": round(height_thresholds[3], 2)
                }
            }
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def ground_classification(pcd_file: Path) -> dict:
        """Classify ground vs non-ground points"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            
            # Use statistical outlier removal for ground filtering
            cl, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
            
            # Simple ground estimation: points below 2m from lowest point
            points = np.asarray(pcd.points)
            if len(points) > 0:
                min_z = points[:, 2].min()
                ground_threshold = min_z + 2.0
                
                ground_indices = points[:, 2] <= ground_threshold
                ground_points = np.sum(ground_indices)
                non_ground_points = len(points) - ground_points
                
                return {
                    "success": True,
                    "ground_points": int(ground_points),
                    "non_ground_points": int(non_ground_points),
                    "total_points": len(points),
                    "ground_percentage": round(ground_points / len(points) * 100, 2) if len(points) > 0 else 0,
                    "ground_threshold_m": round(ground_threshold, 2),
                    "min_elevation_m": round(min_z, 2)
                }
            else:
                return {"success": False, "error": "No points to classify"}
                
        except Exception as e:
            logger.error(f"Ground classification error: {str(e)}")
            return {"success": False, "error": str(e)}
