#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import tomllib


def toml_to_md(infile: str, outfile: str, argument_hint: str | None = None) -> None:
    with open(infile, "rb") as infile_handle:
        data = tomllib.load(infile_handle)

    description = data.get("description", "").strip()
    prompt = data.get("prompt", "")

    frontmatter_lines = [
        "---",
        f"description: {description}",
    ]
    if argument_hint:
        frontmatter_lines.append(f"argument-hint: {argument_hint}")
    frontmatter_lines.extend(
        [
            "---",
            "",
        ]
    )

    with open(outfile, "w", encoding="utf-8") as outfile_handle:
        outfile_handle.write("\n".join(frontmatter_lines))
        outfile_handle.write(prompt.lstrip("\n"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Claude plugin metadata and convert TOML commands to Markdown."
    )
    parser.add_argument(
        "--repo-url",
        default="https://github.com/gemini-cli-extensions/conductor",
        help="Repository URL to use in generated plugin metadata.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with open("gemini-extension.json", "r", encoding="utf-8") as infile_handle:
        extension = json.load(infile_handle)

    plugin_dir = Path(".claude-plugin")
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_path = plugin_dir / "plugin.json"

    plugin_payload = {
        "name": "conductor",
        "version": extension.get("version", "0.0.0"),
        "description": (
            "Context-driven development for Claude Code. "
            "Plan before you build with specs, tracks, and TDD workflows."
        ),
        "author": {
            "name": "Gemini CLI Extensions",
            "url": "https://github.com/gemini-cli-extensions",
        },
        "homepage": "https://github.com/gemini-cli-extensions/conductor",
        "repository": args.repo_url,
        "license": "Apache-2.0",
        "keywords": [
            "conductor",
            "context-driven-development",
            "specs",
            "plans",
            "tracks",
            "tdd",
            "workflow",
            "project-management",
        ],
    }

    with open(plugin_path, "w", encoding="utf-8") as outfile_handle:
        json.dump(plugin_payload, outfile_handle, indent=2)
        outfile_handle.write("\n")

    marketplace_payload = {
        "name": "conductor-marketplace",
        "owner": {
            "name": "Gemini CLI Extensions",
            "url": "https://github.com/gemini-cli-extensions",
        },
        "plugins": [
            {
                "name": "conductor",
                "source": "./",
                "description": (
                    "Context-driven development: specs, plans, tracks, and TDD workflows"
                ),
            }
        ],
    }

    marketplace_path = plugin_dir / "marketplace.json"
    with open(marketplace_path, "w", encoding="utf-8") as outfile_handle:
        json.dump(marketplace_payload, outfile_handle, indent=2)
        outfile_handle.write("\n")

    toml_to_md(
        "commands/conductor/implement.toml",
        "commands/implement.md",
        argument_hint="[track_id]",
    )
    toml_to_md(
        "commands/conductor/newTrack.toml",
        "commands/newTrack.md",
        argument_hint="[description]",
    )
    toml_to_md(
        "commands/conductor/revert.toml",
        "commands/revert.md",
        argument_hint="[track|phase|task]",
    )
    toml_to_md("commands/conductor/setup.toml", "commands/setup.md")
    toml_to_md("commands/conductor/status.toml", "commands/status.md")


if __name__ == "__main__":
    main()
