#!/usr/bin/env bash
# Download both Dendi resources into data/raw/ and check them against data/raw/SHA256SUMS.
# Run from the project root:  bash scripts/download_data.sh
set -euo pipefail

RAW=data/raw
Z=$RAW/zenodo_6591186
P=$RAW/pangloss_dendi
mkdir -p "$Z" "$P/audio" "$P/transcriptions"

# Zenodo record 6591186 (CC-BY-4.0)
[ -f "$Z/jami_dendi.zip" ] || curl -fL -o "$Z/jami_dendi.zip" \
  https://zenodo.org/api/records/6591186/files/jami_dendi.zip/content
[ -d "$Z/extracted" ] || unzip -q "$Z/jami_dendi.zip" -d "$Z/extracted"

# Pangloss Dendi tales (CC-BY-NC-SA-4.0); URLs are listed in sources.tsv
while IFS=$'\t' read -r _ _ _ wav xml; do
  [ -f "$P/audio/$(basename "$wav")" ] || curl -fL -o "$P/audio/$(basename "$wav")" "$wav"
  [ -f "$P/transcriptions/$(basename "$xml")" ] || curl -fL -o "$P/transcriptions/$(basename "$xml")" "$xml"
done < "$P/sources.tsv"

(cd "$RAW" && sha256sum -c SHA256SUMS)
