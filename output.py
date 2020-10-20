import os


def convert_bytes(some_bytes: int, short=False) -> str:
    if some_bytes == 0:
        return "empty"
    elif some_bytes < 2000:
        bytes_str = "b" if short else " bytes"
        return f"{some_bytes}{bytes_str}"
    elif some_bytes < 2_000_000:
        kilobytes_str = "kB" if short else " kilobytes"
        return f"{some_bytes / 1000:.2f}{kilobytes_str}"
    elif some_bytes < 2_000_000_000:
        megabytes_str = "MB" if short else " megabytes"
        return f"{some_bytes / 1000 / 1000:.2f}{megabytes_str}"
    elif some_bytes < 2_000_000_000_000:
        gigabytes_str = "GB" if short else " gigabytes"
        return f"{some_bytes / 1000 / 1000 / 1000:.2f}{gigabytes_str}"
    else:
        terabytes_str = "TB" if short else " terabytes"
        return f"{some_bytes / 1000 / 1000 / 1000 / 1000:.2f}{terabytes_str}"


def get_progress_bytes(processed_bytes, extra_bytes, size):
    return (
        f"{convert_bytes(processed_bytes + extra_bytes)}/{convert_bytes(size)}"
    )


def get_progress_percentage(processed_bytes, extra_bytes, size):
    return f"{(processed_bytes / size * 100):.2f}%"
