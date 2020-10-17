import shutil
from datetime import datetime
from pathlib import Path
from time import sleep, time_ns
from typing import Optional

import typer as typer
from fs import open_fs


DEFAULT_BYTE_COUNT = 5_000_000

__version__ = "1.0.0"


def version_callback(value: bool):
    if value:
        typer.echo(f"Egon {__version__}")
        raise typer.Exit()


BRAILLE_EMPTY = "⠀"
BRAILLE_FULL = "⣿"

UP_DOWN_UP_BRAILLE = [BRAILLE_EMPTY, "⣀", "⣤", "⣶", BRAILLE_FULL, "⣶", "⣤", "⣀"]
DOWN_BLOCK_BRAILLE = ["⠛", "⠶", "⣤"]
UP_BLOCK_BRAILLE = ["⣤", "⠶", "⠛"]
DOWN_BRAILLE = ["⠉", "⠒", "⠤", "⣀", " "]
UP_BRAILLE = [BRAILLE_EMPTY, "⣀", "⠤", "⠒", "⠉"]

# verbosity levels
DEBUG = 4
VERBOSE = 3
TWO_LINES = 2
ONE_LINE = 1
SILENT = 0


def get_path_size(fs, verbose):
    if verbose == DEBUG:
        print(f"Getting paths and sizes from {fs}...")
    elif verbose == VERBOSE:
        print(f"Getting paths and sizes from {fs}...", end="")
    d = {}
    for path, info in fs.walk.info(namespaces=["details"]):
        if info.is_file:
            # print(f"{path}: {info.size}")
            d[path] = info.size
    if verbose == DEBUG:
        print(f"Found {len(d)} files.")
    elif verbose == VERBOSE:
        print(f" found {len(d)} files.")
    return d


def get_required_paths(destination_fs, source_fs, verbose):
    if verbose in [DEBUG, VERBOSE, TWO_LINES]:
        print("Syncing...", end="\r")
    source_index = get_path_size(source_fs, verbose)
    destination_index = get_path_size(destination_fs, verbose)
    required = required_files(source_index, destination_index, verbose)
    if not required:
        message = "No files needed to be retrieved."
    elif len(required) == 1:
        message = (
            f"One single file ({convert_bytes(required[0][1])}) needs to be retrieved."
        )
    else:
        total_bytes = sum([t[1] for t in required])
        message = f"{len(required)} files ({convert_bytes(total_bytes)}) need to be retrieved."
    if verbose in [DEBUG, VERBOSE, TWO_LINES]:
        print(message)
    return required


def required_files(source, destination, verbose):
    required = []
    for path, size in source.items():
        if path not in destination:
            if verbose == DEBUG:
                print(f"{path} not in destination.")
            required.append((path, size))
        elif size != destination[path]:
            if verbose == DEBUG:
                print(
                    f"{path} in destination, but different size "
                    f"({size} != {destination[path]})."
                )
            required.append((path, size))
    return required


# used for defaults
remote_base = Path("/home/jw/docker/torrent/download/complete")
remote_host = "elevenbits"
remote_user = "jw"


def egon(
    source: str = typer.Argument(
        f"ssh://{remote_user}@{remote_host}{remote_base}", help="The remote source."
    ),
    destination: str = typer.Argument(f"/home/jw/Downloads", help="The destination."),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        help="Logging level; -v means quiet, -vvvv means debug.",
        count=True,
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    ),
):
    """Copies all files from the source folder to the destination folder."""
    if not Path(destination).is_dir():
        return -1
    print("Linking...", end="\r")
    with open_fs(source) as source_fs, open_fs(destination) as destination_fs:
        required = get_required_paths(destination_fs, source_fs, verbose)
        if required:
            download(source_fs, destination_fs, required, DOWN_BRAILLE, verbose)


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
    return f"{convert_bytes(processed_bytes + extra_bytes)}/{convert_bytes(size)}"


def get_progress_percentage(processed_bytes, extra_bytes, size):
    return f"{(processed_bytes / size * 100):.2f}%"


def eta(start_time, processed_bytes, extra_bytes, size):
    now = time_ns()
    processed_time = now - start_time
    estimated_seconds_left = size / processed_bytes * processed_time / 1_000_000_000
    estimated_end_date = datetime.fromtimestamp(
        start_time / 1_000_000_000 + estimated_seconds_left
    )
    return f"{estimated_end_date:%H:%M:%S} ({int(estimated_seconds_left)}s)"


def download(source_fs, destination_fs, required, spinner, verbose):
    start_time = time_ns()
    empties = 0
    total_bytes = sum([t[1] for t in required])
    for i, (path, size) in enumerate(required, start=1):
        destination_fs.makedirs(str(Path(path).parents[0]), recreate=True)
        terminal_size = shutil.get_terminal_size()
        with destination_fs.openbin(path, "w") as local_file, source_fs.openbin(
            path
        ) as remote_file:
            some_bytes = remote_file.read(DEFAULT_BYTE_COUNT)
            j = 0
            processed_bytes = 0
            file_start_time = time_ns()
            while some_bytes:
                block_start_time = time_ns()
                terminal_size = shutil.get_terminal_size()
                local_file.write(some_bytes)
                j += 1
                processed_bytes += len(some_bytes)
                some_bytes = remote_file.read(DEFAULT_BYTE_COUNT)
                block_end_time = time_ns()
                by_second = 1_000_000_000 / (block_end_time - block_start_time)
                message = (
                    f"{spinner[j % len(spinner)]} "
                    f"{get_progress_percentage(processed_bytes, len(some_bytes), size)} "
                    f"[{get_progress_bytes(processed_bytes, len(some_bytes), size)}] "
                    f"{DEFAULT_BYTE_COUNT / 1_000_000 * by_second:.2f}MBps: "
                    f"{Path(path).name} (eta: {eta(start_time, processed_bytes, len(some_bytes), size)})."
                )
                print(
                    f"{message}{' ' * (terminal_size.columns - len(message) - 1)}",
                    end="\r",
                    flush=True,
                )
            file_end_time = time_ns()
        if size != 0 and verbose != SILENT:
            done = (
                f"{BRAILLE_FULL} 100.00% {convert_bytes(size)}: "
                f"{path} (took {(file_end_time - file_start_time) / 1_000_000_000:.2f}s)"
            )
            print(f"{done}{' ' * (terminal_size.columns - len(done) - 1)}")
        else:
            empties += 1

    else:
        end_time = time_ns()
        if verbose != SILENT:
            empties_message = f" ({empties} empty files)" if empties else ""
            print(
                f"Completed {len(required)} files ({convert_bytes(total_bytes)}) "
                f"in {(end_time - start_time) / 1_000_000_000:.2f} seconds{empties_message}."
            )


if __name__ == "__main__":
    try:
        typer.run(egon)
    except Exception as e:
        print()
        print()
        print("Aborted.")
        # print(e)
