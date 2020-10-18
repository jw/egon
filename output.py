import os


def convert_bytes(some_bytes: int) -> str:
    if some_bytes == 0:
        return "empty"
    elif some_bytes < 2000:
        return f"{some_bytes} bytes"
    elif some_bytes < 2_000_000:
        return f"{some_bytes / 1000:.2f} kilobytes"
    elif some_bytes < 2_000_000_000:
        return f"{some_bytes / 1000 / 1000:.2f} megabytes"
    elif some_bytes < 2_000_000_000_000:
        return f"{some_bytes / 1000 / 1000 / 1000:.2f} gigabytes"
    else:
        return f"{some_bytes / 1000 / 1000 / 1000 / 1000:.2f} terabytes"


def get_progress_bytes(processed_bytes, extra_bytes, size):
    return (
        f"{convert_bytes(processed_bytes + extra_bytes)}/{convert_bytes(size)}"
    )


def get_progress_percentage(processed_bytes, extra_bytes, size):
    return f"{(processed_bytes / size * 100):.2f}%"
