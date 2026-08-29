# DRIFTBOUND — Game Design Document v1.0

**Top-down 2D Pixel Space Action RPG**

> *Survive the void. Salvage the dead. Build a home among the stars.*

---

## 1. Project North Star

Driftbound is a top-down 2D pixel-art space survival action RPG. The player begins alone inside a damaged escape pod with limited oxygen, power, tools, and information. The defining mechanic is that the player's ship is not selected from a menu or upgraded as a single object — it is physically assembled by discovering, clearing, repairing, docking, and repurposing abandoned pods found throughout space.

Every successful expedition should visibly change the player's home.

**Emotional arc:** stranded → capable → established → powerful → curious about what happened here.

### Design Pillars

| Pillar | Description |
|--------|-------------|
| **BUILD THE SHIP YOU LIVE IN** | Progression must be physically visible in the connected pod layout. |
| **DISCOVERY HAS CONSEQUENCES** | An unknown pod can contain safety, loot, enemies, survivors, hazards, or story. |
| **SURVIVAL WITHOUT BUSYWORK** | Oxygen, power, hull condition, and resources create decisions, not constant chores. |
| **SMALL-SCALE SPACE FEELS PERSONAL** | The player's character, rooms, tools, and objects should remain readable and tactile. |
| **MYSTERY DRIVES EXPLORATION** | Every region and derelict should answer one question while creating another. |

---

## 2. Player Fantasy & Core Loop

**Player fantasy:** *"I started with almost nothing, survived the void, and built this strange ship myself from what I found."*

1. Scan nearby space and choose a destination — wreck, asteroid field, signal, or unidentified pod.
2. Travel/explore while managing immediate risks: oxygen, hazards, hostile life, machines, debris.
3. Gather salvage: scrap, metals, crystals, circuitry, fuel, fibers, biological material, blueprints, rare components.
4. Enter or breach discovered structures; clear hazards/enemies.
5. Decide whether a pod is worth recovering.
6. Repair or craft the required docking/connection components.
7. Attach the pod to the player's growing ship.
8. Restore, specialize, furnish, or repurpose the new room.
9. Craft better gear and ship systems, opening access to more dangerous regions.
10. Follow signals and environmental clues toward the larger mystery.

---

## 3. Camera, Presentation & Art Direction

- **Camera:** Top-down / slight three-quarter top-down readability — inspired by classic handheld monster-catching RPG map presentation, but NOT a direct visual copy.
- **Rendering target:** Modern high-detail pixel art; visually closer to a contemporary "32/64-bit-feeling" pixel production than strict 16-bit limitations.
- Tile-based environments — machinery, doors, consoles, pipes, storage, hazards, and room identity must be immediately readable.
- **Lighting:** Emissive screens, warning lights, suit lamps, nebula glow, weapon effects, darkness in unpowered pods.
- Animations smoother than classic handheld RPGs while retaining deliberate pixel construction.
- **Space exterior:** Deep dark backgrounds, colorful nebulae, drifting debris, distant stars, asteroids, derelicts, resource clusters.
- **Interior palette:** Dark industrial metals with strong room-specific accent colors and readable silhouettes.

---

## 4. Player & Controls

| System | MVP Requirement | Later Expansion |
|--------|----------------|-----------------|
| **Movement** | 8-direction; responsive acceleration; collision. | Dash/boost, suit mobility upgrades. |
| **Interaction** | Context interact: doors, loot, consoles, docking, crafting. | Remote tools, hacking, contextual skills. |
| **Combat** | Real-time top-down action combat. | Weapon classes, status effects, builds, companions. |
| **Vitals** | Health + suit/ship oxygen or equivalent expedition pressure. | Radiation, temperature, contamination (region-specific). |
| **Inventory** | Limited but forgiving inventory with hotbar. | Storage networks, auto-sort, filters. |

---

## 5. Ship & Pod System — Signature Feature

The ship is a **connected graph of physical rooms/pods**. A pod has docking points. Once recovered, it attaches to a valid docking point and becomes part of the playable interior. The player walks through the actual connected rooms.

### Pod Recovery States

1. **Detected** — appears as a signal/contact.
2. **Identified** — scan reveals partial info (type, damage, danger, unknowns).
3. **Boarded** — player enters the pod.
4. **Secured** — enemies/hazards/objectives resolved.
5. **Recoverable** — docking requirements known.
6. **Attached** — physically connected to the ship.
7. **Restored** — power/oxygen/basic functionality repaired.
8. **Specialized** — upgraded or repurposed for a chosen function.

### Example Pod Types

