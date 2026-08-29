# Parallax Layer Tester

A web-based visual testing application for verifying parallax background layers work correctly with proper depth and speed relationships.

## Purpose

This tool allows you to:
- Test all parallax background sets from the Space Parallax Backgrounds v1 collection
- Visually verify that layers move at correct relative speeds
- Adjust parallax intensity in real-time
- Toggle individual layers on/off for testing
- Compare the flat reference with layered parallax

## Quick Start

Start one of the http server scripts and navigate to localhost URL

## Features

### Background Selection
- Dropdown menu lists all available parallax backgrounds
- background sets: Stellar, Toxic, Vapor, Void
- Select any background to instantly load and test it

### Parallax Controls
- **Mouse Movement**: Move your mouse over the canvas to create parallax effect
  - Move right: layers shift left (creating depth illusion)
  - Move down: layers shift up
- **Intensity Slider**: Adjust parallax strength from 0x to 2x
  - 0 = no parallax (flat static image)
  - 1 = default intensity
  - 2 = double the parallax effect
- **Auto Scroll Toggle**: Enable automatic continuous parallax movement for hands-free testing

### Layer Visibility
- Toggle individual layers on/off with checkboxes
- Compare how each layer contributes to the parallax effect
- See layer info: filename, speed multiplier, and depth

### Visual Feedback
- Canvas shows the full parallax effect with all visible layers
- Flat background (reference image) is always drawn first as a base
- Layers are drawn in order of depth (1=far/farthest, 3=near/closest)
- Layers wrap seamlessly to create infinite parallax

## Layer Architecture

Each parallax background consists of:
- **Flat image**: Reference composite (all layers combined)
- **Layer 1 (far)**: Speed multiplier 0.2 - slowest movement, appears farthest away
- **Layer 2 (mid)**: Speed multiplier 0.5 - medium movement, middle distance
- **Layer 3 (near)**: Speed multiplier 1.0 - fastest movement, appears closest

All layers should have transparent backgrounds (PNG with alpha) to create the depth effect when composited.

## What to Look For

When testing, verify:
- **Smooth movement**: No jittering or stuttering as mouse moves
- **Proper depth**: Far layers should appear to move slower than near layers
- **Seamless wrapping**: No visible edges when layers wrap around
- **Alignment**: All layers should be aligned on the flat reference when parallax offset is zero
- **Transparency**: Layers blend correctly with no artifacts

## Troubleshooting

**No images appear:**
- Check browser console for 404 errors
- Ensure the assets folder path is correct in `index.html` (line ~195: `assetBasePath`)
- Verify assets exist at the expected location

**Images load but no parallax effect:**
- Ensure JavaScript is enabled
- Check browser console for errors
- Move your mouse over the canvas area

**Performance issues:**
- Ensure you're using a modern browser with hardware acceleration
- Close other browser tabs
- Try a lower intensity setting

## File Structure

```
parallax_tester/
├── index.html              # Main application (HTML + CSS + JS)
├── parallax_config.json    # Configuration for all backgrounds
├── README.md               # This file
└── assets/                 # (Symlink or copy of source assets)
    ├── flat/               # Flat reference images
    └── layers/             # Layer images (L1_far, L2_mid, L3_near)
```

## Technical Details

- Single-file HTML application (no build step required)
- Uses Canvas API for rendering
- Self-contained: no external libraries
- Real-time parallax calculation based on mouse position
- Bilinear image filtering for smooth scaling
- Wrapping algorithm ensures seamless infinite scrolling

## Browser Compatibility

Tested on:
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

Requires:
- JavaScript ES6+
- Canvas API
- Fetch API

## Notes

- The `assetBasePath` variable in the HTML file points to the production assets by default.
- If you want to copy assets locally, change this path to a relative path like `./assets/`
- For local development without a server, some browsers may restrict loading local files via `file://` protocol. Use a local HTTP server.

---

## LICENSE
Free to use whichever way you want

**Version**: 1.0  
**Created**: 2026-03-07  
**Target**: Space Parallax Backgrounds v1
**Author**: hollowpixeldev@gmail.com
