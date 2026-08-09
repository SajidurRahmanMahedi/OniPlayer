sudo pacman -S --needed base-devel git libtool automake autoconf pkgconf gettext flex bison lua


git clone https://code.videolan.org/videolan/vlc.git
cd vlc
git checkout 3.0.23

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

python3 getlibvlc.py

rm -rf vlc
