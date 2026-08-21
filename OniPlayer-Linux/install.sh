#!/usr/bin/env bash

# =============================================================================
# OniPlayer Installation Script for Arch Linux
# Full-featured Video Player for Linux
# Version: 1.0.0
# =============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation paths
VENV_DIR="onienv"
VLC_ENGINE_DIR="vlc_engine"
DIST_DIR="dist"
INSTALL_DIR="/usr/local/bin"
LIB_DIR="/usr/local/lib"
ICON_DIR="/usr/share/icons"
DESKTOP_DIR="/usr/share/applications"

# Binary and desktop file names
BINARY_NAME="oniplayer"
DESKTOP_FILE="oniplayer.desktop"
ICON_NAME="oniplayer.png"

# =============================================================================
# Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_dependencies() {
    print_header "Checking Dependencies"
    
    # Only check for Python 3 - venv will handle pip and pyinstaller
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found"
        print_info "Please install Python 3:"
        echo "  sudo pacman -S python3"
        exit 1
    fi
    
    print_success "Python 3 is installed"
}

check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        print_warning "This script requires sudo privileges for system installation"
        print_info "You will be prompted for your password"
    fi
}

check_path() {
    print_header "Checking System PATH"
    
    local install_dir="/usr/local/bin"
    local path_added=false
    
    # Check if install directory is in current PATH
    if echo "$PATH" | grep -q "$install_dir"; then
        print_success "$install_dir is already in PATH"
        return 0
    fi
    
    print_warning "$install_dir is not in current PATH"
    print_info "Adding $install_dir to system PATH..."
    
    # Detect current shell
    local current_shell=$(basename "$SHELL")
    print_info "Detected shell: $current_shell"
    
    # Add to system-wide profile for all users
    if [ -f "/etc/profile" ]; then
        if ! grep -q "$install_dir" /etc/profile; then
            echo "" | sudo tee -a /etc/profile > /dev/null
            echo "# Added by OniPlayer installation" | sudo tee -a /etc/profile > /dev/null
            echo "export PATH=\"$install_dir:\$PATH\"" | sudo tee -a /etc/profile > /dev/null
            print_success "Added to /etc/profile (system-wide)"
            path_added=true
        fi
    fi
    
    # Add to /etc/environment for desktop sessions
    if [ -f "/etc/environment" ]; then
        if ! grep -q "$install_dir" /etc/environment; then
            sudo sed -i "s|PATH=\"\\(.*\\)\"|PATH=\"$install_dir:\\1\"|" /etc/environment 2>/dev/null || \
            echo "PATH=\"$install_dir:\$PATH\"" | sudo tee -a /etc/environment > /dev/null
            print_success "Added to /etc/environment (system-wide)"
            path_added=true
        fi
    fi
    
    # Add to user-specific shell configs based on current shell
    case "$current_shell" in
        bash)
            if [ -f "$HOME/.bashrc" ] && ! grep -q "$install_dir" "$HOME/.bashrc"; then
                echo "" >> "$HOME/.bashrc"
                echo "# Added by OniPlayer installation" >> "$HOME/.bashrc"
                echo "export PATH=\"$install_dir:\$PATH\"" >> "$HOME/.bashrc"
                print_success "Added to ~/.bashrc (user-specific)"
                path_added=true
            fi
            ;;
        zsh)
            if [ -f "$HOME/.zshrc" ] && ! grep -q "$install_dir" "$HOME/.zshrc"; then
                echo "" >> "$HOME/.zshrc"
                echo "# Added by OniPlayer installation" >> "$HOME/.zshrc"
                echo "export PATH=\"$install_dir:\$PATH\"" >> "$HOME/.zshrc"
                print_success "Added to ~/.zshrc (user-specific)"
                path_added=true
            fi
            ;;
        fish)
            if [ -f "$HOME/.config/fish/config.fish" ] && ! grep -q "$install_dir" "$HOME/.config/fish/config.fish"; then
                echo "" >> "$HOME/.config/fish/config.fish"
                echo "# Added by OniPlayer installation" >> "$HOME/.config/fish/config.fish"
                echo "set -gx PATH $install_dir \$PATH" >> "$HOME/.config/fish/config.fish"
                print_success "Added to ~/.config/fish/config.fish (user-specific)"
                path_added=true
            fi
            ;;
        *)
            print_warning "Unknown shell: $current_shell, adding to ~/.profile"
            if [ -f "$HOME/.profile" ] && ! grep -q "$install_dir" "$HOME/.profile"; then
                echo "" >> "$HOME/.profile"
                echo "# Added by OniPlayer installation" >> "$HOME/.profile"
                echo "export PATH=\"$install_dir:\$PATH\"" >> "$HOME/.profile"
                print_success "Added to ~/.profile (user-specific)"
                path_added=true
            fi
            ;;
    esac
    
    if [ "$path_added" = true ]; then
        print_warning "You may need to restart your terminal or run 'source ~/.bashrc' (or equivalent) for changes to take effect"
        print_info "Or run: export PATH=\"$install_dir:\$PATH\" for the current session"
    else
        print_warning "Could not automatically add to PATH (already configured or no suitable config file found)"
        print_info "Please manually add: export PATH=\"$install_dir:\$PATH\" to your shell configuration"
    fi
}

