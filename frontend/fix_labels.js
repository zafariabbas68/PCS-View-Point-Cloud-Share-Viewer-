// ===== FIXED: CREATE TEXT LABEL (works in all browsers) =====
function createTextLabel(text, position, color = '#dc2626', size = 0.5, bgColor = 'rgba(255,255,255,0.95)') {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 128;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Font settings
    ctx.font = 'bold 42px Inter, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Measure text
    const metrics = ctx.measureText(text);
    const padding = 24;
    const width = metrics.width + padding * 2;
    const height = 64;
    const x = (canvas.width - width) / 2;
    const y = (canvas.height - height) / 2;
    
    // Background with shadow (using simple rect for compatibility)
    ctx.shadowColor = 'rgba(0,0,0,0.2)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 2;
    ctx.fillStyle = bgColor;
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
    
    // Border
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.stroke();
    
    // Text
    ctx.fillStyle = color;
    ctx.font = 'bold 38px Inter, Arial, sans-serif';
    ctx.fillText(text, canvas.width/2, canvas.height/2 + 4);
    
    // Create texture and sprite
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        sizeAttenuation: true,
        opacity: 1.0
    });
    const sprite = new THREE.Sprite(material);
    sprite.position.copy(position);
    // Position the label slightly above the point
    sprite.position.y += 1.0;
    // Scale the sprite
    const scale = size * 0.025;
    sprite.scale.set(scale * 4.5, scale * 1.1, 1);
    
    console.log('Label created:', text, 'at position:', position);
    return sprite;
}

// ===== FIXED: DRAW LINE WITH LABEL =====
function drawLineWithLabel(p1, p2, color = 0x2563eb) {
    const dist = p1.distanceTo(p2);
    const midPoint = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
    const labelText = `${dist.toFixed(3)} units`;
    
    console.log('Drawing line with label:', labelText);
    
    // Draw the line
    const pts = [p1, p2];
    const geometry = new THREE.BufferGeometry().setFromPoints(pts);
    const material = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
    const line = new THREE.Line(geometry, material);
    scene.add(line);
    cadDrawings.push(line);
    
    // Add label on the line
    const label = createTextLabel(labelText, midPoint, '#2563eb', 0.6);
    scene.add(label);
    cadDrawings.push(label);
    
    // Update panel
    document.getElementById('measureResult').innerHTML = `📏 Distance: ${dist.toFixed(3)} units`;
    document.getElementById('statusMsg').innerHTML = `Distance: ${dist.toFixed(3)} units`;
    updateCADList();
    
    return { line, label, distance: dist };
}

// ===== FIXED: AREA WITH LABEL INSIDE POLYGON =====
function completeAreaWithLabel(areaPoints) {
    if (areaPoints.length < 3) {
        console.log('Not enough points for area:', areaPoints.length);
        return null;
    }
    
    console.log('Completing area with', areaPoints.length, 'points');
    
    // Calculate area using shoelace formula
    let area = 0;
    const n = areaPoints.length;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        area += areaPoints[i].x * areaPoints[j].z;
        area -= areaPoints[j].x * areaPoints[i].z;
    }
    area = Math.abs(area) / 2;
    
    // Calculate perimeter
    let perimeter = 0;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        const dx = areaPoints[i].x - areaPoints[j].x;
        const dz = areaPoints[i].z - areaPoints[j].z;
        perimeter += Math.sqrt(dx*dx + dz*dz);
    }
    
    // Find center for label
    const center = new THREE.Vector3();
    areaPoints.forEach(p => center.add(p));
    center.divideScalar(areaPoints.length);
    center.y += 0.5; // Lift label slightly above the polygon
    
    const labelText = `Area: ${area.toFixed(3)} sq units`;
    
    console.log('Area label:', labelText, 'at center:', center);
    
    // Add area label inside polygon (gold color)
    const label = createTextLabel(labelText, center, '#d4af37', 0.6);
    scene.add(label);
    cadDrawings.push(label);
    
    // Draw the polygon border
    const pts = areaPoints.map(p => p.clone());
    pts.push(pts[0].clone());
    const geometry = new THREE.BufferGeometry().setFromPoints(pts);
    const material = new THREE.LineBasicMaterial({ color: 0xd4af37, linewidth: 2 });
    const polygon = new THREE.Line(geometry, material);
    scene.add(polygon);
    cadDrawings.push(polygon);
    
    // Update panel
    document.getElementById('areaResult').innerHTML = `📐 ${labelText} | Perimeter: ${perimeter.toFixed(3)} units (${n} sides)`;
    document.getElementById('statusMsg').innerHTML = `${labelText}`;
    
    showMessage(`Area: ${area.toFixed(3)} sq units`, 'success');
    updateCADList();
    
    return { area, perimeter, label, labelText };
}
