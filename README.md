# bear-export

Super naive implementation of bear exporter that organizes notes by tags into folders.

## Features

- Exports Bear notes to markdown files
- Organizes notes by tags into corresponding folders (e.g., `#tag` → `/tag/`, `#tag/tag2` → `/tag/tag2/`)
- Notes with multiple tags are duplicated into each tag folder
- Includes asset files (images, attachments)
- Automated export via cron job

## Manual Export

Update the output folder path in `export.py` if needed and run:

```bash
python3 export.py
```

## Automated Export (LaunchAgent)

Schedule automatic exports every 30 seconds using the `schedule.sh` script with macOS LaunchAgent.

### One-Time Setup: Grant Python Full Disk Access

To avoid permission prompts, Python needs access to Bear's database:

1. Open **System Settings** → **Privacy & Security** → **Full Disk Access**
2. Click the lock icon to unlock (enter password)
3. Click the **+** button
4. Press **Cmd+Shift+G** and enter the Python path (run `which python3` to find it, typically `/opt/homebrew/bin/python3`)
5. Select `python3` and click **Open**
6. Enable the checkbox next to `python3`

### Start Automated Export

```bash
./schedule.sh start
```

This installs a LaunchAgent that runs the export every 30 seconds. Export logs are written to `export.log`.

### Stop Automated Export

```bash
./schedule.sh stop
```

This removes the LaunchAgent.

### Check Status

```bash
./schedule.sh status
```

Shows whether the LaunchAgent is currently active.

### View Logs

```bash
tail -f export.log
```

Monitor export activity in real-time. 
