"""Utility helpers（工具辅助） for file handling and streaming playback."""

from __future__ import annotations

import os
import shutil
import subprocess
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import requests
from fuzzywuzzy import fuzz

from exomind_minimax_mcp.constants import DEFAULT_HTTP_TIMEOUT_SECONDS, DEFAULT_MAX_HTTP_DOWNLOAD_BYTES
from exomind_minimax_mcp.exceptions import MiniMaxMcpError


def is_file_writeable(path: Path) -> bool:
    probe = path
    if not probe.exists():
        probe = path.parent
        while not probe.exists() and probe != probe.parent:
            probe = probe.parent
    if not probe.exists():
        return False
    if path.exists():
        return os.access(path, os.W_OK)
    return os.access(probe, os.W_OK)


def _resolve_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _ensure_within_base_path(path: Path, base_path: Path) -> Path:
    resolved_path = _resolve_path(path)
    resolved_base = _resolve_path(base_path)
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError as exc:
        raise MiniMaxMcpError(
            "Output directory must stay inside the configured base path（输出目录必须位于基础目录内）"
        ) from exc
    return resolved_path


def describe_path(path: Path, relative_to: Path | None = None) -> str:
    resolved_path = _resolve_path(path)
    if relative_to is not None:
        try:
            return str(resolved_path.relative_to(_resolve_path(relative_to)))
        except ValueError:
            pass
    return resolved_path.name or str(resolved_path)


def build_output_file(
    tool: str,
    text: str,
    output_path: Path,
    extension: str,
    full_id: bool = False,
) -> Path:
    del text
    del full_id
    filename = f"{tool}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}.{extension}"
    return output_path / filename


def build_output_path(
    output_directory: str | None,
    base_path: str | None = None,
    is_test: bool = False,
) -> Path:
    effective_base_path = _resolve_path(Path(base_path or str(Path.home() / "Desktop")))

    if output_directory is None:
        output_path = effective_base_path
    elif not os.path.isabs(os.path.expanduser(output_directory)):
        output_path = effective_base_path / Path(output_directory)
    else:
        output_path = Path(os.path.expanduser(output_directory))

    output_path = _ensure_within_base_path(output_path, effective_base_path)

    if is_test:
        return output_path
    if not is_file_writeable(output_path):
        raise MiniMaxMcpError(f"Directory ({describe_path(output_path, effective_base_path)}) is not writeable")
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def find_similar_filenames(
    target_file: str,
    directory: Path,
    threshold: int = 70,
) -> list[tuple[Path, int]]:
    target_filename = os.path.basename(target_file)
    similar_files: list[tuple[Path, int]] = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename == target_filename and os.path.join(root, filename) == target_file:
                continue
            similarity = fuzz.token_sort_ratio(target_filename, filename)
            if similarity >= threshold:
                similar_files.append((Path(root) / filename, similarity))

    similar_files.sort(key=lambda item: item[1], reverse=True)
    return similar_files


def check_audio_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".wav",
        ".mp3",
        ".m4a",
        ".aac",
        ".ogg",
        ".flac",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
    }


def try_find_similar_files(filename: str, directory: Path, take_n: int = 5) -> list[Path]:
    return [path for path, _ in find_similar_filenames(filename, directory)[:take_n] if check_audio_file(path)]


def process_input_file(file_path: str, audio_content_check: bool = True) -> Path:
    path = Path(file_path)
    base_root: Path | None = None
    if not path.is_absolute():
        base_path = os.getenv("MINIMAX_MCP_BASE_PATH")
        if not base_path:
            raise MiniMaxMcpError("File path must be absolute if MINIMAX_MCP_BASE_PATH is not set")
        base_root = _resolve_path(Path(base_path))
        path = _ensure_within_base_path(base_root / path, base_root)

    display_path = describe_path(path, base_root)

    if not path.exists():
        if path.parent.exists():
            similar_files = try_find_similar_files(path.name, path.parent)
            if similar_files:
                joined = ",".join(describe_path(item, base_root) for item in similar_files)
                raise MiniMaxMcpError(f"File ({display_path}) does not exist. Did you mean any of these files: {joined}?")
        raise MiniMaxMcpError(f"File ({display_path}) does not exist")

    if not path.is_file():
        raise MiniMaxMcpError(f"File ({display_path}) is not a file")
    if audio_content_check and not check_audio_file(path):
        raise MiniMaxMcpError(f"File ({display_path}) is not an audio or video file")
    return path


def _validate_content_length(headers: dict[str, str], max_bytes: int) -> None:
    content_length = headers.get("content-length")
    if content_length and int(content_length) > max_bytes:
        raise MiniMaxMcpError(
            f"Remote file exceeds max size {max_bytes} bytes（远程文件超过大小限制）"
        )


def download_bytes(
    url: str,
    max_bytes: int = DEFAULT_MAX_HTTP_DOWNLOAD_BYTES,
    timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
) -> bytes:
    response = requests.get(url, stream=True, timeout=timeout)
    try:
        response.raise_for_status()
        _validate_content_length(response.headers, max_bytes)

        written = 0
        buffer = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            written += len(chunk)
            if written > max_bytes:
                raise MiniMaxMcpError(
                    f"Remote file exceeds max size {max_bytes} bytes（远程文件超过大小限制）"
                )
            buffer.extend(chunk)
        return bytes(buffer)
    finally:
        response.close()


def download_to_file(
    url: str,
    output_file: Path,
    max_bytes: int = DEFAULT_MAX_HTTP_DOWNLOAD_BYTES,
    timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
) -> Path:
    response = requests.get(url, stream=True, timeout=timeout)
    try:
        response.raise_for_status()
        _validate_content_length(response.headers, max_bytes)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        written = 0
        try:
            with output_file.open("wb") as file_handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > max_bytes:
                        raise MiniMaxMcpError(
                            f"Remote file exceeds max size {max_bytes} bytes（远程文件超过大小限制）"
                        )
                    file_handle.write(chunk)
        except Exception:
            with suppress(OSError):
                output_file.unlink()
            raise
        return output_file
    finally:
        response.close()


def is_installed(lib_name: str) -> bool:
    return shutil.which(lib_name) is not None


def play(audio: bytes | Iterator[bytes]) -> None:
    if not is_installed("ffplay"):
        raise ValueError(
            "ffplay from ffmpeg not found; install ffmpeg first（未找到 ffplay，请先安装 ffmpeg）."
        )

    import tempfile, threading

    if isinstance(audio, bytes):
        # Direct: write to temp file, ffplay plays from file path (reliable -autoexit)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(audio)
            tmp_path = tmp.name

        try:
            proc = subprocess.Popen(
                args=["ffplay", "-autoexit", "-nodisp", tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            proc.wait()
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    else:
        # Streaming: pipe stdin so ffplay plays as chunks arrive
        proc = subprocess.Popen(
            args=["ffplay", "-autoexit", "-", "-nodisp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        def writer():
            try:
                for chunk in audio:
                    if proc.stdin.closed:
                        break
                    proc.stdin.write(chunk)
                proc.stdin.close()
            except Exception:
                try:
                    proc.stdin.close()
                except Exception:
                    pass

        t = threading.Thread(target=writer, daemon=True)
        t.start()
        proc.wait()
        t.join(timeout=5)
