import numpy as np
import open3d as o3d
from scipy.spatial import Delaunay
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VolumeCalculator:
    """Advanced volume calculation engine similar to Cube-3d"""
    
    @staticmethod
    def calculate_volume(pcd_file: Path, base_elevation: float = None) -> dict:
        """Calculate volume above base elevation"""
        try:
            pcd = o3d.io.read_point_cloud(str(pcd_file))
            points = np.asarray(pcd.points)
            
            if base_elevation is None:
                base_elevation = points[:, 2].min()
            
            # Calculate volume using triangulation
            try:
                # Project points to 2D for triangulation
                xy_points = points[:, :2]
                
                # Create Delaunay triangulation
                tri = Delaunay(xy_points)
                
                volume = 0
                for simplex in tri.simplices:
                    # Get the three points of the triangle
                    p1, p2, p3 = points[simplex]
                    
                    # Calculate average height
                    avg_height = (p1[2] + p2[2] + p3[2]) / 3 - base_elevation
                    
                    if avg_height > 0:
                        # Calculate area of triangle
                        area = VolumeCalculator.triangle_area(p1[:2], p2[:2], p3[:2])
                        volume += area * avg_height
                
                volume = abs(volume)
                
                return {
                    "success": True,
                    "volume_cubic_meters": round(volume, 3),
                    "base_elevation": round(base_elevation, 3),
                    "max_elevation": round(points[:, 2].max(), 3),
                    "area_sqm": round(VolumeCalculator.convex_hull_area(points[:, :2]), 3),
                    "method": "delaunay_triangulation"
                }
                
            except Exception as e:
                # Fallback: voxel-based volume calculation
                return VolumeCalculator.voxel_volume(points, base_elevation)
                
        except Exception as e:
            logger.error(f"Volume calculation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def triangle_area(p1, p2, p3):
        """Calculate area of triangle given 2D points"""
        return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - 
                   (p3[0] - p1[0]) * (p2[1] - p1[1])) / 2
    
    @staticmethod
    def convex_hull_area(points):
        """Calculate convex hull area"""
        from scipy.spatial import ConvexHull
        try:
            hull = ConvexHull(points)
            return hull.volume
        except:
            return 0
    
    @staticmethod
    def voxel_volume(points, base_elevation, voxel_size=0.5):
        """Fallback volume calculation using voxels"""
        # Create voxel grid
        min_bound = points.min(axis=0)
        max_bound = points.max(axis=0)
        
        x_bins = int((max_bound[0] - min_bound[0]) / voxel_size) + 1
        y_bins = int((max_bound[1] - min_bound[1]) / voxel_size) + 1
        
        height_grid = np.full((x_bins, y_bins), base_elevation)
        
        for point in points:
            x_idx = int((point[0] - min_bound[0]) / voxel_size)
            y_idx = int((point[1] - min_bound[1]) / voxel_size)
            if 0 <= x_idx < x_bins and 0 <= y_idx < y_bins:
                if point[2] > height_grid[x_idx, y_idx]:
                    height_grid[x_idx, y_idx] = point[2]
        
        # Calculate volume
        volume = 0
        for i in range(x_bins):
            for j in range(y_bins):
                height = height_grid[i, j] - base_elevation
                if height > 0:
                    volume += height * voxel_size * voxel_size
        
        return {
            "success": True,
            "volume_cubic_meters": round(volume, 3),
            "base_elevation": round(base_elevation, 3),
            "method": "voxel_based",
            "voxel_size": voxel_size
        }
    
    @staticmethod
    def cut_fill_analysis(current_pcd: Path, design_pcd: Path = None) -> dict:
        """Calculate cut and fill volumes between two surfaces"""
        try:
            pcd_current = o3d.io.read_point_cloud(str(current_pcd))
            points_current = np.asarray(pcd_current.points)
            
            if design_pcd and design_pcd.exists():
                pcd_design = o3d.io.read_point_cloud(str(design_pcd))
                points_design = np.asarray(pcd_design.points)
            else:
                # If no design surface, assume flat at lowest point
                base_z = points_current[:, 2].min()
                points_design = np.column_stack([points_current[:, 0], points_current[:, 1], 
                                                  np.full(len(points_current), base_z)])
            
            # Calculate differences
            cuts = []
            fills = []
            
            for i, point in enumerate(points_current):
                if i < len(points_design):
                    diff = point[2] - points_design[i, 2]
                    if diff > 0:
                        fills.append(diff)
                    else:
                        cuts.append(abs(diff))
            
            cut_volume = sum(cuts) * 0.01  # Approximate with unit area
            fill_volume = sum(fills) * 0.01
            
            return {
                "success": True,
                "cut_volume_cubic_meters": round(cut_volume, 3),
                "fill_volume_cubic_meters": round(fill_volume, 3),
                "net_volume": round(fill_volume - cut_volume, 3),
                "analysis_type": "cut_fill"
            }
        except Exception as e:
            logger.error(f"Cut/fill analysis error: {str(e)}")
            return {"success": False, "error": str(e)}
