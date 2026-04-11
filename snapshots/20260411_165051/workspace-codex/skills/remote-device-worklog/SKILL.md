---
name: remote-device-worklog
description: Document remote device repairs, installs, diagnostics, and configuration work in a durable on-device work-instructions folder. Use when an agent SSHes into a Jetson, Nano, Raspberry Pi, workstation, server, or other remote box and performs meaningful work that should be written down as an operating manual entry. Especially use after browser fixes, service repairs, package installs, hardware setup, networking changes, AI/model runtime changes, or any repeated maintenance task.
---

# Remote Device Worklog

When you fix or improve a remote machine, leave behind documentation on that machine so the work is repeatable.

## Default pattern
Create or reuse a top-level desktop folder like:
- `JETSON_WORK_INSTRUCTIONS/`
- `DEVICE_WORK_INSTRUCTIONS/`
- or another device-specific equivalent if one already exists

Inside it, maintain categories such as:
- `00_INDEX/`
- `01_TEMPLATES/`
- `10_SYSTEM/`
- `20_BROWSERS/`
- `30_NETWORK/`
- `40_SERVICES/`
- `50_AI_MODELS/`
- `60_AUTOMATION/`
- `70_HARDWARE/`
- `90_ARCHIVE/`

## What to document
For each meaningful repair/install/change, write a markdown entry that includes:
1. Summary
2. Symptoms
3. Root cause
4. Environment
5. Investigation path
6. Commands run
7. What changed
8. Validation
9. Caveats / risks
10. Follow-up ideas

Keep the write-up concrete. Include the exact commands and the real reason the fix worked.

## Rules
- Prefer **one detailed durable doc** over scattered ad hoc notes.
- Do not just record the happy ending. Record what was broken and how you reasoned about it.
- If the final fix is a workaround rather than a true root-level repair, say that clearly.
- Add or update an index/work-log file so future readers can find the entry quickly.
- If you create a reusable template, store it under `01_TEMPLATES/`.

## Naming guidance
Use dated filenames for detailed repair notes, for example:
- `2026-04-09_CHROMIUM_REPAIR.md`
- `2026-04-09_SSH_RECOVERY.md`
- `2026-04-09_TAILSCALE_SETUP.md`

Use stable filenames for summaries/status:
- `README.md`
- `BROWSER_STATUS.md`
- `WORK_LOG.md`

## Workflow
1. Detect where the device should keep durable local work instructions.
2. Create the folder structure if it does not exist.
3. Write a detailed markdown entry for the task you just completed.
4. Update the work log/index.
5. If the structure itself is useful, create a reusable template.
6. Verify the files exist on the remote device.

## Tooling
Use the bundled script to bootstrap the folder structure quickly:

```bash
bash skills/remote-device-worklog/scripts/bootstrap_worklog.sh \
  "$HOME/Desktop/JETSON_WORK_INSTRUCTIONS"
```

Then write the task-specific markdown file into the appropriate category.

For structure guidance, read `references/worklog-structure.md`.
