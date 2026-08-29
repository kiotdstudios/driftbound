with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. SAVE / LOAD FUNCTIONS — inject before the boot() function
# ══════════════════════════════════════════════════════════════════
BOOT_ANCHOR = "// ─── BOOT ─────────────────────────────────────────────────────────────────────"
SAVE_BLOCK = """// ─── SAVE / LOAD ─────────────────────────────────────────────────────────────

const SAVE_KEY = 'driftbound_save_v1';

function saveGame() {
  const data = {
    worldX:       ship.worldX,
    worldY:       ship.worldY,
    ore:          ship.ore,
    mineral:      ship.mineral,
    armalcolite:  ship.armalcolite,
    fuel:         ship.fuel,
    hp:           ship.hp,
    cargoLimit:   ship.shipType.cargoLimit,
    attachedPods: attachedPods.map(p => p.pid),
    worldPodsLeft: worldPods.map(p => p.pid),
    savedAt:      Date.now(),
  };
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify(data));
  } catch(e) { console.warn('Save failed:', e); }
}

function loadGame() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return false;
    const data = JSON.parse(raw);

    ship.worldX       = data.worldX       || 0;
    ship.worldY       = data.worldY       || 0;
    ship.ore          = data.ore          || 0;
    ship.mineral      = data.mineral      || 0;
    ship.armalcolite  = data.armalcolite  || 0;
    ship.fuel         = data.fuel         ?? FUEL_CAPACITY;
    ship.hp           = data.hp           ?? 100;

    // Restore cargo limit (pod bonuses)
    if (data.cargoLimit && data.cargoLimit > CARGO_LIMIT) {
      ship.shipType.cargoLimit = data.cargoLimit;
    }

    // Restore attached pods
    if (data.attachedPods) {
      data.attachedPods.forEach(pid => {
        // Find which pod type this was
        const wpod = worldPods.find(p => p.pid === pid);
        if (wpod) {
          attachedPods.push({ ...POD_TYPES[wpod.type], pid });
        }
      });
    }

    // Remove world pods that were already collected
    if (data.worldPodsLeft) {
      for (let i = worldPods.length - 1; i >= 0; i--) {
        if (!data.worldPodsLeft.includes(worldPods[i].pid)) {
          worldPods.splice(i, 1);
        }
      }
    }

    return true;
  } catch(e) {
    console.warn('Load failed:', e);
    return false;
  }
}

function deleteSave() {
  localStorage.removeItem(SAVE_KEY);
  showToast('SAVE DELETED — RELOADING...', '#ef4444');
  setTimeout(() => location.reload(), 1500);
}

// Auto-save every 30 seconds + on key events
let _autoSaveTimer = 0;
function tickAutoSave() {
  _autoSaveTimer++;
  if (_autoSaveTimer >= 1800) {   // 30s at 60fps
    _autoSaveTimer = 0;
    saveGame();
  }
}

// ─── BOOT ─────────────────────────────────────────────────────────────────────"""

if BOOT_ANCHOR in d:
    d = d.replace(BOOT_ANCHOR, SAVE_BLOCK)
    fixes.append('save/load functions injected')
