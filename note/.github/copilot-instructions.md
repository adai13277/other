# AutoFighter - AI Agent Guidance

## Project Overview

**AutoFighter** is a game automation framework for dungeon/PvE games (Chinese dungeon-style games). It programmatically executes attack combos, ability rotations, and buff management through keyboard/mouse simulation. The system supports multiple character classes with class-specific combat patterns.

**Key Components:**
- [src/main.py](../src/main.py) - Entry point with expiration checking, logging setup, and multi-threading orchestration
- [src/auto_fighter.py](../src/auto_fighter.py) - Combat controller: config loading, buff scheduling, main combat loop
- [src/action_driver.py](../src/action_driver.py) - Low-level action primitives: keyboard/mouse input, timing, heartbeat mechanism
- [config.json](../src/config.json) - Combat profiles (e.g., "牧师拆车", "弓箭手拆贝贝") with action sequences and buff schedules

## Architecture

### Three-Layer Design

1. **Main Loop** ([src/main.py](../src/main.py#L84-L128))
   - Orchestrates two daemon threads: buff thread and main combat thread
   - Monitors expiration date and runtime limits
   - Handles graceful shutdown on KeyboardInterrupt

2. **Combat Controller** ([src/auto_fighter.py](../src/auto_fighter.py))
   - Loads JSON config, parses action sequences and buff timings
   - Manages two parallel buff systems (see "Buff Classification" below)
   - Executes main combat loop with synchronous buff checks via heartbeat callback

3. **Action Driver** ([src/action_driver.py](../src/action_driver.py#L23-L80))
   - PyAutoGUI wrapper with intelligent wait() that:
     - Respects stop_event for responsive shutdown
     - Triggers heartbeat callbacks during waits (for sync buffs)
     - Handles negative sleep duration edge case
   - Class-specific methods: loop_att() (left-right spam), loop_att1() (mage teleport), loop_att3() (archer stance), loop_mushi_pw() (priest AOE)

### Data Flow

`
config.json (JSON profiles)
  
AutoFighter.load_config_from_json()  parses use_config number
  
init_buff_timers()  categorizes SHORTCUTS into threaded/sync lists
  
Two parallel paths:
  A) run_threaded_buffs() [thread]  ticks interval < 100 buffs independently
  B) run() [main]  executes action_sequence, checks sync buffs via heartbeat
`

## Key Patterns & Conventions

### Config Structure (config.json)

- **use_config**: Number string (e.g., "1", "2") selecting active profile
- **configs[N]**: Profile object with:
  - _desc: Human-readable class/purpose (Chinese)
  - ction_sequence: Array of {unction, rgs} to execute in loop
  - SHORTCUTS: Array of {key, interval} for buff/ability timings
  - is_buff: Boolean enabling/disabling buff system
  - 
unTime: Total seconds (-1 for infinite)

### Buff Classification Logic ([src/auto_fighter.py](../src/auto_fighter.py#L63-L100))

`python
# Determines whether buff runs in independent thread (fast) or main loop (safe)
interval < 0         DISABLED (skip)
interval < 100       THREADED (ignores animation lock, extreme speed)
interval >= 100:
  - interval % 10 == 0    THREADED (e.g., 200, 550, 900)
  - interval % 10 != 0    SYNC (waits for action idle, e.g., 777, 888)
`

**Special encoding** for 3-digit numbers (e.g., 888  base 88 + offset):
- Repeating tens digit signals optimization (888 = 88s + safety offset -5)
- Used to encode both interval and safety margin in one number

### Heartbeat Mechanism

[ActionDriver.wait()](../src/action_driver.py#L37-L79) invokes heartbeat_callback() during waits if registered:
- Allows AutoFighter.check_sync_buffs() to trigger sync-mode buffs mid-action
- Prevents recursion via _is_processing_heartbeat lock
- Ensures responsive buff timing without interrupting current action

### Action Methods (Class-Specific Patterns)

All action methods in [ActionDriver](../src/action_driver.py#L125-L195) follow left-right alternation for balanced positioning:

| Method | Use Case | Pattern |
|--------|----------|---------|
| loop_att(keys, lt, rt) | Melee/spellcaster | Hold keys, iterate leftright alternation for lt/rt seconds |
| loop_att1(keys, dt, at) | Mage (teleport d-key) | Left/right teleport (d-key) for dts, then stance attack for ts |
| loop_att3(keys, t) | Archer (no teleport) | Stance-locked, hold keys for 	 seconds per side |
| loop_mushi_pw(stand_t, move_t) | Priest (AOE) | Raid-style: stand, hold-attack, move-attack, repeat |

## Development Workflows

### Running the Bot

`atch
# Windows batch launcher (src/start.cmd)
cd src
conda activate venv313
python -i main.py   # Interactive mode, inspect vars at prompt
`

### Adding a New Character Profile

1. Edit [config.json](../src/config.json): Add new entry to configs
2. Choose ction_sequence from available methods in [ActionDriver](../src/action_driver.py)
3. Define SHORTCUTS with interval rules (see Buff Classification above)
4. Set use_config to your new profile number to activate

**Example (Archer DPS):**
`json
"5": {
  "_desc": "궁수 스피드런",
  "action_sequence": [{"function": "loop_att3", "args": [["a"], 3]}],
  "SHORTCUTS": [
    {"key": "q", "interval": -1},
    {"key": "e", "interval": 500}
  ]
}
`

### Debugging & Logging

- **Log file**: [src/auto_fighter.log](../src/auto_fighter.log) (truncated on each run)
- **Interactive prompt** (python -i): Inspect ighter object, call ighter.request_stop() to gracefully exit
- **Action metadata**: Use @action_meta() decorator (see [ActionDriver](../src/action_driver.py#L12-L18)) to document new actions

### Modifying Low-Level Timing

- Adjust wait() sleep granularity ([ActionDriver.wait()](../src/action_driver.py#L69-L72)): Change max(0.1, ...) to reduce heartbeat latency
- Fix PyAutoGUI failsafe for external interrupts: Set pyautogui.FAILSAFE = False (done globally in [ActionDriver](../src/action_driver.py#L5))

## External Dependencies & Integration

- **PyAutoGUI** ([ActionDriver](../src/action_driver.py#L1)): Cross-platform keyboard/mouse simulation
- **pynput** ([mouse.py](../src/mouse.py)): Alternative mouse controller (imported but not actively used in main flow)
- **Python stdlib**: 	hreading, json, logging, 	ime, datetime, os
- **PyInstaller**: Generates .exe with embedded config; looks for config.json relative to executable ([AutoFighter.__init__](../src/auto_fighter.py#L32-L36))

## Common Pitfalls & Fixes

1. **Negative sleep duration**  Fixed in [ActionDriver.wait()](../src/action_driver.py#L70) with max(0, remaining)
2. **Heartbeat recursion**  Prevented via _is_processing_heartbeat lock in [wait()](../src/action_driver.py#L58-L66)
3. **Config not found**  Check use_config matches a key in configs; exe version looks in exe dir, not working dir
4. **Buffs not triggering**  Verify is_buff: true in config; ensure interval doesn't fall into disabled (<0) category

## Expiration & Authorization

- **EXPIRATION_DATE** in [main.py](../src/main.py#L13): Hardcoded trial expiration (format: "YYYY-MM-DD")
- On expiration, displays Windows MessageBox popup and exits with code 1
- Logs remaining days on startup for transparency
- To extend trial: modify EXPIRATION_DATE and rebuild .exe via PyInstaller

## Thread Safety & Graceful Shutdown

- **stop_event** (threading.Event): Shared across main and buff threads for responsive shutdown
- ighter.request_stop() sets stop_event, allowing current actions to finish
- Main loop checks should_stop() at action boundaries (not mid-action for responsiveness)
- Buff threads check stop_event every 0.1s heartbeat

## PyInstaller Packaging Notes

- Built spec: [AutoFighter.spec](../src/AutoFighter.spec)
- .exe embeds config.json in working directory; looks relative to executable path
- Test exe by running from outside src/ to verify config discovery (exe looks in exe dir, not cwd)