check_existing_installation() {
    print_header "Checking Existing Installation"
    
    if [ -f "$INSTALL_DIR/$BINARY_NAME" ]; then
        print_warning "OniPlayer is already installed at $INSTALL_DIR/$BINARY_NAME"
        read -p "Do you want to uninstall the existing version? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            uninstall_oniplayer
        else
            print_error "Installation cancelled"
            exit 1
        fi
    fi
}

create_virtual_environment() {
    print_header "Creating Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
}

install_dependencies() {
    print_header "Installing Python Dependencies"
    
    source "$VENV_DIR/bin/activate"
    
    # Install pip and setuptools first
    pip install --upgrade pip setuptools
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "No requirements.txt found, installing basic dependencies..."
        pip install pyqt6 python-vlc pyinstaller
        print_success "Basic dependencies installed"
    fi
    
    deactivate
}

build_binary() {
    print_header "Building OniPlayer Binary"
    
    source "$VENV_DIR/bin/activate"
    
    if [ -d "$DIST_DIR" ]; then
        print_info "Cleaning previous build..."
        rm -rf "$DIST_DIR"
    fi
    
    pyinstaller --noconfirm --onefile --windowed --name "$BINARY_NAME" main.py
    print_success "Binary built successfully"
    
    deactivate
}

install_system_files() {
    print_header "Installing System Files"
    
    # Create directories
    sudo mkdir -p "$INSTALL_DIR"
    sudo mkdir -p "$LIB_DIR"
    sudo mkdir -p "$ICON_DIR"
    sudo mkdir -p "$DESKTOP_DIR"
    
    # Install binary
    print_info "Installing binary to $INSTALL_DIR..."
    sudo cp "$DIST_DIR/$BINARY_NAME" "$INSTALL_DIR/"
    sudo chmod +x "$INSTALL_DIR/$BINARY_NAME"
    print_success "Binary installed"
    
    # Install VLC engine
    if [ -d "$VLC_ENGINE_DIR" ]; then
        print_info "Installing VLC engine to $LIB_DIR..."
        sudo cp -r "$VLC_ENGINE_DIR" "$LIB_DIR/"
        sudo chown -R root:root "$LIB_DIR/$VLC_ENGINE_DIR"
        sudo chmod -R 755 "$LIB_DIR/$VLC_ENGINE_DIR"
        print_success "VLC engine installed"
    else
        print_warning "VLC engine directory not found, skipping..."
    fi
    
    # Install icon
    if [ -f "icon.png" ]; then
        print_info "Installing icon to $ICON_DIR..."
        sudo cp icon.png "$ICON_DIR/$ICON_NAME"
        sudo chmod 644 "$ICON_DIR/$ICON_NAME"
        print_success "Icon installed"
    else
        print_warning "icon.png not found, skipping..."
    fi
}

