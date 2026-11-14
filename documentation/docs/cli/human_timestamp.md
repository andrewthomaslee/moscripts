# human_timestamp

Prints the current time, human-readable. Defaults to `America/Chicago`.

```sh
human_timestamp                          # 2026-11-14 08:54:54 AM
human_timestamp -t UTC
human_timestamp -t Europe/Helsinki -f '%H:%M'
```

An unknown time zone exits with an error.
