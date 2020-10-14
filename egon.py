import shutil
from pathlib import Path
from time import sleep

import typer as typer
from fs import open_fs


BRAILLE_EMPTY = "⠀"
BRAILLE_FULL = "⣿"
BRAILLE = [BRAILLE_EMPTY, "⣀", "⣤", "⣶", BRAILLE_FULL, "⣶", "⣤", "⣀"]

DEFAULT_BYTE_COUNT = 5

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
    if verbose in [DEBUG, VERBOSE]:
        print("Syncing...")
    elif verbose == TWO_LINES:
        print("Syncing...", end="")
    source_index = get_path_size(source_fs, verbose)
    destination_index = get_path_size(destination_fs, verbose)
    required = required_files(source_index, destination_index, verbose)
    if not required:
        message = "No files needed to be retrieved."
    elif len(required) == 1:
        message = "One single file needs to be retrieved."
    else:
        message = f"{len(required)} files need to be retrieved."
    if verbose in [DEBUG, VERBOSE]:
        print(message)
    elif verbose == TWO_LINES:
        print(f" {message}")
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
        help="Logging level; -v means quite, -vvvv means debug.",
        count=True,
    ),
):
    """Copies the files from the remote folder to the local folder."""
    if not Path(destination).is_dir():
        return -1
    with open_fs(source) as source_fs, open_fs(destination) as destination_fs:
        required = get_required_paths(destination_fs, source_fs, verbose)
        if required:
            download(source_fs, destination_fs, required, verbose)


def get_progress_bytes(processed_bytes, extra_bytes, size):
    return f"{processed_bytes + extra_bytes}/{size}"


def get_progress_percentage(processed_bytes, extra_bytes, size):
    return f"{(processed_bytes / size * 100):.2f}%"


def download(source_fs, destination_fs, required, verbose):
    for i, (path, size) in enumerate(required, start=1):
        if verbose in [DEBUG, VERBOSE]:
            print(f"{j:03}: {path}...")
        destination_fs.makedirs(str(Path(path).parents[0]), recreate=True)
        terminal_size = shutil.get_terminal_size()
        with destination_fs.openbin(path, "w") as local_file, source_fs.openbin(
            path
        ) as remote_file:
            some_bytes = remote_file.read(DEFAULT_BYTE_COUNT)
            j = 0
            processed_bytes = 0
            while some_bytes:
                terminal_size = shutil.get_terminal_size()
                local_file.write(some_bytes)
                print(
                    f"{BRAILLE[j % len(BRAILLE)]} {get_progress_percentage(processed_bytes, len(some_bytes), size)} [{get_progress_bytes(processed_bytes, len(some_bytes), size)}] Syncing {i} of {len(required)} files... {path}...",
                    end="\r",
                    flush=True,
                )
                sleep(0.05)
                j += 1
                processed_bytes += len(some_bytes)
                some_bytes = remote_file.read(DEFAULT_BYTE_COUNT)
            done = f"{BRAILLE_FULL} 100.00% [{size}/{size}]"
            print(f"{done}{' ' * (terminal_size.columns - len(done) -1)}")

    else:
        print(f"Complete!")


if __name__ == "__main__":
    typer.run(egon)
