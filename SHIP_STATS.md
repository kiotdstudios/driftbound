# DRIFTBOUND — Ship Stats & Game Constants
> Edit values here as reference. To apply changes, update the matching `const` in `driftbound_flight_test.html`.

---

## ⬡ VAGRANT (Active Ship)
| Attribute       | Value  | Notes                                      |
|-----------------|--------|--------------------------------------------|
| Cargo Limit     | 50     | Nebulite + Armalcolite share the hold      |
| Accepts         | ore, armalcolite | Mineral Material is bonus, no hold cost |
| Description     | General-purpose miner                      |

---

## 🚀 Movement & Physics
| Constant        | Value  | Notes                                      |
|-----------------|--------|--------------------------------------------|
| THRUST          | 0.18   | Acceleration per frame (normal)            |
| NORMAL_MAX      | 0.65   | Max speed without boost                    |
| BOOST_THRUST    | 0.42   | Acceleration per frame (boost)             |
| BOOST_MAX       | 5.28   | Max speed while boosting                   |
| BOOST_RAMP_UP   | 0.022  | How fast boost builds                      |
| BOOST_RAMP_DOWN | 0.006  | How fast boost decays when released        |
| FRICTION        | 0.984  | Velocity multiplier per frame (0.984 = slow drift) |
| BRAKE           | 0.88   | Velocity multiplier when braking           |
| SPEED_THRESH    | 0.12   | Min speed before snapping to 0             |

---

## 🛡️ Hull & Combat
| Constant         | Value | Notes                                      |
|------------------|-------|--------------------------------------------|
| SHIP_MAX_HP      | 100   | Max hull points                            |
| COLLISION_RADIUS | 28    | Asteroid collision detection radius (px)   |
| COLLISION_BOUNCE | 0.45  | Velocity multiplier on asteroid bounce     |
| COLLISION_DAMAGE | 8     | Hull damage per asteroid hit               |
| COLLISION_IFRAMES| 60    | Invincibility frames after asteroid hit    |
| PVP_COLLISION_R  | 56    | Ship-to-ship collision radius (2x normal)  |
| PVP_DAMAGE       | 6     | Hull damage per PVP collision              |
| PVP_IFRAMES      | 90    | Invincibility frames after PVP hit         |
| PVP_BOUNCE       | 0.6   | Velocity multiplier on PVP bounce          |

> **Death:** At 0 HP, ship explodes and respawns after **4 seconds** at world origin ±150px.

---

## ⛏️ Mining
| Constant       | Value | Notes                                      |
|----------------|-------|--------------------------------------------|
| MINE_RANGE     | 140   | World-px radius to begin mining            |
| MINE_INTERVAL  | 20    | Frames between each mine hit               |
| MINE_DAMAGE    | 1     | HP damage dealt to asteroid per hit        |

### Asteroid Types
| Type       | HP | Ore Drop | Loot Type    | Loot Chance |
|------------|----|----------|--------------|-------------|
| sm_brown   | 3  | 1–2      | Mineral Mat  | 2%          |
| lg_brown   | 5  | 2–3      | Mineral Mat  | 2%          |
| lg_planet  | 6  | 3–5      | Armalcolite  | 100%        |

### Ore / Minerals
| Resource       | Key          | Cargo Cost | Source            | Use                          |
|----------------|--------------|------------|-------------------|------------------------------|
| Nebulite       | ore          | 1 per unit | All asteroids     | 5 ore → 2 fuel               |
| Armalcolite    | armalcolite  | 1 per unit | lg_planet only    | 1 unit → 2 fuel (direct)     |
| Mineral Mat    | mineral      | 0 (bonus)  | 2% drop all rocks | Crafting component (future)  |

---

## ⛽ Fuel
| Constant       | Value | Notes                                      |
|----------------|-------|--------------------------------------------|
| FUEL_CAPACITY  | 10.0  | Max fuel (gallons displayed)               |
| FUEL_MPG       | 27    | Miles per gallon                           |
| PIXELS_PER_MILE| 300   | World pixels per mile                      |
| ORE_PER_FUEL   | 5     | Nebulite needed to craft 1 fuel batch      |
| FUEL_PER_CRAFT | 2.0   | Fuel gained per craft action               |

---

## 🌍 World
| Constant    | Value | Notes                                      |
|-------------|-------|--------------------------------------------|
| WORLD_SPREAD| 4000  | World radius (asteroids spawn within this) |
| AST_COUNT   | 30    | Number of asteroids active at once         |
| AST_SCALE   | 2     | Sprite scale multiplier for asteroids      |
| ORE_COLLECT_R| 50   | Radius to auto-collect ore pickups (px)    |

---

## 🎨 HUD
| Constant    | Value              | Notes                    |
|-------------|--------------------|--------------------------|
| HUD_FONT    | 26px Courier New   | Primary HUD text         |
| HUD_FONT_SM | 22px Courier New   | Secondary HUD text       |
| HUD_COLOR   | #4FC3C3 (teal)     | Main accent color        |
| HUD_DIM     | #4FC3C380 (50% teal)| Dim label color         |

---

## 🕹️ Display
| Constant      | Value | Notes                          |
|---------------|-------|--------------------------------|
| SPRITE_SIZE   | 68    | Raw sprite sheet frame size    |
| DISPLAY_SCALE | 2     | Render scale (68 → 136px ship) |
| FRAME_COUNT   | 9     | Animation frames per direction |
| ANIM_FPS      | 12    | Animation playback speed       |
