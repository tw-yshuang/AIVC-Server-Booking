# Future Work

## `src/booking/booking.py`

1. Add new CLI feature
    - **remove task**: `-rm`, `--remove-task`, for remove the schedule task, must have `--user-id` in the command.

---

## `src/monitor/Monitor.py`

1. Balance the GPUs Usage Rate
   - After reboot system, re-schedule the gpus assign, change the order of assign mechanician.

2. Avoid Assign Duplicate GPUs
    - Scheduling algorithm to re-schedule the gpus assign to get the better assign method.
