package com.media.oniplayer

data class FolderItem(
    val name: String,
    val path: String,
    val videos: List<VideoItem>
)
