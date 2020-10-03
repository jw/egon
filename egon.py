from pathlib import Path

import fs
from fs.osfs import OSFS


def get_path_size(fs):
    print(f"Getting paths and sizes from {fs}...", end="")
    d = {}
    for path, info in fs.walk.info(namespaces=["details"]):
        if info.is_file:
            # print(f"{path}: {info.size}")
            d[path] = info.size
    print(f" found {len(d)} files.")
    return d


def egon(local_base: Path, remote_base: str):
    local = OSFS(str(local_base))
    destination = get_path_size(local)
    remote = fs.open_fs(remote_base)
    source = get_path_size(remote)
    print("Syncing...", end="")
    required = []
    for path, size in source.items():
        if path not in destination:
            # print(f"{path} not in destination.")
            required.append(path)
        elif size != destination[path]:
            # print(f"{path} in destination, but different size "
            #       f"({size} != {destination[path]}).")
            required.append(path)
    number = len(required) if required else "no"
    print(f" {number} files need to be retrieved.")
    if required:
        for i, path in enumerate(required, start=1):
            print(f"{i:03}: {path}...")
            file = local_base / path[1:]
            Path(file.parents[0]).mkdir(parents=True, exist_ok=True)
            with open(file, "wb") as f:
                remote.download(path, f)
        else:
            print(f"Complete!")
    else:
        print("The source files are in the destination.")

    if local:
        local.close()
    if remote:
        remote.close()


if __name__ == "__main__":
    # get these from argv
    local_base = Path("/home/jw/Downloads")
    remote_base = Path("/home/jw/docker/torrent/download/complete")
    remote_host = 'elevenbits'
    remote_user = 'jw'
    egon(local_base, f"ssh://{remote_user}@{remote_host}{remote_base}")
