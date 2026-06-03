import open3d as o3d
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported Stonex formats
SUPPORTED_FORMATS = {".las", ".laz", ".ply", ".e57", ".xyz", ".txt", ".cx3d"}


def convert_point_cloud(input_path: Path, output_path: Path) -> dict:
    """
    Convert various point cloud formats to PLY for web visualization.
    Supports Stonex native formats: LAS, LAZ, E57, PLY, XYZ, TXT, CX3D
    Returns metadata about the conversion.
    """
    try:
        logger.info(f"Converting {input_path} -> {output_path}")

        # Read point cloud (Open3D handles multiple formats)
        pcd = o3d.io.read_point_cloud(str(input_path))

        if len(pcd.points) == 0:
            logger.error("Point cloud has no points!")
            return {"success": False, "error": "No points found in file"}

        num_points = len(pcd.points)
        logger.info(f"Loaded {num_points} points")

        # Calculate point cloud statistics
        points = np.asarray(pcd.points)
        min_bound = points.min(axis=0)
        max_bound = points.max(axis=0)
        center = (min_bound + max_bound) / 2

        # Calculate point density estimate
        if num_points > 1:
            bbox_volume = np.prod(max_bound - min_bound)
            density = num_points / bbox_volume if bbox_volume > 0 else 0
        else:
            density = 0

        # Downsample for web performance (if too large)
        original_points = num_points
        if num_points > 2_000_000:
            logger.info(f"Downsampling from {num_points} to 2,000,000 points")
            pcd = pcd.uniform_down_sample(every_k_points=num_points // 2_000_000)
            num_points = len(pcd.points)

        # Write to PLY
        o3d.io.write_point_cloud(str(output_path), pcd, write_ascii=False)

        metadata = {
            "success": True,
            "original_points": original_points,
            "display_points": num_points,
            "min_bound": min_bound.tolist(),
            "max_bound": max_bound.tolist(),
            "center": center.tolist(),
            "point_density": round(density, 4),
            "has_colors": pcd.has_colors(),
            "has_normals": pcd.has_normals(),
            "converted_at": datetime.now().isoformat()
        }

        logger.info(f"Successfully saved to {output_path}")
        return metadata

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        return {"success": False, "error": str(e)}


def calculate_volume(pcd_file: Path) -> dict:
    """Calculate volume for stockpile/earthwork applications."""
    try:
        pcd = o3d.io.read_point_cloud(str(pcd_file))
        points = np.asarray(pcd.points)

        if len(points) < 4:
            return {"error": "Not enough points for volume calculation"}

        # Simple volume calculation using convex hull
        try:
            # Estimate normals first
            pcd.estimate_normals()
            # Poisson surface reconstruction
            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)

            # Calculate volume
            volume = mesh.get_volume()

            # Calculate surface area
            surface_area = mesh.get_surface_area()

            return {
                "success": True,
                "volume_cubic_meters": round(volume, 3),
                "surface_area_sq_meters": round(surface_area, 3),
                "point_count": len(points)
            }
        except:
            # Fallback: voxel-based volume estimation
            voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=0.1)
            voxel_count = len(voxel_grid.get_voxels())
            estimated_volume = voxel_count * 0.001

            return {
                "success": True,
                "volume_cubic_meters": round(estimated_volume, 3),
                "volume_estimation_method": "voxel_based",
                "point_count": len(points)
            }

    except Exception as e:
        return {"error": str(e)}


def get_point_cloud_info(pcd_file: Path) -> dict:
    """Extract comprehensive metadata from a point cloud."""
    try:
        pcd = o3d.io.read_point_cloud(str(pcd_file))
        points = np.asarray(pcd.points)

        return {
            "point_count": len(pcd.points),
            "has_colors": pcd.has_colors(),
            "has_normals": pcd.has_normals(),
            "bounds": {
                "min": points.min(axis=0).tolist(),
                "max": points.max(axis=0).tolist()
            },
            "center": points.mean(axis=0).tolist()
        }
    except Exception as e:
        return {"error": str(e)}