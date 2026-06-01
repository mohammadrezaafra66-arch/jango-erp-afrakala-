# Windows Task Scheduler for Bot Panel

The bot panel one-shot runner is already available at:

```text
scripts/run_bot_panel_once.ps1
```

Use Windows Task Scheduler to run this file on a fixed interval.

Recommended MVP interval:

```text
Every 5 minutes
```

Task Scheduler values:

```text
Program: powershell.exe
Arguments: -ExecutionPolicy Bypass -File .\scripts\run_bot_panel_once.ps1
Start in: project root folder
```

The runner writes logs here:

```text
logs/bot_panel_runner
```

Before enabling the scheduled task, test the runner manually from the project root:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\run_bot_panel_once.ps1
```

Expected result when there are no pending requests:

```text
Found 0 pending bot request(s).
Bot panel runner completed successfully
```

Operational rule:

```text
Do not run faster than once per minute.
```
