"""
Download a pinned GitHub Release bundle for the smoothness ML model.

Usage:
    python -m scripts.fetch_model_release \\
        --repo owner/smoothness-model \\
        --tag v1.2.3 \\
        --token $GITHUB_TOKEN

    # Custom output directory (default: agents/scoring/model_bundle)
    python -m scripts.fetch_model_release \\
        --repo owner/smoothness-model \\
        --tag v1.2.3 \\
        --token $GITHUB_TOKEN \\
        --out path/to/model_bundle

The script downloads:
  - models/*.joblib  -> <out>/model.joblib
  - serving/model_contract.json      -> <out>/serving/model_contract.json
  - serving/background_features.json -> <out>/serving/background_features.json

Exits non-zero if any required file is missing from the release or download fails.
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

REQUIRED_SERVING_FILES = {"model_contract.json", "background_features.json"}
GITHUB_API = "https://api.github.com"


def _get(url: str, token: str | None) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _download(url: str, token: str | None, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"Accept": "application/octet-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        while chunk := resp.read(1 << 20):  # 1 MB chunks
            f.write(chunk)


def fetch(repo: str, tag: str, token: str, out: Path) -> None:
    print(f"Fetching release '{tag}' from {repo}...")
    url = f"{GITHUB_API}/repos/{repo}/releases/tags/{tag}"
    try:
        release = _get(url, token)
    except urllib.error.HTTPError as e:
        print(f"ERROR: GitHub API returned {e.code} for {url}", file=sys.stderr)
        if e.code == 404:
            print(
                f"  Release tag '{tag}' not found in repo '{repo}'.",
                file=sys.stderr,
            )
        sys.exit(1)

    assets: list[dict] = release.get("assets", [])
    if not assets:
        print("ERROR: Release has no uploaded assets.", file=sys.stderr)
        sys.exit(1)

    asset_names = {a["name"] for a in assets}
    print(f"Release assets found: {sorted(asset_names)}")

    # ── Find model.joblib ────────────────────────────────────────────────────
    joblib_assets = [a for a in assets if a["name"].endswith(".joblib")]
    if not joblib_assets:
        print("ERROR: No *.joblib asset found in release.", file=sys.stderr)
        sys.exit(1)
    if len(joblib_assets) > 1:
        # Pick the first alphabetically for determinism; warn so it's visible.
        joblib_assets.sort(key=lambda a: a["name"])
        print(
            f"WARNING: Multiple .joblib assets found, using '{joblib_assets[0]['name']}'."
        )

    model_asset = joblib_assets[0]
    model_dest = out / "model.joblib"
    print(f"  Downloading {model_asset['name']} -> {model_dest}")
    _download(model_asset["browser_download_url"], token, model_dest)

    # ── Find serving/ JSON files ─────────────────────────────────────────────
    missing_serving: set[str] = set()
    for filename in REQUIRED_SERVING_FILES:
        asset = next((a for a in assets if a["name"] == filename), None)
        if asset is None:
            missing_serving.add(filename)
            continue
        dest = out / "serving" / filename
        print(f"  Downloading {filename} -> {dest}")
        _download(asset["browser_download_url"], token, dest)

    if missing_serving:
        print(
            f"ERROR: Required serving files not found in release: {sorted(missing_serving)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Contract audit log ───────────────────────────────────────────────────
    contract_path = out / "serving" / "model_contract.json"
    try:
        contract = json.loads(contract_path.read_text())
        contract_version = contract.get("contract_version", "<unknown>")
        feature_columns = contract.get("feature_columns", [])
        print(
            f"\nModel bundle ready:"
            f"\n  release tag      : {tag}"
            f"\n  contract_version : {contract_version}"
            f"\n  feature_columns  : {feature_columns}"
            f"\n  output dir       : {out.resolve()}"
        )
    except Exception as exc:
        print(f"WARNING: Could not read model_contract.json for audit: {exc}")

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a pinned GitHub Release model bundle."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repo in owner/name format, e.g. acme/smoothness-model",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Exact release tag to pin, e.g. v1.2.3",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="GitHub personal access token (optional for public repos)",
    )
    parser.add_argument(
        "--out",
        default="agents/scoring/model_bundle",
        help="Output directory for the bundle (default: agents/scoring/model_bundle)",
    )
    args = parser.parse_args()

    out = Path(args.out)
    fetch(repo=args.repo, tag=args.tag, token=args.token, out=out)


if __name__ == "__main__":
    main()
