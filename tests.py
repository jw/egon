from unittest.mock import patch

from fs import open_fs

from egon import DEBUG
from egon import eta
from egon import get_path_size
from egon import get_required_paths
from egon import required_files
from egon import VERBOSE
from output import convert_bytes
from output import get_progress_bytes
from output import get_progress_percentage


def test_get_path_size():
    some_fs = open_fs("./tests/source")
    assert get_path_size(some_fs) == {
        "/fizz.txt": 15,
        "/foo/foo_one.txt": 3,
        "/foo/foo_two.txt": 269,
    }
    assert get_path_size(some_fs, verbose=DEBUG) == {
        "/fizz.txt": 15,
        "/foo/foo_one.txt": 3,
        "/foo/foo_two.txt": 269,
    }
    assert get_path_size(some_fs, verbose=VERBOSE) == {
        "/fizz.txt": 15,
        "/foo/foo_one.txt": 3,
        "/foo/foo_two.txt": 269,
    }


def test_required():
    source_fs = open_fs("./tests/source")
    source = get_path_size(source_fs)
    destination_fs = open_fs("./tests/destination")
    destination = get_path_size(destination_fs)
    assert required_files(source, destination) == [
        ("/fizz.txt", 15),
        ("/foo/foo_two.txt", 269),
    ]
    assert required_files(source, destination, verbose=DEBUG) == [
        ("/fizz.txt", 15),
        ("/foo/foo_two.txt", 269),
    ]


def test_get_required_paths():
    source_fs = open_fs("./tests/source")
    destination_fs = open_fs("./tests/destination")
    assert get_required_paths(destination_fs, source_fs, verbose=DEBUG) == [
        ("/fizz.txt", 15),
        ("/foo/foo_two.txt", 269),
    ]


def test_convert_bytes():
    assert convert_bytes(0) == "empty"
    assert convert_bytes(100) == "100 bytes"
    assert convert_bytes(1100) == "1100 bytes"
    assert convert_bytes(2100) == "2.10 kilobytes"
    assert convert_bytes(20100) == "20.10 kilobytes"
    assert convert_bytes(2201100) == "2.20 megabytes"
    assert convert_bytes(4444201100) == "4.44 gigabytes"
    assert convert_bytes(6666444201100) == "6.67 terabytes"
    assert convert_bytes(77776666444201100) == "77776.67 terabytes"
    assert convert_bytes(0, short=True) == "empty"
    assert convert_bytes(100, short=True) == "100b"
    assert convert_bytes(1100, short=True) == "1100b"
    assert convert_bytes(2100, short=True) == "2.10kB"
    assert convert_bytes(20100, short=True) == "20.10kB"
    assert convert_bytes(2201100, short=True) == "2.20MB"
    assert convert_bytes(4444201100, short=True) == "4.44GB"
    assert convert_bytes(6666444201100, short=True) == "6.67TB"
    assert convert_bytes(77776666444201100, short=True) == "77776.67TB"


def test_get_progress_bytes():
    assert get_progress_bytes(10, 5, 30) == "15 bytes/30 bytes"


def test_get_progress_percentage():
    assert get_progress_percentage(10, 15, 30) == "33.33%"


@patch("egon.time_ns", return_value=1_000_000_000 * 60)
def test_eta(mock_time):
    assert eta(50, 10, 20, 100) == "01:10:00 (599s)"
