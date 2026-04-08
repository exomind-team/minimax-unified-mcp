"""Utility helpers（工具辅助） for file handling and streaming playback."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterator

from fuzzywuzzy import fuzz

from exomind_minimax_mcp.exceptions import MiniMaxMcpError


def is_file_writeable(path: Path) -> bool:
    if path.exists():
        return os.access(path, os.W_OK)
    return os.access(path.parent, os.W_OK)


def build_output_file(
    tool: str,
    text: str,
    output_path: Path,
    extension: str,
    full_id: bool = False,
) -> Path:
    text_id = text if full_id else text[:10]
    filename = f"{tool}_{text_id.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return output_path / filename


def build_output_path(
    output_directory: str | None,
    base_path: str | None = None,
    is_test: bool = False,
) -> Path:
    effective_base_path = base_path or str(Path.home() / "Desktop")

    if output_directory is None:
        output_path = Path(os.path.expanduser(effective_base_path))
    elif not os.path.isabs(os.path.expanduser(output_directory)):
        output_path = Path(os.path.expanduser(effective_base_path)) / Path(output_directory)
    else:
        output_path = Path(os.path.expanduser(output_directory))

    if is_test:
        return output_path
    if not is_file_writeable(output_path):
        raise MiniMaxMcpError(f"Directory ({output_path}) is not writeable")
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
    if not path.is_absolute():
        base_path = os.getenv("MINIMAX_MCP_BASE_PATH")
        if not base_path:
            raise MiniMaxMcpError("File path must be absolute if MINIMAX_MCP_BASE_PATH is not set")
        path = Path(base_path) / path

    if not path.exists():
        if path.parent.exists():
            similar_files = try_find_similar_files(path.name, path.parent)
            if similar_files:
                joined = ",".join(str(item) for item in similar_files)
                raise MiniMaxMcpError(f"File ({path}) does not exist. Did you mean any of these files: {joined}?")
        raise MiniMaxMcpError(f"File ({path}) does not exist")

    if not path.is_file():
        raise MiniMaxMcpError(f"File ({path}) is not a file")
    if audio_content_check and not check_audio_file(path):
        raise MiniMaxMcpError(f"File ({path}) is not an audio or video file")
    return path


def is_installed(lib_name: str) -> bool:
    return shutil.which(lib_name) is not None


def play(audio: bytes | Iterator[bytes]) -> None:
    if not is_installed("ffplay"):
        raise ValueError(
            "ffplay from ffmpeg not found; install ffmpeg first（未找到 ffplay，请先安装 ffmpeg）."
        )

    proc = subprocess.Popen(
        args=["ffplay", "-autoexit", "-", "-nodisp"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if isinstance(audio, bytes):
        proc.stdin.write(audio)
        proc.stdin.close()
    else:
        for chunk in audio:
            proc.stdin.write(chunk)
        proc.stdin.close()

    proc.wait()
