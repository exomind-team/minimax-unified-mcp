from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    from exomind_minimax_mcp.live_config import load_live_settings
    from exomind_minimax_mcp.live_runner import (
        format_live_report_json,
        format_live_report_text,
        run_live_matrix,
    )

    parser = argparse.ArgumentParser(description="Run real MiniMax live API matrix checks（执行真实在线接口矩阵检查）.")
    parser.add_argument("--json", action="store_true", help="Print JSON output（输出 JSON）")
    parser.add_argument("--only", help="Run only one tool check（只跑一个工具）")
    parser.add_argument("--output-dir", default=str(Path.cwd() / "live-artifacts"), help="Artifact output directory")
    parser.add_argument("--disable-playback", action="store_true", help="Skip local audio playback")
    args = parser.parse_args()

    settings = load_live_settings()
    if settings is None:
        print("Missing live MiniMax credentials. Set MINIMAX_TOKEN_PLAN_API_KEY + MINIMAX_API_HOST.", file=sys.stderr)
        return 2

    results = run_live_matrix(
        api_key=settings.token_plan_key,
        api_host=settings.api_host,
        output_dir=args.output_dir,
        only=args.only,
        include_playback=not args.disable_playback,
    )
    if args.json:
        print(format_live_report_json(results))
    else:
        print(format_live_report_text(results))
    return 1 if any(item.status == "error" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
