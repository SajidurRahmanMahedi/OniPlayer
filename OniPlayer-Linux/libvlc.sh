sudo pacman -S --needed base-devel git libtool automake autoconf pkgconf gettext flex bison lua ffmpeg

git clone --depth 1 --branch 3.0.23 https://code.videolan.org/videolan/vlc.git

cd vlc

./bootstrap

mkdir build && cd build

../configure \
    --prefix=/usr/local \
    --disable-vlc \
    --disable-qt \
    --disable-skins2 \
    --enable-shared \
    --disable-static \
    --disable-gst-decode

make -j$(nproc)

cd ../..

python3 ./get_engine.py

rm -rf vlc
rm ./get_engine.py
rm -- "$0"
