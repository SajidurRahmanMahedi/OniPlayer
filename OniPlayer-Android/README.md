# OniPlayer Android

<p align="center">
  <strong>A premium, high-performance, dark-themed native Android video player powered by VideoLAN's LibVLC.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Platform Badge" />
  <img src="https://img.shields.io/badge/Language-Kotlin-0095D5?style=for-the-badge&logo=kotlin&logoColor=white" alt="Language Badge" />
  <img src="https://img.shields.io/badge/Core%20Engine-LibVLC%203.7.0-orange?style=for-the-badge&logo=vlc&logoColor=white" alt="VLC Badge" />
  <img src="https://img.shields.io/badge/Min%20SDK-35-blue?style=for-the-badge" alt="Min SDK Badge" />
  <img src="https://img.shields.io/badge/Target%20SDK-36-blue?style=for-the-badge" alt="Target SDK Badge" />
</p>

---

## Overview

**OniPlayer** is a highly polished native Android media player built in Kotlin. It features a full dark mode system designed around curated deep dark palettes and sky-blue accents. Powered by the industry-grade **LibVLC core engine**, OniPlayer guarantees butter-smooth hardware-accelerated playback of practically any video format, accompanied by an extremely responsive, gesture-rich viewing experience.

Whether you're organizing local collections into immediate folder trees, selecting custom subtitle tracks, scrubbing with high-precision overlays, or locking screen controls to watch uninterrupted, OniPlayer is designed for immersive and distraction-free entertainment.

---

## Outstanding Features

OniPlayer delivers an exceptionally premium experience right out of the box through these powerful features:

### High-Performance Playback & Format Compatibility
*   **LibVLC 3.7.0 Core:** Complete support for major video and audio standards (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.3gp`, `.ts`, and more).
*   **Hardware Acceleration:** Leverages the GPU to decode high-resolution streams smoothly with minimal battery impact.
*   **Smart Subtitle Synchronization:** Automatically searches for and mounts candidate subtitle files (`.srt`, `.ass`, `.ssa`, `.vtt`, `.sub`, `.smi`, `.ttml`, `.dfxp`) located in the same directory, matching the video name.

### Gesture-Driven Playback Controls
OniPlayer comes with an intuitive gesture interface tailored for power users:
*   **Brightness Swipe (Left-Side):** Smoothly adjust screen brightness by swiping up/down on the left half of the screen.
*   **Volume Swipe (Right-Side):** Adjust the system and VLC volume simultaneously by swiping up/down on the right half.
*   **Professional scrubbing / Precise Seek (Horizontal Swipe):** Slower, more precise scrubbing (0.25x scaling) allows high-fidelity seeking with a clean overlay showing absolute target time and delta offset (e.g., `+0:12` in green or `-1:05` in red).
*   **Pinch to Zoom (Two-Finger Scale):** Instantly zoom in or out of the video using a natural pinch gesture.
*   **Double Tap to Play/Pause:** Quickly toggle playback states.
*   **UI Touch Prevention (Screen Lock):** A long-press locks the interface, hiding all indicators and control bars to prevent accidental back actions or taps. A simple lock button overlay lets you unlock with ease.
*   **Edge-Gesture Protection:** Touch gestures are ignored within a fixed edge area ($48\text{ dp}$ threshold) to prevent clashes with system-level back swipes or navigation gestures.

### Gorgeous Library UI & Watch Progress Memory
*   **Curated Dark Design:** Employs an ultra-modern, deep-dark color scheme utilizing Sky-Blue (`#4FC3F7`) highlights, Netflix-Red style progress bars, and elegant transparent rounded confirm dialogs.
*   **Folder Tree Navigation:** Media is grouped by their immediate parent folders, separating internal storage and SD card collections cleanly.
*   **Watch History & Resume:** Saves the playback position of all videos in real-time. Displays a custom red progress bar under partially watched videos and a solid `WATCHED` badge for completed clips. Includes a **"Continue from Position"** quick-button inside the player.
*   **Batch Selection Mode:** Long-press folders or videos to enter multi-select mode. Select multiple items to delete them securely using our beautiful rounded Card layout confirmations.
*   **Swipe-to-Refresh Scan:** Seamlessly reload your media library. It triggers a comprehensive re-scan of files and requests a MediaStore update immediately.

---

## Tech Stack & Core Libraries

*   **Core Platform:** Native Android (Kotlin)
*   **Minimum/Target SDK:** Android 15 (API 35) / Android 16 (API 36)
*   **Playback Engine:** [LibVLC for Android](https://code.videolan.org/videolan/vlc-android) (`org.videolan.android:libvlc-all:3.7.0`)
*   **Image Caching:** [Glide v4.16.0](https://github.com/bumptech/glide) for lightning-fast video thumbnail generation.
*   **UI Architecture:** XML layouts with ConstraintLayouts, customized BottomSheets for track selectors, and RecyclerViews with custom binders to avoid scroll jumps during selection mode.

---

## Getting Started

### Prerequisites
*   **Android Studio** Jellyfish or later.
*   **JDK 11** or higher.
*   An Android device running **Android 15+ (API 35+)** for full system permission support.

### Building the Project
1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/OniPlayer.git
    cd OniPlayer/OniPlayer-Android
    ```
2.  Open the project in Android Studio.
3.  Let Gradle sync finish. The project is pre-configured to fetch the VLC Maven artifacts.
4.  Build and deploy the debug APK onto your test device:
    ```bash
    ./gradlew installDebug
    ```

---
