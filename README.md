

```markdown
# Python Script Background Execution on Raspberry Pi

This repository contains instructions on how to run a Python script in the background on a Raspberry Pi, ensuring that the process continues even after the terminal is closed.

## Steps to Run the Script

### 1. Add Your Program
Save your Python script in the desired location on your Raspberry Pi.

### 2. Run the Script in the Background
Use the following command to start the script in the background:

```bash
nohup python3 /path/to/script.py &
```

- `nohup` prevents the process from terminating when the terminal is closed.
- `&` runs the process in the background.

By default, the output of the script will be saved in a `nohup.out` file.

### 3. Redirect Logs to a Specific File (Optional)
To save logs in a specific file rather than `nohup.out`, run:

```bash
nohup python3 /path/to/script.py > mylogfile.log 2>&1 &
```

This command will:
- Save both standard output and error logs to `mylogfile.log`.

### 4. Check Running Processes
To verify if your script is running, use:

```bash
ps aux | grep python
```

This will show all active Python processes.

### 5. View Logs in Real-Time
To see the log file in real-time, use:

```bash
tail -f nohup.out
```

Or replace `nohup.out` with the name of your log file if you've used a custom one (e.g., `mylogfile.log`).

### 6. Restart the Script
If you need to restart the script, simply re-run the command:

```bash
nohup python3 /path/to/script.py &
```
```

