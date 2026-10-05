#!/bin/bash
set -euo pipefail
# Apt reads only the dated, staged repository under a --network=none build.
for suite in jammy jammy-updates jammy-security; do
  gpgv --keyring /usr/share/keyrings/ubuntu-archive-keyring.gpg "ubuntu/dists/$suite/InRelease"
done
printf '%s\n' 'deb [check-valid-until=no signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/qwen-bundle/ubuntu jammy main universe' 'deb [check-valid-until=no signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/qwen-bundle/ubuntu jammy-updates main universe' 'deb [check-valid-until=no signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/qwen-bundle/ubuntu jammy-security main universe' > /opt/qwen-bundle/build/snapshot.list
apt-get -o Dir::Etc::sourcelist=/opt/qwen-bundle/build/snapshot.list -o Dir::Etc::sourceparts=- update
# Offline file repository, exact explicit closure. Dependencies may not be silently acquired externally.
mapfile -t packages < build/apt-packages.lock
apt-get -o Dir::Etc::sourcelist=/opt/qwen-bundle/build/snapshot.list -o Dir::Etc::sourceparts=- --no-install-recommends -y install "${packages[@]}"
dpkg --audit
dpkg-query -W -f='${Package}\t${Version}\n' > build/base-plus-apt-installed.tsv