| Pod Type | Function |
|----------|----------|
| **Armory** | Weapons, ammo/energy cells, weapon bench, upgrade slots. |
| **Workshop/Fabricator** | Advanced crafting and repair recipes. |
| **Med Bay** | Healing, status recovery, biological research. |
| **Hydroponics/Garden** | Renewable biological resources; food/oxygen bonuses. |
| **Storage/Cargo** | Expands storage and logistics. |
| **Reactor/Power** | Increases ship power budget. |
| **Life Support** | Oxygen capacity, filtration, expedition support. |
| **Navigation/Scanner** | Better map data, signal detection, route options. |
| **Crew Quarters** | Survivor/companion capacity. |
| **Research Lab** | Analyzes artifacts, organisms, technology, and story items. |
| **Unknown/Unique Pods** | One-off story or mechanic rooms. |

---

## 6. Exploration Structure

The game should feel like traveling through **connected pockets of space** rather than a giant empty map. Regions contain navigable exterior zones and points of interest: wrecks, resource clusters, distress signals, stations, asteroids, anomalies, hostile nests, and drifting pods.

| Region Tier | Description |
|-------------|-------------|
| **Early** | Relatively safe salvage field. Teaches movement, oxygen, salvage, first docking. |
| **Mid** | Stronger hazards, locked systems, hostile factions/robots/organisms, multi-room derelicts. |
| **Late** | Severe environmental conditions, rare resources, high-value pods, major story structures. |

**Rule:** Exploration must regularly return something useful — materials, blueprint, pod, lore, shortcut, survivor, upgrade, or new signal.

---

## 7. Combat

Combat is **real-time top-down action** — not turn-based. Readable, quick, and dangerous enough that entering an unidentified pod creates tension.

- **MVP weapon:** Pulse rifle or compact energy weapon with aim/fire/reload or heat behavior.
- **Melee/tool option:** Plasma cutter or salvage tool that doubles as an emergency weapon.
- Enemies telegraph attacks clearly; pixel effects must not obscure hit readability.
- **Environmental combat:** Explosive canisters, electrical panels, vacuum breaches, doors, cover-like machinery.
- **Enemy categories:** Malfunctioning security machines, scavengers, alien organisms, infected/altered entities, and (later) intelligent factions.

---

## 8. Resources, Crafting & Economy

| Resource | Primary Use | Design Note |
|----------|-------------|-------------|
| **Scrap** | Basic repairs / structures | Common universal salvage. |
| **Iron/Alloy** | Hull, tools, pod restoration | Structural material. |
| **Crystal** | Energy systems / advanced gear | More region-dependent. |
| **Circuitry** | Electronics, scanners, automation | Found in technical wreckage. |
| **Fuel/Energy Cells** | Travel and powered systems | Should create planning, not grind. |
| **Fiber/Biomass** | Medical, filters, biological recipes | Supports organic systems. |
| **Rare Components** | Major upgrades / special pods | Gate meaningful progression. |

### Crafting Rules

- Crafting begins simple: health pack, oxygen tank/refill, repair kit, basic ammo/energy, docking component.
- Blueprints unlock new recipes. Important progression recipes should be discoverable through exploration — not random grind.
- Advanced crafting depends on specialized rooms (Workshop, Armory, Med Bay, Research Lab).
- **Do not overload with dozens of near-identical resources during MVP.**

---

## 9. Progression

| Axis | What Improves |
|------|---------------|
| **Character** | Suit capacity, health, oxygen, movement, tool efficiency, weapon handling. |
| **Equipment** | Weapon tiers, mods, salvage tools, scanner, protection modules. |
| **Ship** | More pods, docking options, power, storage, life support, scanner range, travel capability. |
| **Knowledge** | Blueprints, map information, decoded logs, faction/alien understanding. |
| **Access** | New regions require combinations of ship capability, equipment, and story discoveries. |

**Rule:** Avoid simple stat inflation as the only reward. The best upgrades unlock a new action, destination, room function, strategy, or way to solve a problem.

---

## 10. Narrative Framework

The opening provides limited context intentionally. The player regains control in a damaged pod and solves immediate survival problems before understanding the larger situation. Story is delivered through:

- Environmental evidence
- Recovered logs
- Strange signals
- Unique pods
- Survivors
- Major derelicts

**Central question:** Why is this region filled with disconnected pods and wreckage, and what caused the collapse/disaster?

**Secondary question:** Who was the player before becoming stranded, and why were they here?

The ship itself becomes a record of the journey — recovered rooms can retain markings, damage, logs, or artifacts from prior owners.

