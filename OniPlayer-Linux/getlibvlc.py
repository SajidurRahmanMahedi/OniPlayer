import os
import shutil
import glob
from pathlib import Path

# Configured paths
BUILD_DIR = Path("/home/rover/Desktop/libvlc/vlc/build").resolve()
PROJECT_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = PROJECT_DIR / "vlc_engine"

def copy_vlc_artifacts():
    if not BUILD_DIR.exists():
        print(f"[Error] VLC build directory not found: {BUILD_DIR}")
        return

    print(f"--> Source build directory: {BUILD_DIR}")
    print(f"--> Destination project folder: {OUTPUT_DIR}\n")

    # Target destination paths
    lib_dest = OUTPUT_DIR / "lib"
    plugins_dest = OUTPUT_DIR / "plugins"

    lib_dest.mkdir(parents=True, exist_ok=True)
    plugins_dest.mkdir(parents=True, exist_ok=True)

    # 1. Locate and copy libvlc shared libraries
    libvlc_pattern = BUILD_DIR / "lib" / ".libs" / "libvlc.so*"
    libvlc_files = glob.glob(str(libvlc_pattern))

    if not libvlc_files:
        print("[Warning] Could not find libvlc.so in lib/.libs/")
    for file_path in libvlc_files:
        p = Path(file_path)
        dest_file = lib_dest / p.name
        if p.is_symlink():
            target = os.readlink(p)
            if dest_file.is_symlink() or dest_file.exists():
                dest_file.unlink()
            os.symlink(target, dest_file)
            print(f"[Symlink] {p.name} -> {target}")
        else:
            shutil.copy2(p, dest_file)
            print(f"[Copied] {p.name}")

    # 2. Locate and copy libvlccore shared libraries
    libvlccore_pattern = BUILD_DIR / "src" / ".libs" / "libvlccore.so*"
    libvlccore_files = glob.glob(str(libvlccore_pattern))

    if not libvlccore_files:
        print("[Warning] Could not find libvlccore.so in src/.libs/")
    for file_path in libvlccore_files:
        p = Path(file_path)
        dest_file = lib_dest / p.name
        if p.is_symlink():
            target = os.readlink(p)
            if dest_file.is_symlink() or dest_file.exists():
                dest_file.unlink()
            os.symlink(target, dest_file)
            print(f"[Symlink] {p.name} -> {target}")
        else:
            shutil.copy2(p, dest_file)
            print(f"[Copied] {p.name}")

    # 3. Locate and copy all compiled plugin .so files across modules tree
    modules_dir = BUILD_DIR / "modules"
    print("\n--> Searching for plugins in modules directory...")
    plugin_count = 0

    for plugin_path in modules_dir.glob("**/.libs/*.so*"):
        # Copy the actual plugin shared object and symlinks
        dest_plugin = plugins_dest / plugin_path.name
        if plugin_path.is_symlink():
            target = os.readlink(plugin_path)
            if dest_plugin.is_symlink() or dest_plugin.exists():
                dest_plugin.unlink()
            os.symlink(target, dest_plugin)
        else:
            shutil.copy2(plugin_path, dest_plugin)
            plugin_count += 1

    print(f"[Copied] {plugin_count} plugin modules to {plugins_dest}")
    print("\n[Success] VLC engine files successfully placed in your project folder.")

if __name__ == "__main__":
    copy_vlc_artifacts()
