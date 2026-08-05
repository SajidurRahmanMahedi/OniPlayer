#!/usr/bin/env python3
"""
OniPlayer Linux
================
Uses Qt6 Multimedia (QMediaPlayer + QVideoWidget) on Linux.
Requires: PyQt6 + GStreamer codecs.
"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QStyle, QSizePolicy,
    QFrame, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QPoint, QMimeData, QDateTime
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QAction, QActionGroup, QIcon, QFontMetrics, QPainter, QPen, QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class ClickableSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(),
                event.pos().x(), self.width()
            )
            self.setValue(value)
            self.sliderMoved.emit(value)
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(),
                event.pos().x(), self.width()
            )
            self.setValue(value)
            self.sliderMoved.emit(value)
            event.accept()
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        event.ignore()

class StrokedLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw text with stroke
        pen = QPen(Qt.GlobalColor.black, 4)
        painter.setPen(pen)
        
        # Draw text outline (stroke) in 8 directions
        x = 5
        y = self.height() // 2 + 10
        
        offsets = [(-3,-3), (0,-3), (3,-3),
                  (-3,0),          (3,0),
                  (-3,3),  (0,3),  (3,3),
                  (-2,-2), (2,-2),
                  (-2,2),  (2,2)]
                  
        for dx, dy in offsets:
            painter.drawText(x + dx, y + dy, self.text())
            
        # Draw the main text in cyan
        painter.setPen(QColor("#00FFFF"))
        painter.drawText(x, y, self.text())

class VideoFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Mouse state tracking
        self.left_button_pressed = False
        self.right_button_pressed = False
        self.show_context = True
        self.combination_active = False
        self.combination_start_time = QDateTime.currentMSecsSinceEpoch()
        
        # Button combination detection
        self.button_combination_timer = QTimer(self)
        self.button_combination_timer.setSingleShot(True)
        self.button_combination_timer.setInterval(50)
        self.button_combination_timer.timeout.connect(self.handle_button_combination)
        self.pending_button_combination = None
        
        # Hide cursor by default
        self.setCursor(Qt.CursorShape.BlankCursor)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create context menu
        self.context_menu = QMenu(self)
        self.setup_context_menu()
        
        # Logo text
        self.logo_text = "OniPlayer"
        self.logo_font = self.font()
        self.logo_font.setPointSize(28)
        self.logo_font.setBold(True)

    def handle_button_combination(self):
        """Handle button combinations after the timeout"""
        # Only trigger if both buttons are still pressed
        if self.pending_button_combination == "right_hold_left":
            if self.right_button_pressed and self.left_button_pressed:
                self.parent.play_previous()
                self.combination_active = True
                self.combination_start_time = QDateTime.currentMSecsSinceEpoch()
        elif self.pending_button_combination == "left_hold_right":
            if self.left_button_pressed and self.right_button_pressed:
                self.parent.play_next()
                self.combination_active = True
                self.combination_start_time = QDateTime.currentMSecsSinceEpoch()
        self.pending_button_combination = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.left_button_pressed = True
            if self.right_button_pressed:
                # Right button is already pressed, this is a right-hold-left-click
                self.pending_button_combination = "right_hold_left"
                self.button_combination_timer.start()
                self.show_context = False
                self.combination_active = True  # Set immediately to prevent context menu
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_button_pressed = True
            if self.left_button_pressed:
                # Left button is already pressed, this is a left-hold-right-click
                self.pending_button_combination = "left_hold_right"
                self.button_combination_timer.start()
                self.show_context = False
                self.combination_active = True  # Set immediately to prevent context menu
            else:
                # For single right click, allow context menu on release
                self.show_context = True
                # Start a timer to track if this is a hold
                self.right_click_timer = QTimer(self)
                self.right_click_timer.setSingleShot(True)
                self.right_click_timer.setInterval(200)  # 200ms threshold for hold
                self.right_click_timer.timeout.connect(self.on_right_click_hold)
                self.right_click_timer.start()
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Start a timer for middle button hold
            self.middle_click_timer = QTimer(self)
            self.middle_click_timer.setSingleShot(True)
            self.middle_click_timer.setInterval(1000)  # 1 second for subtitle toggle
            self.middle_click_timer.timeout.connect(self.on_middle_click_hold)
            self.middle_click_timer.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.left_button_pressed = False
            if self.pending_button_combination:
                self.button_combination_timer.stop()
                self.pending_button_combination = None
            # Only reset combination lock when both buttons are released
            if not self.right_button_pressed:
                # Add a small delay before resetting combination lock
                QTimer.singleShot(100, self.reset_combination_lock)
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_button_pressed = False
            if hasattr(self, 'right_click_timer'):
                self.right_click_timer.stop()
            if self.pending_button_combination:
                self.button_combination_timer.stop()
                self.pending_button_combination = None
            # Only reset combination lock when both buttons are released
            if not self.left_button_pressed:
                # Add a small delay before resetting combination lock
                QTimer.singleShot(100, self.reset_combination_lock)
            
            # Show context menu on right-click release if no combination was triggered
            if self.show_context and self.parent.has_media and not self.combination_active:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.update_audio_tracks()
                self.update_subtitle_tracks()
                self.context_menu.popup(event.globalPosition().toPoint())
                self.context_menu.aboutToHide.connect(self._on_context_menu_hide)
        elif event.button() == Qt.MouseButton.MiddleButton:
            if hasattr(self, 'middle_click_timer'):
                # If timer is still running, it means this was a quick click
                if self.middle_click_timer.isActive():
                    self.middle_click_timer.stop()
                    self.parent.toggle_fullscreen()  # Toggle fullscreen only on quick click
        super().mouseReleaseEvent(event)

    def reset_combination_lock(self):
        self.combination_active = False
        self.show_context = True

    def contextMenuEvent(self, event):
        # Context menu is now handled in mouseReleaseEvent
        event.ignore()

    def _on_context_menu_hide(self):
        cursor_pos = self.mapFromGlobal(self.cursor().pos())
        local_y = cursor_pos.y()
        window_height = self.parent.height()
        if not (local_y <= 50 or window_height - local_y <= 50):
            self.setCursor(Qt.CursorShape.BlankCursor)

    def setup_context_menu(self):
        self.context_menu.setStyleSheet("""
            QMenu {
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid rgba(60, 60, 60, 0.8);
                padding: 5px;
                border-radius: 3px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
                color: rgba(255, 255, 255, 0.9);
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(60, 60, 60, 0.8);
                margin: 4px 0px;
            }
        """)
        
        play_action = self.context_menu.addAction("Play/Pause")
        play_action.triggered.connect(self.parent.toggle_play)
        
        fullscreen_action = self.context_menu.addAction("Toggle Fullscreen")
        fullscreen_action.triggered.connect(self.parent.toggle_fullscreen)
        
        self.context_menu.addSeparator()
        
        # Audio tracks menu
        self.audio_tracks_menu = self.context_menu.addMenu("Audio Track")
        self.audio_track_group = QActionGroup(self)
        self.audio_track_group.setExclusive(True)
        self.audio_track_group.triggered.connect(self.on_audio_track_changed)
        
        # Subtitle tracks menu
        self.subtitle_tracks_menu = self.context_menu.addMenu("Subtitles")
        self.subtitle_track_group = QActionGroup(self)
        self.subtitle_track_group.setExclusive(True)
        self.subtitle_track_group.triggered.connect(self.on_subtitle_track_changed)
        
        self.context_menu.addSeparator()
        
        open_action = self.context_menu.addAction("Open File...")
        open_action.triggered.connect(self.parent.open_file)
        
        self.context_menu.addSeparator()
        
        prev_action = self.context_menu.addAction("Previous Video")
        prev_action.triggered.connect(lambda: self.parent.play_previous())
        next_action = self.context_menu.addAction("Next Video")
        next_action.triggered.connect(lambda: self.parent.play_next())
        
        self.context_menu.addSeparator()
        
        seek_menu = self.context_menu.addMenu("Seek")
        back_10 = seek_menu.addAction("Back 10 seconds")
        back_10.triggered.connect(lambda: self.parent.seek_relative(-10))
        forward_10 = seek_menu.addAction("Forward 10 seconds")
        forward_10.triggered.connect(lambda: self.parent.seek_relative(10))
        back_30 = seek_menu.addAction("Back 30 seconds")
        back_30.triggered.connect(lambda: self.parent.seek_relative(-30))
        forward_30 = seek_menu.addAction("Forward 30 seconds")
        forward_30.triggered.connect(lambda: self.parent.seek_relative(30))
    
    def update_audio_tracks(self):
        """Update the audio tracks submenu with available tracks"""
        if not self.audio_tracks_menu:
            return
            
        self.audio_tracks_menu.clear()
        
        if not self.parent.has_media:
            no_tracks = self.audio_tracks_menu.addAction("No Audio Tracks")
            no_tracks.setEnabled(False)
            return
        
        audio_tracks = self.parent.media_player.audioTracks()
        if not audio_tracks or len(audio_tracks) == 0:
            no_tracks = self.audio_tracks_menu.addAction("No Audio Tracks")
            no_tracks.setEnabled(False)
            return
        
        current_track = self.parent.media_player.activeAudioTrack()
        
        for i, track in enumerate(audio_tracks):
            # Use extracted language from ffprobe if available
            track_name = f"Track {i + 1}"
            if hasattr(self.parent, 'audio_track_languages') and i < len(self.parent.audio_track_languages):
                lang = self.parent.audio_track_languages[i]
                if lang:
                    track_name = f"Track {i + 1} ({lang})"
            
            action = self.audio_tracks_menu.addAction(track_name)
            action.setCheckable(True)
            action.setData(i)
            if i == current_track:
                action.setChecked(True)
            self.audio_track_group.addAction(action)
    
    def update_subtitle_tracks(self):
        """Update the subtitle tracks submenu with available tracks"""
        if not self.subtitle_tracks_menu:
            return
            
        self.subtitle_tracks_menu.clear()
        for action in self.subtitle_track_group.actions():
            self.subtitle_track_group.removeAction(action)
        
        if not self.parent.has_media:
            no_tracks = self.subtitle_tracks_menu.addAction("No Subtitles")
            no_tracks.setEnabled(False)
            return
        
        subtitle_tracks = self.parent.media_player.subtitleTracks()
        if not subtitle_tracks or len(subtitle_tracks) == 0:
            no_tracks = self.subtitle_tracks_menu.addAction("No Subtitles")
            no_tracks.setEnabled(False)
            return
        
        current_track = self.parent.media_player.activeSubtitleTrack()
        
        # Add disable option
        disable_action = QAction("Disabled", self)
        disable_action.setCheckable(True)
        disable_action.setData(-1)
        if current_track == -1:
            disable_action.setChecked(True)
        self.subtitle_track_group.addAction(disable_action)
        self.subtitle_tracks_menu.addAction(disable_action)
        
        # Add subtitle tracks
        for i, track in enumerate(subtitle_tracks):
            # Try to get language from track metadata
            lang = track.value(track.Key.Language) if hasattr(track, 'Key') else ''
            title = track.value(track.Key.Title) if hasattr(track, 'Key') else ''
            
            if lang:
                track_name = f"Track {i + 1} ({lang})"
            elif title:
                track_name = title
            else:
                track_name = f"Track {i + 1}"
            
            action = self.subtitle_tracks_menu.addAction(track_name)
            action.setCheckable(True)
            action.setData(i)
            if i == current_track:
                action.setChecked(True)
            self.subtitle_track_group.addAction(action)
    
    def on_audio_track_changed(self, action):
        """Handle audio track selection"""
        track_id = action.data()
        audio_tracks = self.parent.media_player.audioTracks()
        if audio_tracks and track_id < len(audio_tracks):
            self.parent.media_player.setActiveAudioTrack(track_id)
            self.update_audio_tracks()
    
    def on_subtitle_track_changed(self, action):
        """Handle subtitle track selection"""
        track_id = action.data()
        subtitle_tracks = self.parent.media_player.subtitleTracks()
        if subtitle_tracks:
            self.parent.media_player.setActiveSubtitleTrack(track_id)
            self.update_subtitle_tracks()

    def on_right_click_hold(self):
        self.show_context = False

    def on_middle_click_hold(self):
        # Toggle subtitles
        self.parent.cycle_subtitle_track()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.parent:
            event.accept()
            # Reset button combination state to prevent accidental triggers
            self.left_button_pressed = False
            self.right_button_pressed = False
            self.pending_button_combination = None
            self.combination_active = False
            self.parent.toggle_play()
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        # Check if right mouse button is actually pressed during wheel event
        buttons = event.buttons()
        right_button_held = buttons & Qt.MouseButton.RightButton
        
        if self.left_button_pressed:
            delta = event.angleDelta().y()
            if delta > 0:
                self.parent.seek_relative(5)
            else:
                self.parent.seek_relative(-5)
            event.accept()
        elif right_button_held:
            self.show_context = False
            # Audio track cycling
            delta = event.angleDelta().y()
            if delta > 0:
                self.parent.cycle_audio_track_reverse()
            else:
                self.parent.cycle_audio_track()
            event.accept()
        else:
            delta = event.angleDelta().y()
            if delta > 0:
                current_volume = self.parent.volume_slider.value()
                new_volume = max(0, min(100, current_volume + 5))
                if new_volume != current_volume:
                    self.parent.volume_slider.setValue(new_volume)
                    self.parent.set_volume(new_volume)
                    self.parent.show_volume_overlay()
            else:
                current_volume = self.parent.volume_slider.value()
                new_volume = max(0, min(100, current_volume - 5))
                if new_volume != current_volume:
                    self.parent.volume_slider.setValue(new_volume)
                    self.parent.set_volume(new_volume)
                    self.parent.show_volume_overlay()
            event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.parent.toggle_play()
            event.accept()
        elif event.key() == Qt.Key.Key_F and not event.isAutoRepeat():
            self.parent.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape and self.parent.isFullScreen():
            self.parent.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.parent.toggle_fullscreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Up:
            current_volume = self.parent.volume_slider.value()
            new_volume = max(0, min(100, current_volume + 5))
            if new_volume != current_volume:
                self.parent.volume_slider.setValue(new_volume)
                self.parent.set_volume(new_volume)
                self.parent.show_volume_overlay()
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            current_volume = self.parent.volume_slider.value()
            new_volume = max(0, min(100, current_volume - 5))
            if new_volume != current_volume:
                self.parent.volume_slider.setValue(new_volume)
                self.parent.set_volume(new_volume)
                self.parent.show_volume_overlay()
            event.accept()
        elif event.key() == Qt.Key.Key_Left:
            self.parent.seek_relative(-10)
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            self.parent.seek_relative(10)
            event.accept()
        elif event.key() == Qt.Key.Key_M and not event.isAutoRepeat():
            self.parent.toggle_mute()
            event.accept()
        elif event.key() == Qt.Key.Key_PageUp:
            self.parent.play_next()
            event.accept()
        elif event.key() == Qt.Key.Key_PageDown:
            self.parent.play_previous()
            event.accept()
        elif event.key() == Qt.Key.Key_A and not event.isAutoRepeat():
            self.parent.cycle_audio_track()
            event.accept()
        elif event.key() == Qt.Key.Key_S and not event.isAutoRepeat():
            self.parent.cycle_subtitle_track()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        
        if isinstance(self.parent, QMainWindow):
            cursor_pos = event.pos()
            local_y = cursor_pos.y()
            window_height = self.parent.height()
            
            top_area_height = 50
            timeline_area_height = 50
            
            if local_y <= top_area_height or window_height - local_y <= timeline_area_height:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.BlankCursor)
            
            if self.parent.isFullScreen():
                if window_height - local_y <= timeline_area_height:
                    self.parent.timeline_container.show()
                else:
                    self.parent.timeline_container.hide()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.parent.has_media:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setFont(self.logo_font)
            
            text_rect = painter.fontMetrics().boundingRect(self.logo_text)
            x = (self.width() - text_rect.width()) // 2
            y = (self.height() - text_rect.height()) // 2
            
            painter.setPen(QPen(QColor(0, 0, 0, 60)))
            painter.drawText(x + 1, y + text_rect.height() + 1, self.logo_text)
            
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.drawText(x, y + text_rect.height(), self.logo_text)

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OniPlayer")
        self.setMinimumSize(800, 600)

        # ----- Central widget & layout -----
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # ----- Video display with custom frame -----
        self.video_container = QWidget()
        self.video_layout = QVBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_layout.setSpacing(0)
        
        self.video_frame = VideoFrame(self)
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_layout.addWidget(self.video_frame)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.video_frame.layout.addWidget(self.video_widget)
        
        self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.video_container)

        # ----- Timeline container -----
        self.timeline_container = QWidget()
        self.timeline_container.setFixedHeight(40)
        self.timeline_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.timeline_container.setStyleSheet("""
            QWidget {
                background: rgba(43, 43, 43, 0.9);
            }
        """)
        
        timeline_layout = QHBoxLayout(self.timeline_container)
        timeline_layout.setContentsMargins(10, 0, 5, 0)
        timeline_layout.setSpacing(5)
        
        # Play button
        self.play_button = QPushButton()
        self.play_button.setFixedSize(32, 32)
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 50, 50, 0.8);
                border: none;
                border-radius: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(90, 90, 90, 1.0);
            }
        """)
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play)
        timeline_layout.addWidget(self.play_button)
        
        # Previous button
        self.prev_button = QPushButton()
        self.prev_button.setFixedSize(32, 32)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 50, 50, 0.8);
                border: none;
                border-radius: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(90, 90, 90, 1.0);
            }
        """)
        self.prev_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.prev_button.clicked.connect(self.play_previous)
        timeline_layout.addWidget(self.prev_button)
        
        # Next button
        self.next_button = QPushButton()
        self.next_button.setFixedSize(32, 32)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 50, 50, 0.8);
                border: none;
                border-radius: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(90, 90, 90, 1.0);
            }
        """)
        self.next_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        self.next_button.clicked.connect(self.play_next)
        timeline_layout.addWidget(self.next_button)
        
        # Timeline slider
        self.timeline_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 3px;
                background: rgba(255, 255, 255, 0.2);
                margin: 0px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: none;
                width: 8px;
                height: 8px;
                margin: -3px 0;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #3399FF;
                border: none;
                height: 3px;
                margin: 0px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFFFFF;
                border: none;
                width: 10px;
                height: 10px;
                margin: -4px 0;
                border-radius: 5px;
            }
            QSlider::groove:horizontal:hover {
                height: 4px;
            }
            QSlider::sub-page:horizontal:hover {
                height: 4px;
            }
        """)
        self.timeline_slider.setRange(0, 0)
        self.timeline_slider.sliderMoved.connect(self._seek)
        self.timeline_slider.sliderPressed.connect(self._start_drag)
        self.timeline_slider.sliderReleased.connect(self._end_drag)
        timeline_layout.addWidget(self.timeline_slider)
        
        # Time labels
        self.time_label = QLabel("0:00")
        self.time_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background: transparent;
                font-size: 11px;
                min-width: 35px;
                padding: 0;
            }
        """)
        
        self.duration_label = QLabel("/ 0:00")
        self.duration_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background: transparent;
                font-size: 11px;
                min-width: 35px;
                padding: 0;
            }
        """)
        
        time_layout = QHBoxLayout()
        time_layout.setSpacing(2)
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.duration_label)
        timeline_layout.addLayout(time_layout)
        
        # Volume controls
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(2)
        
        self.volume_button = QPushButton()
        self.volume_button.setFixedSize(28, 28)
        self.volume_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 50, 50, 0.8);
                border: none;
                border-radius: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(90, 90, 90, 1.0);
            }
        """)
        self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.volume_button.clicked.connect(self.toggle_mute)
        volume_layout.addWidget(self.volume_button)
        
        self.volume_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                margin: 0px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: none;
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }
            QSlider::sub-page:horizontal {
                background: #3399FF;
                border: none;
                height: 4px;
                margin: 0px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFFFFF;
                border: none;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::groove:horizontal:hover {
                height: 5px;
            }
            QSlider::sub-page:horizontal:hover {
                height: 5px;
            }
        """)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)
        volume_layout.addWidget(self.volume_slider)
        
        timeline_layout.addLayout(volume_layout)
        self.main_layout.addWidget(self.timeline_container)

        # ----- Media backend -----
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Set default volume
        self.audio_output.setVolume(0.6)
        
        # ----- Signals / slots -----
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        self.media_player.playbackStateChanged.connect(self.update_play_button)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.errorOccurred.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        
        # Drag state to avoid slider feedback loop
        self._dragging = False
        self._is_muted = False
        
        # State tracking
        self.has_media = False
        self.playlist = []
        self.current_file = None
        self.current_index = 0
        self.last_volume = 60
        self.audio_track_languages = []
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Set initial window size
        self.resize(1024, 768)
        
        # Show window
        self.show()
        
        # Set focus to video frame
        self.video_frame.setFocus()

    # ------------------------------------------------------------------
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Media File", "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.webm *.wmv);;All Files (*)"
        )
        if file_path:
            self.play_file(file_path)
    
    def play_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        print(f"Loading file: {file_path}")
        self.update_playlist(file_path)
        
        # Extract audio and subtitle track languages using PyAV
        self.audio_track_languages = self.extract_track_languages(file_path)
        
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.media_player.play()
        self.has_media = True
        self.current_file = file_path
        
        # Update window title
        filename_display = os.path.basename(file_path)
        self.setWindowTitle(f"OniPlayer - {filename_display}")
        
        # Force video frame update
        self.video_frame.update()
    
    def extract_track_languages(self, file_path):
        """Extract audio track languages using PyAV"""
        import av
        audio_languages = []
        try:
            with av.open(file_path) as container:
                for stream in container.streams:
                    if stream.type == 'audio':
                        # Try to get language from metadata
                        lang = stream.metadata.get('language', stream.metadata.get('LANGUAGE', ''))
                        if lang:
                            audio_languages.append(lang)
                        else:
                            audio_languages.append('')
        except Exception as e:
            print(f"Error extracting track languages: {e}")
            audio_languages = []
        return audio_languages
    
    def toggle_fullscreen(self):
        if not self.isFullScreen():
            self.prev_geometry = self.geometry()
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.showFullScreen()
            self.timeline_container.hide()
        else:
            self.showNormal()
            if hasattr(self, 'prev_geometry'):
                self.setGeometry(self.prev_geometry)
            self.timeline_container.show()
            self.main_layout.setContentsMargins(0, 0, 0, 40)
    
    def toggle_play(self):
        if not self.has_media:
            return
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def seek_relative(self, seconds):
        if not self.has_media:
            return
        current_position = self.media_player.position()
        new_position = current_position + (seconds * 1000)
        new_position = max(0, new_position)
        self.media_player.setPosition(new_position)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.isFullScreen():
            # Show/hide timeline based on mouse position
            show_bottom = event.pos().y() > self.height() - 50
            
            if show_bottom:
                self.timeline_container.show()
                self.timeline_container.raise_()
            else:
                self.timeline_container.hide()
    
    def play_next(self):
        if not self.playlist or len(self.playlist) <= 1:
            self.media_player.stop()
            self.has_media = False
            self.current_file = None
            self.timeline_slider.setValue(0)
            self.time_label.setText("0:00")
            self.duration_label.setText("/ 0:00")
            self.setWindowTitle("OniPlayer")
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.video_frame.update()
            return
        
        next_index = self.current_index + 1
        if next_index >= len(self.playlist):
            self.media_player.stop()
            self.has_media = False
            self.current_file = None
            self.timeline_slider.setValue(0)
            self.time_label.setText("0:00")
            self.duration_label.setText("/ 0:00")
            self.setWindowTitle("OniPlayer")
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.video_frame.update()
            return
        
        self.current_index = next_index
        next_file = self.playlist[self.current_index]
        self.play_file(next_file)
    
    def play_previous(self):
        if not self.playlist or len(self.playlist) <= 1:
            return
        
        self.current_index = (self.current_index - 1) % len(self.playlist)
        prev_file = self.playlist[self.current_index]
        self.play_file(prev_file)
    
    def update_playlist(self, filepath):
        filepath = os.path.normpath(filepath)
        self.current_directory = os.path.dirname(filepath)
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm'}
        
        self.playlist = [
            os.path.normpath(os.path.join(self.current_directory, f))
            for f in os.listdir(self.current_directory)
            if os.path.splitext(f)[1].lower() in video_extensions
        ]
        
        self.playlist.sort()
        
        if filepath not in self.playlist:
            self.playlist.append(filepath)
            self.playlist.sort()
        
        self.current_file = filepath
        self.current_index = self.playlist.index(filepath)
    
    def cycle_audio_track(self):
        """Cycle to the next audio track"""
        if not self.has_media:
            return
            
        try:
            audio_tracks = self.media_player.audioTracks()
            if not audio_tracks or len(audio_tracks) <= 1:
                print("No audio tracks to cycle through")
                return
                
            current_track = self.media_player.activeAudioTrack()
            next_track = (current_track + 1) % len(audio_tracks)
            
            self.media_player.setActiveAudioTrack(next_track)
            
            # Update the menu if visible
            if hasattr(self.video_frame, "update_audio_tracks"):
                self.video_frame.update_audio_tracks()
                
        except Exception as e:
            print(f"Error cycling audio track: {e}")
    
    def cycle_audio_track_reverse(self):
        """Cycle to the previous audio track"""
        if not self.has_media:
            return
            
        try:
            audio_tracks = self.media_player.audioTracks()
            if not audio_tracks or len(audio_tracks) <= 1:
                print("No audio tracks to cycle through")
                return
                
            current_track = self.media_player.activeAudioTrack()
            prev_track = (current_track - 1) % len(audio_tracks)
            
            self.media_player.setActiveAudioTrack(prev_track)
            
            # Update the menu if visible
            if hasattr(self.video_frame, "update_audio_tracks"):
                self.video_frame.update_audio_tracks()
                
        except Exception as e:
            print(f"Error cycling audio track in reverse: {e}")
    
    def cycle_subtitle_track(self):
        """Cycle to the next subtitle track"""
        if not self.has_media:
            return
            
        try:
            subtitle_tracks = self.media_player.subtitleTracks()
            if not subtitle_tracks or len(subtitle_tracks) == 0:
                print("No subtitle tracks to cycle through")
                return
                
            current_track = self.media_player.activeSubtitleTrack()
            
            # Cycle: -1 (disabled) -> 0 -> 1 -> ... -> -1
            if current_track == -1:
                next_track = 0
            elif current_track + 1 < len(subtitle_tracks):
                next_track = current_track + 1
            else:
                next_track = -1
            
            self.media_player.setActiveSubtitleTrack(next_track)
            
            # Update the menu if visible
            if hasattr(self.video_frame, "update_subtitle_tracks"):
                self.video_frame.update_subtitle_tracks()
                
        except Exception as e:
            print(f"Error cycling subtitle track: {e}")

    def toggle_mute(self):
        if not self.has_media:
            return
        self._is_muted = not self._is_muted
        self.audio_output.setMuted(self._is_muted)
        icon = QStyle.StandardPixmap.SP_MediaVolumeMuted if self._is_muted else QStyle.StandardPixmap.SP_MediaVolume
        self.volume_button.setIcon(self.style().standardIcon(icon))

    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
        self.audio_output.setMuted(False)
        self._is_muted = False
        self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))

    # ------------------------------------------------------------------
    def duration_changed(self, duration):
        """Set slider range when media duration is known."""
        self.timeline_slider.setRange(0, duration)
        self.duration_label.setText(f"/ {self._format_time(duration)}")

    def position_changed(self, position):
        """Update slider and time label – but not during a user drag."""
        if not self._dragging:
            self.timeline_slider.blockSignals(True)
            self.timeline_slider.setValue(position)
            self.timeline_slider.blockSignals(False)
        self.time_label.setText(self._format_time(position))
    
    def media_status_changed(self, status):
        """Handle media status changes."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next()
        elif status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            # Update subtitle tracks when media is loaded
            if hasattr(self.video_frame, "update_subtitle_tracks"):
                self.video_frame.update_subtitle_tracks()

    def _start_drag(self):
        self._dragging = True

    def _end_drag(self):
        self._dragging = False
        # Final seek to where the mouse was released
        self.media_player.setPosition(self.timeline_slider.value())

    def _seek(self, position):
        """Called continuously while dragging (because setTracking=True)."""
        if self._dragging:
            self.media_player.setPosition(position)
            self.time_label.setText(self._format_time(position))

    # ------------------------------------------------------------------
    def update_play_button(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def handle_error(self, error, error_string):
        print(f"Media error: {error} - {error_string}")
    
    # ------------------------------------------------------------------
    # Drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.isLocalFile():
                self.play_file(url.toLocalFile())
                event.acceptProposedAction()
    
    # ------------------------------------------------------------------
    # Window events
    def showEvent(self, event):
        super().showEvent(event)
        self.video_frame.setFocus()
    
    def moveEvent(self, event):
        super().moveEvent(event)
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        
        if self.isFullScreen():
            cursor_pos = event.pos()
            local_y = cursor_pos.y()
            window_height = self.height()
            
            top_area_height = 50
            timeline_area_height = 50
            
            if local_y <= top_area_height:
                self.timeline_container.show()
            else:
                self.timeline_container.hide()
                
            if window_height - local_y <= timeline_area_height:
                self.timeline_container.show()
            else:
                self.timeline_container.hide()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)

    # ------------------------------------------------------------------
    @staticmethod
    def _format_time(ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h:02}:{m:02}:{s:02}"
        return f"{m:02}:{s:02}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark theme
    app.setPalette(QApplication.style().standardPalette())
    
    player = MediaPlayer()
    
    # Go to fullscreen by default after a short delay
    QTimer.singleShot(100, player.toggle_fullscreen)
    
    # If file path is provided as argument, play it
    if len(sys.argv) > 1:
        player.play_file(sys.argv[1])
    
    sys.exit(app.exec())