create_desktop_entry() {
    print_header "Creating Desktop Entry"
    
    sudo tee "$DESKTOP_DIR/$DESKTOP_FILE" > /dev/null <<EOF
[Desktop Entry]
Name=OniPlayer
GenericName=Video Player
Comment=Full-featured Video Player
Exec=$INSTALL_DIR/$BINARY_NAME %F
Icon=$ICON_DIR/$ICON_NAME
Type=Application
Categories=Video;Player;AudioVideo;
MimeType=video/mp4;video/mpeg;video/quicktime;video/x-msvideo;video/x-matroska;video/webm;video/x-ms-wmv;video/3gpp;video/3gpp2;video/flv;video/x-flv;video/x-theora+ogg;video/x-ogm+ogg;video/mp2t;video/ogg;video/quicktime;video/vnd.mpegurl;video/webm;video/x-avi;video/x-flv;video/x-m4v;video/x-matroska;video/x-mpeg;video/x-ms-asf;video/x-ms-wmv;video/x-msvideo;video/x-ogm+ogg;video/x-theora+ogg;
Terminal=false
StartupNotify=true
Keywords=video;player;media;vlc;
EOF
    
    sudo chmod +x "$DESKTOP_DIR/$DESKTOP_FILE"
    print_success "Desktop entry created"
}

cleanup() {
    print_header "Cleaning Up"
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Removing virtual environment..."
        rm -rf "$VENV_DIR"
        print_success "Virtual environment removed"
    fi
    
    if [ -d "$DIST_DIR" ]; then
        print_info "Removing build directory..."
        rm -rf "$DIST_DIR"
        print_success "Build directory removed"
    fi
    
    if [ -d "build" ]; then
        print_info "Removing PyInstaller build directory..."
        rm -rf "build"
        print_success "PyInstaller build directory removed"
    fi
    
    if [ -f "$BINARY_NAME.spec" ]; then
        print_info "Removing PyInstaller spec file..."
        rm -f "$BINARY_NAME.spec"
        print_success "PyInstaller spec file removed"
    fi
}

uninstall_oniplayer() {
    print_header "Uninstalling OniPlayer"
    
    # Remove binary
    if [ -f "$INSTALL_DIR/$BINARY_NAME" ]; then
        sudo rm -f "$INSTALL_DIR/$BINARY_NAME"
        print_success "Binary removed"
    fi
    
    # Remove VLC engine
    if [ -d "$LIB_DIR/$VLC_ENGINE_DIR" ]; then
        sudo rm -rf "$LIB_DIR/$VLC_ENGINE_DIR"
        print_success "VLC engine removed"
    fi
    
    # Remove icon
    if [ -f "$ICON_DIR/$ICON_NAME" ]; then
        sudo rm -f "$ICON_DIR/$ICON_NAME"
        print_success "Icon removed"
    fi
    
    # Remove desktop entry
    if [ -f "$DESKTOP_DIR/$DESKTOP_FILE" ]; then
        sudo rm -f "$DESKTOP_DIR/$DESKTOP_FILE"
        print_success "Desktop entry removed"
    fi
    
    print_success "OniPlayer uninstalled successfully"
}

update_system() {
    print_header "Updating System"
    
    print_info "Running system update..."
    sudo pacman -Syu
    print_success "System updated"
}

print_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install    Install OniPlayer (default)"
    echo "  uninstall  Uninstall OniPlayer"
    echo "  help       Show this help message"
    echo ""
    echo "The installation process includes:"
    echo "  - Dependency checking and installation"
    echo "  - PATH configuration for system-wide access"
    echo "  - Virtual environment creation"
    echo "  - Binary building with PyInstaller"
    echo "  - System file installation"
    echo "  - Desktop entry creation"
    echo "  - System update (pacman -Syu)"
    echo ""
    echo "Note: This script is designed for Arch Linux systems"
    echo ""
    echo "Examples:"
    echo "  $0           # Install OniPlayer"
    echo "  $0 install   # Install OniPlayer"
    echo "  $0 uninstall # Uninstall OniPlayer"
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    print_header "OniPlayer Installation Script"
    
    # Parse command line arguments
    case "${1:-install}" in
        install)
            check_sudo
            check_dependencies
            check_existing_installation
            check_path
            create_virtual_environment
            install_dependencies
            build_binary
            install_system_files
            create_desktop_entry
            cleanup
            update_system
            print_header "Installation Complete"
            print_success "OniPlayer has been installed successfully!"
            print_info "You can now run OniPlayer by typing 'oniplayer' in your terminal"
            print_info "Or launch it from your application menu"
            ;;
        uninstall)
            check_sudo
            uninstall_oniplayer
            ;;
        help|--help|-h)
            print_usage
            ;;
        *)
            print_error "Invalid option: $1"
            print_usage
            exit 1
            ;;
    esac
}

# Trap errors and cleanup
trap 'print_error "Installation failed!"' ERR

# Run main function
main "$@"
