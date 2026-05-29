package com.media.oniplayer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide

import android.content.SharedPreferences
import android.widget.ProgressBar

class VideoAdapter(
    private val videos: List<VideoItem>,
    private val sharedPrefs: SharedPreferences,
    private val onVideoClick: (VideoItem) -> Unit,
    private val onVideoLongClick: (VideoItem) -> Unit,
    private var isMultiSelectMode: Boolean = false,
    private var selectedVideos: Set<String> = emptySet(),
    private val onSelectionToggle: (String) -> Unit = {}
) : RecyclerView.Adapter<VideoAdapter.VideoViewHolder>() {

    class VideoViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val thumbnailView: ImageView = view.findViewById(R.id.videoThumbnail)
        val titleTextView: TextView = view.findViewById(R.id.videoTitle)
        val durationTextView: TextView = view.findViewById(R.id.videoDuration)
        val progressBar: ProgressBar = view.findViewById(R.id.videoProgressBar)
        val watchedBadge: TextView = view.findViewById(R.id.tvWatchedBadge)
        val selectionIndicator: View = view.findViewById(R.id.selectionIndicator)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VideoViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_video, parent, false)
        return VideoViewHolder(view)
    }

    override fun onBindViewHolder(holder: VideoViewHolder, position: Int) {
        val video = videos[position]
        holder.titleTextView.text = video.title
        holder.durationTextView.text = formatDuration(video.duration)
        
        // Handle progress and watched status
        val progress = sharedPrefs.getLong("progress_${video.path}", 0L)
        if (progress > 0 && video.duration > 0) {
            val percentage = (progress * 100 / video.duration).toInt()
            if (percentage >= 95) {
                holder.watchedBadge.visibility = View.VISIBLE
                holder.progressBar.visibility = View.GONE
            } else {
                holder.watchedBadge.visibility = View.GONE
                holder.progressBar.visibility = View.VISIBLE
                holder.progressBar.progress = percentage
            }
        } else {
            holder.watchedBadge.visibility = View.GONE
            holder.progressBar.visibility = View.GONE
        }

        Glide.with(holder.itemView.context)
            .load(video.path)
            .placeholder(android.R.color.darker_gray)
            .into(holder.thumbnailView)
        
        // Handle selection UI
        val isSelected = selectedVideos.contains(video.path ?: "")
        holder.selectionIndicator.visibility = if (isMultiSelectMode) View.VISIBLE else View.GONE
        
        // Use different colors for selected vs unselected states
        val color = if (isSelected) {
            ContextCompat.getColor(holder.itemView.context, R.color.accent_primary)
        } else {
            ContextCompat.getColor(holder.itemView.context, R.color.accent_unselected)
        }
        (holder.selectionIndicator as android.widget.ImageView).setColorFilter(color)
        
        // Update background based on selection
        holder.itemView.isSelected = isSelected
        holder.itemView.alpha = if (isSelected && isMultiSelectMode) 0.8f else 1.0f
        holder.itemView.setBackgroundColor(
            if (isSelected && isMultiSelectMode) {
                val color = ContextCompat.getColor(holder.itemView.context, R.color.accent_primary)
                android.graphics.Color.argb(30, android.graphics.Color.red(color), android.graphics.Color.green(color), android.graphics.Color.blue(color))
            } else {
                android.graphics.Color.TRANSPARENT
            }
        )
        
        // Handle click events
        holder.itemView.setOnClickListener {
            if (isMultiSelectMode) {
                onSelectionToggle(video.path ?: "")
            } else {
                onVideoClick(video)
            }
        }
        
        holder.itemView.setOnLongClickListener {
            onVideoLongClick(video)
            true
        }
    }


    override fun getItemCount(): Int = videos.size
    
    fun updateSelectionState(
        newSelectedVideos: Set<String>,
        newMultiSelectMode: Boolean
    ) {
        // Update internal state through a method that can be called from MainActivity
        selectedVideos = newSelectedVideos
        isMultiSelectMode = newMultiSelectMode
        // This will trigger a rebind of all items without recreating the adapter
        notifyDataSetChanged()
    }

    private fun formatDuration(durationMs: Long): String {
        val seconds = (durationMs / 1000) % 60
        val minutes = (durationMs / (1000 * 60)) % 60
        val hours = (durationMs / (1000 * 60 * 60))
        
        return if (hours > 0) {
            String.format("%d:%02d:%02d", hours, minutes, seconds)
        } else {
            String.format("%d:%02d", minutes, seconds)
        }
    }
}
