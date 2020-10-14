from fs import open_fs

from egon import get_path_size, required_files


def test_get_path_size():
    some_fs = open_fs("./tests/source")
    assert get_path_size(some_fs) == {
        "/fizz.txt": 14,
        "/foo/foo_one.txt": 2,
        "/foo/foo_two.txt": 268,
    }


def test_required():
    source_fs = open_fs("./tests/source")
    source = get_path_size(source_fs)
    destination_fs = open_fs("./tests/destination")
    destination = get_path_size(destination_fs)
    assert required_files(destination, source) == ["/fizz.txt", "/foo/foo_two.txt"]