else:
    fixes.append('boot anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 2. CALL loadGame() in boot() after loadAll()
# ══════════════════════════════════════════════════════════════════
BOOT_LOAD_ANCHOR = "  await loadAll();\r\n\r\n  initAsteroids();"
BOOT_LOAD_NEW    = ("  await loadAll();\r\n\r\n"
                    "  initAsteroids();\r\n\r\n"
                    "  // Restore saved progress\r\n"
                    "  const hadSave = loadGame();\r\n"
                    "  if (hadSave) showToast('GAME LOADED', '#22c55e');")
if BOOT_LOAD_ANCHOR in d:
    d = d.replace(BOOT_LOAD_ANCHOR, BOOT_LOAD_NEW)
    fixes.append('loadGame() called in boot()')
else:
    fixes.append('boot loadAll anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 3. CALL tickAutoSave() in the game loop (after tickParticles)
# ══════════════════════════════════════════════════════════════════
TICK_ANCHOR = "  tickParticles();\r\n\r\n  drawParticles();"
TICK_NEW    = "  tickParticles();\r\n  tickAutoSave();\r\n\r\n  drawParticles();"
if TICK_ANCHOR in d:
    d = d.replace(TICK_ANCHOR, TICK_NEW)
    fixes.append('tickAutoSave in game loop')
else:
    fixes.append('tick anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 4. SAVE ON ORE COLLECT — after showToast for ore/armalcolite pickup
#    Also save when pod is attached (already has showToast line)
# ══════════════════════════════════════════════════════════════════
# Save when refine happens (C key)
OLD_REFINE_SAVE = "    if (ship.armalcolite > 0) {\r\n"
NEW_REFINE_SAVE = "    if (ship.armalcolite > 0) {\r\n"
# We'll hook saveGame() after the pod attach toast instead
OLD_POD_TOAST = "        showToast('POD ATTACHED  +' + (podType.cargoBonus||0) + ' CARGO', '#38bdf8');"
NEW_POD_TOAST = "        showToast('POD ATTACHED  +' + (podType.cargoBonus||0) + ' CARGO', '#38bdf8');\r\n        saveGame();"
if OLD_POD_TOAST in d:
    d = d.replace(OLD_POD_TOAST, NEW_POD_TOAST)
    fixes.append('saveGame on pod attach')
else:
    fixes.append('pod toast anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 5. SAVE HUD INDICATOR + DELETE key shortcut
#    Add tiny save indicator to HUD (top-right, below modules)
#    and bind Delete key to wipe save
# ══════════════════════════════════════════════════════════════════
# Add Delete key handler near the key input section
OLD_KEY_HANDLER = "document.addEventListener('keydown', e => {"
NEW_KEY_HANDLER = """document.addEventListener('keydown', e => {
  if (e.code === 'Delete' && confirm('Delete save data and reset?')) { deleteSave(); return; }"""
if OLD_KEY_HANDLER in d:
    d = d.replace(OLD_KEY_HANDLER, NEW_KEY_HANDLER, 1)  # only first occurrence
    fixes.append('Delete key = wipe save')
else:
    fixes.append('keydown handler: NO MATCH')

# Add save timestamp display in drawAttachedPods
OLD_ATTACHED = """function drawAttachedPods(cx, cy) {
  if (!attachedPods.length) return;
  // Draw small icons on HUD (top-right corner)
  ctx.save();
  ctx.textAlign = 'right';
  ctx.font = '11px Courier New';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText('MODULES:', canvas.width - 14, 28);
  attachedPods.forEach((p, i) => {
    ctx.fillStyle = p.color || '#38bdf8';
    ctx.fillText('⬡ ' + p.label, canvas.width - 14, 28 + (i+1)*16);
  });
  ctx.restore();
}"""
NEW_ATTACHED = """function drawAttachedPods(cx, cy) {
  // Draw modules + save indicator top-right
  ctx.save();
  ctx.textAlign = 'right';
  ctx.font = '11px Courier New';
  // Auto-save flash indicator
  const saveFlash = _autoSaveTimer > 1780;   // last 20 frames of 30s cycle
  if (saveFlash) {
    ctx.fillStyle = '#22c55e';
    ctx.fillText('● SAVING...', canvas.width - 14, 16);
  }
  if (attachedPods.length) {
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('MODULES:', canvas.width - 14, 28);
    attachedPods.forEach((p, i) => {
      ctx.fillStyle = p.color || '#38bdf8';
      ctx.fillText('⬡ ' + p.label, canvas.width - 14, 28 + (i+1)*16);
    });
  }
  ctx.restore();
}"""
if OLD_ATTACHED in d:
    d = d.replace(OLD_ATTACHED, NEW_ATTACHED)
    fixes.append('drawAttachedPods save indicator')
else:
    fixes.append('drawAttachedPods: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
