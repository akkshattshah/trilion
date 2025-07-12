const { createCanvas } = require('canvas');
const fs = require('fs');

// Create canvas
const width = 800;
const height = 200;
const canvas = createCanvas(width, height);
const ctx = canvas.getContext('2d');

// Create gradient
const gradient = ctx.createLinearGradient(0, 0, width, 0);
gradient.addColorStop(0, '#8B9EFF');   // Blue
gradient.addColorStop(0.5, '#B76EFF'); // Purple
gradient.addColorStop(1, '#FF6B6B');   // Coral/Red

// Set text properties
ctx.fillStyle = gradient;
ctx.font = 'bold 120px Arial';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';

// Draw text
ctx.fillText('Trilion', width/2, height/2);

// Save to PNG
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync('trilion-logo.png', buffer); 