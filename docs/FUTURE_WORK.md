# Future Work

## `src/booking/booking.py`

1. Add new CLI feature
    - **remove task**: `-rm`, `--remove-task`, for remove the schedule task, must have `--user-id` in the command.

---

## `src/monitor/Monitor.py`

1. Watchdog to monitor jobs/monitor_exec

2. Balance the GPUs Usage Rate
   - After reboot system, re-schedule the gpus assign, change the order of assign mechanician.

3. Avoid Assign Duplicate GPUs
    - Scheduling algorithm to re-schedule the gpus assign to get the better assign method.

---

## Idle Container

> Create an idle container, letting users that are not running the booking container can access the server to move the files.
>
### `Idle.Dockerfile`

Base on `Dokcerfile`.

- user name: idle
- shell setup
- welcome message
- install python env tool & some dotfile

### `src/monitor/run_container.py`

#### `run_idle_container()`

- cpus: 0.5
- volume like `run_container()`
