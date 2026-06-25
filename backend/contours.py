import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib import cm
import json

def generate_contours(points, interval=1.0, grid_size=100, smooth=1.0):
    """
    Generate proper contour lines from point cloud data using grid interpolation
    
    Args:
        points: numpy array of shape (N, 3) containing x, y, z coordinates
        interval: contour interval in meters
        grid_size: size of the grid for interpolation
        smooth: smoothing factor for the grid
    
    Returns:
        List of contour line segments with elevation values
    """
    if len(points) < 4:
        return []
    
    # Extract coordinates
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    
    # Create grid
    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)
    
    # Add padding
    padding = (x_max - x_min) * 0.05
    x_min -= padding
    x_max += padding
    y_min -= padding
    y_max += padding
    
    # Create grid points
    xi = np.linspace(x_min, x_max, grid_size)
    yi = np.linspace(y_min, y_max, grid_size)
    xi_grid, yi_grid = np.meshgrid(xi, yi)
    
    # Interpolate using LinearNDInterpolator for better results
    coords = np.column_stack((x, y))
    interpolator = LinearNDInterpolator(coords, z, fill_value=np.nan)
    zi = interpolator(xi_grid, yi_grid)
    
    # Handle NaN values
    nan_mask = np.isnan(zi)
    if np.all(nan_mask):
        return []
    
    # Fill NaN values using nearest neighbor
    zi_flat = zi.flatten()
    nan_indices = np.where(nan_mask.flatten())[0]
    if len(nan_indices) > 0:
        valid_indices = np.where(~nan_mask.flatten())[0]
        if len(valid_indices) > 0:
            from scipy.spatial import KDTree
            tree = KDTree(np.column_stack((xi_grid.flatten()[valid_indices], yi_grid.flatten()[valid_indices])))
            for idx in nan_indices:
                point = np.array([xi_grid.flatten()[idx], yi_grid.flatten()[idx]])
                _, nearest = tree.query(point)
                zi_flat[idx] = zi_flat[valid_indices[nearest]]
        zi = zi_flat.reshape(grid_size, grid_size)
    
    # Apply smoothing
    if smooth > 0:
        zi = gaussian_filter(zi, sigma=smooth)
    
    # Determine contour levels
    z_min = np.nanmin(zi)
    z_max = np.nanmax(zi)
    
    if np.isnan(z_min) or np.isnan(z_max):
        return []
    
    # Create contour levels starting from a clean base
    base_level = np.floor(z_min / interval) * interval
    levels = np.arange(base_level, z_max + interval, interval)
    
    # Remove levels outside the data range
    levels = levels[(levels >= z_min - interval/2) & (levels <= z_max + interval/2)]
    
    if len(levels) == 0:
        return []
    
    # Generate contour lines using matplotlib
    contours = []
    
    try:
        # Create contour set
        contour_set = plt.contour(xi_grid, yi_grid, zi, levels=levels)
        
        # Extract contour paths
        for level, collection in zip(contour_set.levels, contour_set.collections):
            paths = collection.get_paths()
            for path in paths:
                vertices = path.vertices
                if len(vertices) > 2:
                    # Convert grid coordinates back to original coordinates
                    # (xi_grid and yi_grid are already in original coordinate space)
                    segments = []
                    for vertex in vertices:
                        segments.append({
                            'x': float(vertex[0]),
                            'y': float(vertex[1]),
                            'z': float(level)
                        })
                    contours.append({
                        'elevation': float(level),
                        'points': segments,
                        'is_major': abs(level % (interval * 5)) < 0.001 or abs(level % (interval * 5) - interval * 5) < 0.001
                    })
        
        plt.close()
        
    except Exception as e:
        plt.close()
        print(f"Contour generation error: {e}")
        return []
    
    return contours

def generate_contour_geojson(contours):
    """Convert contours to GeoJSON format for frontend rendering"""
    features = []
    for contour in contours:
        coordinates = [[p['x'], p['z']] for p in contour['points']]
        # Close the polygon if it's a closed contour
        if len(coordinates) > 2:
            if (coordinates[0][0] - coordinates[-1][0])**2 + (coordinates[0][1] - coordinates[-1][1])**2 < 0.01:
                coordinates.append(coordinates[0])
        
        features.append({
            'type': 'Feature',
            'properties': {
                'elevation': contour['elevation'],
                'is_major': contour.get('is_major', False)
            },
            'geometry': {
                'type': 'LineString' if len(coordinates) > 2 else 'MultiPoint',
                'coordinates': coordinates
            }
        })
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }
