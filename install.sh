#!/bin/sh
set -eu
printf '\n  AmneziaWG Client для UniFi · v0.3.0\n  Developed by Roman Tselischev / https://vk.com/greez\n\n'
BASE=https://raw.githubusercontent.com/DjGreeZ/Amnezia-UniFi/v0.3.0
TMP=$(mktemp -d /tmp/awg-download.XXXXXX)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
cd "$TMP"
curl -fL --progress-bar "$BASE/AmneziaWG-UniFi-v0.3.0.run" -o AmneziaWG-UniFi-v0.3.0.run
curl -fsSL "$BASE/AmneziaWG-UniFi-v0.3.0.sha256" -o checksums
sha256sum -c checksums
sh AmneziaWG-UniFi-v0.3.0.run
