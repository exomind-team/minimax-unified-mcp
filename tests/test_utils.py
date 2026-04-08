import pytest
from pathlib import Path
import tempfile
from exomind_minimax_mcp.exceptions import MiniMaxMcpError
from exomind_minimax_mcp.utils import (
    is_file_writeable,
    build_output_file,
    build_output_path,
    download_bytes,
    download_to_file,
    find_similar_filenames,
    try_find_similar_files,
    process_input_file,
)

def test_is_file_writeable():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        assert is_file_writeable(temp_path) is True
        assert is_file_writeable(temp_path / "nonexistent.txt") is True


def test_make_output_file():
    tool = "test"
    text = "hello world"
    output_path = Path("/tmp")
    result = build_output_file(tool, text, output_path, "mp3")
    assert result.name.startswith("test_")
    assert "hello" not in result.name
    assert "world" not in result.name
    assert result.suffix == ".mp3"


def test_make_output_path():
    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        result = build_output_path(temp_dir)
        assert result == Path(temp_dir)
        assert result.exists()
        assert result.is_dir()

    # Test with None output_directory (should use base_path)
    base_path = "/tmp/test_base"
    result = build_output_path(None, base_path, is_test=True)
    assert result == Path(base_path)
    
    # Test with relative output_directory
    base_path = "/tmp/test_base"
    result = build_output_path("subdir", base_path, is_test=True)
    assert result == Path(base_path) / "subdir"
    
    with tempfile.TemporaryDirectory() as allowed_base:
        allowed_path = Path(allowed_base)
        nested_path = allowed_path / "nested"
        result = build_output_path(str(nested_path), str(allowed_path), is_test=True)
        assert result == nested_path

    with tempfile.TemporaryDirectory() as allowed_base, tempfile.TemporaryDirectory() as forbidden_path:
        with pytest.raises(MiniMaxMcpError):
            build_output_path(forbidden_path, allowed_base, is_test=True)
    
    # Test with None base_path (should use desktop)
    result = build_output_path(None, None, is_test=True)
    assert result == Path.home() / "Desktop"
    


def test_find_similar_filenames():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test_file.txt"
        similar_file = temp_path / "test_file_2.txt"
        different_file = temp_path / "different.txt"

        test_file.touch()
        similar_file.touch()
        different_file.touch()

        results = find_similar_filenames(str(test_file), temp_path)
        assert len(results) > 0
        assert any(str(similar_file) in str(r[0]) for r in results)


def test_try_find_similar_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test_file.mp3"
        similar_file = temp_path / "test_file_2.mp3"
        different_file = temp_path / "different.txt"

        test_file.touch()
        similar_file.touch()
        different_file.touch()

        results = try_find_similar_files(str(test_file), temp_path)
        assert len(results) > 0
        assert any(str(similar_file) in str(r) for r in results)


def test_process_input_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.mp3"

        with open(test_file, "wb") as f:
            f.write(b"\xff\xfb\x90\x64\x00")

        result = process_input_file(str(test_file))
        assert result == test_file

        with pytest.raises(MiniMaxMcpError):
            process_input_file(str(temp_path / "nonexistent.mp3"))


def test_download_bytes_rejects_oversized_payload(monkeypatch):
    class FakeResponse:
        headers = {"content-length": "20"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"1234567890"
            yield b"abcdefghij"

        def close(self):
            return None

    monkeypatch.setattr(
        "exomind_minimax_mcp.utils.requests.get",
        lambda url, stream=True, timeout=30: FakeResponse(),
    )

    with pytest.raises(MiniMaxMcpError):
        download_bytes("https://example.com/demo.bin", max_bytes=8)


def test_download_to_file_streams_chunks(tmp_path, monkeypatch):
    target = tmp_path / "sample.bin"

    class FakeResponse:
        headers = {"content-length": "6"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"abc"
            yield b"def"

        def close(self):
            return None

    monkeypatch.setattr(
        "exomind_minimax_mcp.utils.requests.get",
        lambda url, stream=True, timeout=30: FakeResponse(),
    )

    written = download_to_file("https://example.com/demo.bin", target, max_bytes=8)

    assert written == target
    assert target.read_bytes() == b"abcdef"