> Avoid locking the final lore too early. Prototype the gameplay mystery first, then write canon around the strongest mechanics.

---

## 11. UI / UX

| Element | Details |
|---------|---------|
| **HUD** | Health, shield/suit integrity, oxygen, compact objective, quick-access hotbar. |
| **Map/Scanner** | Nearby signals, known pods, resources, hazards, home ship marker. |
| **Pod Interaction** | Clear options: Scan, Board, Connect, Leave. Show docking requirements. |
| **Ship Layout Screen** | Readable top-down connected-room diagram with power/function status. |
| **Crafting** | Blueprint list, item preview, required materials, owned/required counts, craft action. |
| **Inventory** | Icon + name + count. Never rely on color alone. |

---

## 12. MVP / Vertical Slice

The first playable milestone must **prove the pod fantasy** before building a large universe.

- [ ] 1 playable character with 8-direction movement and basic animations.
- [ ] 1 starting escape pod/home room.
- [ ] 1 small exterior space/salvage region.
- [ ] 3 resource types minimum.
- [ ] 1 craft station with 4–6 useful recipes.
- [ ] 1 ranged weapon + 1 salvage/melee tool.
- [ ] 2 enemy types.
- [ ] 3 discoverable pods: **Armory**, **Workshop**, one mystery/utility pod.
- [ ] Boarding, clearing, repairing, docking, and walking into an attached pod.
- [ ] Basic ship power/oxygen logic.
- [ ] One short narrative thread leading to a larger signal.
- [ ] Save/load.

### Vertical Slice Success Test

> A new player should be able to start stranded, leave home, gather salvage, fight or evade danger, discover a pod, acquire the resources to recover it, attach it, enter the newly expanded ship, and use the new room function — all within one short session.

---

## 13. Explicit Non-Goals for Early Development

- No procedural galaxy at MVP.
- No massive open-world map.
- No multiplayer until the single-player pod loop is proven.
- No dozens of weapons, resources, factions, or biomes before the core loop works.
- No fully simulated orbital physics requirement.
- No turn-based combat unless playtesting shows action combat fundamentally fails.
- Do not build decorative ship customization before pod connection, room function, and exploration are fun.

---

## 14. Rules for the Game Design Agent

1. Treat the modular pod/ship system as the game's **primary differentiator**. Do not reduce it to a menu-only upgrade system.
2. When proposing features, explain how they improve exploration, survival, pod discovery, ship growth, combat, or mystery.
3. Prioritize a playable vertical slice over content volume.
4. Keep systems understandable enough for a solo/small-team 2D project unless explicitly told to expand scope.
5. Use placeholders for undecided lore — do not invent permanent canon without approval.
6. Maintain top-down modern pixel-art readability in all environment, UI, enemy, and animation recommendations.
7. Every new resource must have a distinct gameplay purpose. Avoid resource bloat.
8. Every pod type must create a meaningful function, decision, or story payoff.
9. When designing a **region**, include: visual identity, hazard, resources, enemy set, pod opportunities, story clue, and progression requirement.
10. When designing an **enemy**, include: silhouette, behavior, attack telegraph, counterplay, drops, and why it belongs in that region.
11. When designing an **item or upgrade**, specify: acquisition, recipe/cost, effect, progression tier, and what new decision it enables.
12. Flag any suggestion that materially increases scope before implementing it.

---

## 15. Open Design Questions

- Does the character physically fly/jet through exterior space, pilot the starting pod, or use a small EVA craft?
- How freeform is pod placement: fixed docking nodes, grid-based attachment, or limited structural rules?
- Can pods be detached/rearranged later?
- Is ship power a global budget or room-by-room network?
- How punishing should oxygen be?
- Death model: reload, rescue/recovery, dropped salvage, clone/med system, or another fiction?
- Will friendly survivors/crew eventually inhabit recovered rooms?
- Hand-authored regions only, procedural encounter placement, or hybrid?
- Final title: Driftbound or replacement?

---

## 16. Immediate Production Order

1. Lock movement scale, character sprite size, tile size, and camera framing.
2. Prototype one starting pod interior.
3. Prototype one exterior salvage area.
4. Implement interaction + inventory + three resources.
5. Implement crafting for repair/docking component.
6. Create one abandoned pod with a hostile encounter.
7. Implement pod secured state and docking.
8. Make attached pod become a seamless walkable room on the home ship.
9. Add one functional reward inside it (Armory recommended).
10. **Only after this loop feels good:** expand enemies, rooms, regions, story, and progression.

---

*DRIFTBOUND — V1 Design North Star*
