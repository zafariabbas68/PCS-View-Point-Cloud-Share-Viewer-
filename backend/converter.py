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
    Supports Stonex native formats.
    """
    try:
        logger.info(f"Starting conversion: {input_path} -> {output_path}")

        # Check if input file exists
        if not input_path.exists():
            return {"success": False, "error": f"Input file not found: {input_path}"}

        logger.info(f"Input file size: {input_path.stat().st_size} bytes")

        # Read point cloud
        pcd = o3d.io.read_point_cloud(str(input_path))

        if len(pcd.points) == 0:
            logger.error("Point cloud has no points!")
            return {"success": False, "error": "No points found in file"}

        num_points = len(pcd.points)
        logger.info(f"Loaded {num_points} points")

        # For web performance, limit to 500,000 points
        original_points = num_points
        if num_points > 500_000:
            logger.info(f"Downsampling from {num_points} to 500,000 points")
            # Use voxel downsampling for better quality
            voxel_size = 0.05
            pcd = pcd.voxel_down_sample(voxel_size)
            num_points = len(pcd.points)
            logger.info(f"After downsampling: {num_points} points")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to PLY (binary format is smaller and faster)
        success = o3d.io.write_point_cloud(str(output_path), pcd, write_ascii=False)

        if not success:
            return {"success": False, "error": "Open3D write_point_cloud returned False"}

        # Verify output file was created
        if not output_path.exists():
            return {"success": False, "error": "Output file was not created"}

        file_size = output_path.stat().st_size
        logger.info(f"Successfully saved to {output_path} ({file_size} bytes)")

        metadata = {
            "success": True,
            "original_points": original_points,
            "display_points": num_points,
            "file_size_bytes": file_size,
            "has_colors": pcd.has_colors(),
            "has_normals": pcd.has_normals(),
            "converted_at": datetime.now().isoformat()
        }

        return metadata

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
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
            surface_area = mesh.get_surface_area()

            return {
                "success": True,
                "volume_cubic_meters": round(volume, 3),
                "surface_area_sq_meters": round(surface_area, 3),
                "point_count": len(points)
            }
        except:
            # Fallback: bounding box volume estimation
            min_bound = points.min(axis=0)
            max_bound = points.max(axis=0)
            bbox_volume = np.prod(max_bound - min_bound)

            return {
                "success": True,
                "volume_cubic_meters": round(bbox_volume, 3),
                "volume_estimation_method": "bounding_box",
                "point_count": len(points)
            }

    except Exception as e:
        return {"error": str(e)}


def get_point_cloud_info(pcd_file: Path) -> dict:
    """Extract comprehensive metadata from a point cloud."""
    try:
        pcd = o3d.io.read_point_cloud(str(pcd_file))
        points = np.asarray(pcd.points)

        if len(points) == 0:
            return {"error": "No points in point cloud"}

        min_bound = points.min(axis=0)
        max_bound = points.max(axis=0)

        return {
            "point_count": len(pcd.points),
            "has_colors": pcd.has_colors(),
            "has_normals": pcd.has_normals(),
            "bounds": {
                "min": min_bound.tolist(),
                "max": max_bound.tolist()
            },
            "center": points.mean(axis=0).tolist(),
            "span": (max_bound - min_bound).tolist()
        }
    except Exception as e:
        return {"error": str(e)}