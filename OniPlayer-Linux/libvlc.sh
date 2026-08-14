# git clone --depth 1 --branch 3.0.23 https://code.videolan.org/videolan/vlc.git

#!/usr/bin/env bash

set -Eeuo pipefail

readonly VLC_VERSION="3.0.23"
readonly VLC_ARCHIVE="./vlc.tar.gz"
readonly VLC_DIR="./vlc"
readonly ENGINE_SCRIPT="./get_engine.py"
readonly PREFIX="/usr/local"

cleanup() {
    echo "==> Cleaning up..."

    rm -rf -- "$VLC_DIR"
    rm -f -- "$ENGINE_SCRIPT" "$VLC_ARCHIVE"

    echo "==> Cleanup complete."
}

on_error() {
    local exit_code=$?
    echo "ERROR: Installation failed (exit code: $exit_code)." >&2
    exit "$exit_code"
}

trap on_error ERR
trap 'echo "==> Interrupted."; exit 130' INT TERM

echo "==> Installing build dependencies..."

sudo pacman -S --needed \
    base-devel \
    git \
    libtool \
    automake \
    autoconf \
    pkgconf \
    gettext \
    flex \
    bison \
    lua \
    ffmpeg \
    tar \
    qt6-base

echo "==> Extracting VLC source..."

rm -rf -- "$VLC_DIR"
tar -xzf "$VLC_ARCHIVE"

cd "$VLC_DIR"

echo "==> Bootstrapping VLC..."

./bootstrap

echo "==> Configuring VLC..."

mkdir -p build
cd build

../configure \
    --prefix="$PREFIX" \
    --disable-vlc \
    --disable-qt \
    --disable-skins2 \
    --enable-shared \
    --disable-static \
    --disable-gst-decode

echo "==> Building VLC..."

make -j"$(nproc)"

cd ../..

echo "==> Running engine setup..."

python3 "$ENGINE_SCRIPT"

echo "==> Updating system packages..."

sudo pacman -Syu

cleanup

echo "==> Done."
