#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker Desktop required; nothing installed." >&2; exit 2
fi
if ! docker info >/dev/null 2>&1; then
  echo "Start Docker Desktop first." >&2; exit 2
fi
export HOST_UID="$(id -u)" HOST_GID="$(id -g)"
for d in input projects output library; do mkdir -p "$ROOT/$d"; done
cd "$ROOT"
COMPOSE=(docker compose -f docker-compose.macos-safe.yml --project-directory "$ROOT")
case "${1:-}" in
  build)
    shift
    "${COMPOSE[@]}" build --pull safe "$@"
    ;;
  doctor)
    "${COMPOSE[@]}" run --rm safe python -c 'import os,sys,shutil; print("python",sys.version.split()[0],"ffmpeg",shutil.which("ffmpeg"),"node",shutil.which("node"),"uid",os.getuid(),"network", "offline via Docker")'
    ;;
  run)
    shift
    [ "$#" -gt 0 ] || { echo "Specify an isolated command." >&2; exit 2; }
    "${COMPOSE[@]}" run --rm safe "$@"
    ;;
  *)
    echo "Usage: bash scripts/macos-safe.sh {build|doctor|run <command>}" >&2
    exit 2
    ;;
esac
