#!/usr/bin/env bash
# Session-Ende: Linux-FS pushen und Windows-Mount auf origin/main zurücksetzen.
set -euo pipefail

LINUX_REPO="$HOME/git_repos/consent-test-suite"
WIN_REPO="/mnt/f/git_repos/consent-test-suite"

echo "==> Push Linux-FS zu origin..."
git -C "$LINUX_REPO" push

echo "==> Sync Windows-Mount auf origin/main..."
git -C "$WIN_REPO" fetch
git -C "$WIN_REPO" reset --hard origin/main

echo "==> Fertig. Beide Repos auf $(git -C "$LINUX_REPO" rev-parse --short HEAD)."
