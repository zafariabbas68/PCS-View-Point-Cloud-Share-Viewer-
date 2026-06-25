// ===== CONTOUR GENERATION (Updated) =====
window.generateContours = async function(interval) {
    if (!currentModel) {
        showMessage('Load a point cloud first', 'warning');
        return;
    }

    // Clear previous contours
    contourLines.forEach(obj => scene.remove(obj));
    contourLines = [];
    contourLabels.forEach(obj => scene.remove(obj));
    contourLabels = [];

    showMessage('Generating contours...', 'info');

    try {
        const response = await fetch(`/api/contours/generate/${currentModel}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                interval: interval || 1.0,
                grid_size: 150,
                smooth: 0.5
            })
        });

        const data = await response.json();

        if (!data.success || !data.contours || data.contours.length === 0) {
            showMessage('No contours could be generated', 'warning');
            return;
        }

        // Visualize contours
        const colors = {
            major: 0xdc2626,  // Red for major contours
            minor: 0xf59e0b   // Orange for minor contours
        };

        data.contours.forEach(contour => {
            if (contour.points.length < 3) return;

            const pts = contour.points.map(p => new THREE.Vector3(p[0], p[1] + 0.01, p[2]));
            const isMajor = contour.is_major || Math.abs(contour.elevation % (interval * 5)) < 0.01;
            const color = isMajor ? colors.major : colors.minor;

            // Create contour line
            const geometry = new THREE.BufferGeometry().setFromPoints(pts);
            const material = new THREE.LineBasicMaterial({
                color: color,
                linewidth: isMajor ? 2 : 1,
                transparent: true,
                opacity: isMajor ? 1.0 : 0.7
            });
            const line = new THREE.Line(geometry, material);
            scene.add(line);
            contourLines.push(line);
            cadDrawings.push(line);

            // Add elevation label (only for major contours or every 5th contour)
            if (isMajor || contour.points.length > 10) {
                const midIdx = Math.floor(contour.points.length / 2);
                const midPoint = contour.points[midIdx];
                const labelPos = new THREE.Vector3(midPoint[0], midPoint[1] + 0.1, midPoint[2]);
                const label = createTextLabel(`${contour.elevation.toFixed(1)}m`, labelPos, '#dc2626', 0.25);
                scene.add(label);
                contourLabels.push(label);
                cadDrawings.push(label);
            }
        });

        showMessage(`Generated ${data.contours.length} contour lines at ${interval}m interval`, 'success');
        updateCADList();

        // Update the result box
        document.getElementById('contourResult').innerHTML = `
            <div class="row"><span class="label">Interval:</span><span class="value">${interval} m</span></div>
            <div class="row"><span class="label">Lines:</span><span class="value">${data.contours.length}</span></div>
            <div class="row"><span class="label">Major Contours:</span><span class="value red">${data.contours.filter(c => c.is_major || Math.abs(c.elevation % (interval * 5)) < 0.01).length}</span></div>
            <div class="row"><span class="label">Status:</span><span class="value green">Generated ✓</span></div>
        `;

    } catch (error) {
        showMessage(`Contour generation failed: ${error.message}`, 'error');
    }
};
