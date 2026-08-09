package com.media.oniplayer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView

class FolderAdapter(
    private val folders: List<FolderItem>,
    private val onFolderClick: (FolderItem) -> Unit,
    private val onFolderLongClick: (FolderItem) -> Unit,
    private var isMultiSelectMode: Boolean = false,
    private var selectedFolders: Set<String> = emptySet(),
    private val onSelectionToggle: (String) -> Unit = {}
) : RecyclerView.Adapter<FolderAdapter.FolderViewHolder>() {

    class FolderViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val folderName: TextView = view.findViewById(R.id.folderName)
        val folderVideoCount: TextView = view.findViewById(R.id.folderVideoCount)
        val selectionIndicator: View = view.findViewById(R.id.selectionIndicator)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FolderViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_folder, parent, false)
        return FolderViewHolder(view)
    }

    override fun onBindViewHolder(holder: FolderViewHolder, position: Int) {
        val folder = folders[position]
        holder.folderName.text = folder.name
        val count = folder.videos.size
        holder.folderVideoCount.text = if (count == 1) "1 video" else "$count videos"
        
        // Handle selection UI
        val isSelected = selectedFolders.contains(folder.path ?: "")
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
                onSelectionToggle(folder.path ?: "")
            } else {
                onFolderClick(folder)
            }
        }
        
        holder.itemView.setOnLongClickListener {
            onFolderLongClick(folder)
            true
        }
    }

    override fun getItemCount(): Int = folders.size
    
    fun updateSelectionState(
        newSelectedFolders: Set<String>,
        newMultiSelectMode: Boolean
    ) {
        // Update internal state through a method that can be called from MainActivity
        selectedFolders = newSelectedFolders
        isMultiSelectMode = newMultiSelectMode
        // This will trigger a rebind of all items without recreating the adapter
        notifyDataSetChanged()
    }
}
