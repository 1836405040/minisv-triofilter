#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo 'Usage: bash scripts/run.sh CONFIG.yaml [additional Snakemake arguments]' >&2
  exit 2
fi
config=$1
shift
exec snakemake --snakefile workflow/Snakefile --configfile "$config" --cores "${CORES:-16}" --printshellcmds "$@"
