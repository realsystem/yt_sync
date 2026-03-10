package com.ytarchive.sync

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    private val TAG = "SyncWorker"
    private val settingsManager = SettingsManager(context)
    private val driveService = DriveService(context, settingsManager)
    private val notificationHelper = NotificationHelper(context)

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        Log.i(TAG, "Starting sync...")

        try {
            // Check if connected to Drive
            if (!settingsManager.getIsConnected()) {
                Log.w(TAG, "Not connected to Google Drive")
                return@withContext Result.failure()
            }

            // Show notification
            notificationHelper.showSyncStarted()

            // Get list of files in Drive
            val driveFiles = driveService.listFiles("youtube_archive")

            if (driveFiles.isEmpty()) {
                Log.i(TAG, "No files to sync")
                notificationHelper.showSyncComplete(0)
                updateLastSyncTime()
                return@withContext Result.success()
            }

            // Get local download directory
            val localDir = getDownloadDirectory()
            if (!localDir.exists()) {
                localDir.mkdirs()
            }

            // Find new files (not already downloaded)
            val localFiles = localDir.listFiles()?.map { it.name }?.toSet() ?: emptySet()
            val newFiles = driveFiles.filter { it.name !in localFiles }

            Log.i(TAG, "Found ${newFiles.size} new files to download")

            var downloadedCount = 0
            for (file in newFiles) {
                try {
                    val destFile = File(localDir, file.name)
                    driveService.downloadFile(file.id, destFile)
                    downloadedCount++
                    notificationHelper.updateSyncProgress(downloadedCount, newFiles.size)
                    Log.i(TAG, "Downloaded: ${file.name}")
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to download ${file.name}: ${e.message}")
                }
            }

            // Update last sync time
            updateLastSyncTime()

            // Show completion notification
            notificationHelper.showSyncComplete(downloadedCount)

            Log.i(TAG, "Sync complete. Downloaded $downloadedCount files")
            Result.success()

        } catch (e: Exception) {
            Log.e(TAG, "Sync failed: ${e.message}", e)
            notificationHelper.showSyncError(e.message ?: "Unknown error")
            Result.failure()
        }
    }

    private fun getDownloadDirectory(): File {
        // Try external storage first (SD card or emulated)
        val externalDir = applicationContext.getExternalFilesDir(null)
        return if (externalDir != null) {
            File(externalDir, "YouTube")
        } else {
            // Fallback to internal storage
            File(applicationContext.filesDir, "YouTube")
        }
    }

    private suspend fun updateLastSyncTime() {
        val dateFormat = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())
        val currentTime = dateFormat.format(Date())
        settingsManager.setLastSyncTime(currentTime)
    }
}

data class DriveFile(
    val id: String,
    val name: String,
    val size: Long,
    val mimeType: String
)
