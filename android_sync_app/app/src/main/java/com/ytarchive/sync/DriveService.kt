package com.ytarchive.sync

import android.content.Context
import android.content.Intent
import android.util.Log
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.Scope
import com.google.api.client.googleapis.extensions.android.gms.auth.GoogleAccountCredential
import com.google.api.client.http.javanet.NetHttpTransport
import com.google.api.client.json.gson.GsonFactory
import com.google.api.services.drive.Drive
import com.google.api.services.drive.DriveScopes
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class DriveService(
    private val context: Context,
    private val settingsManager: SettingsManager
) {
    private val TAG = "DriveService"

    private var driveClient: Drive? = null
    private var googleSignInClient: GoogleSignInClient? = null

    init {
        initializeGoogleSignIn()
    }

    private fun initializeGoogleSignIn() {
        val signInOptions = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestEmail()
            .requestScopes(Scope(DriveScopes.DRIVE_READONLY))
            .build()

        googleSignInClient = GoogleSignIn.getClient(context, signInOptions)

        // Check if already signed in
        val account = GoogleSignIn.getLastSignedInAccount(context)
        if (account != null) {
            initializeDriveClient(account)
        }
    }

    suspend fun authenticate(): Boolean = withContext(Dispatchers.IO) {
        try {
            // This would normally open a sign-in Intent
            // For now, we'll check if already authenticated
            val account = GoogleSignIn.getLastSignedInAccount(context)
            if (account != null) {
                initializeDriveClient(account)
                settingsManager.setConnected(true)
                true
            } else {
                // In a real implementation, start sign-in flow here
                Log.i(TAG, "Need to sign in - would launch sign-in Intent")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Authentication failed: ${e.message}")
            false
        }
    }

    private fun initializeDriveClient(account: GoogleSignInAccount) {
        val credential = GoogleAccountCredential.usingOAuth2(
            context,
            listOf(DriveScopes.DRIVE_READONLY)
        )
        credential.selectedAccount = account.account

        driveClient = Drive.Builder(
            NetHttpTransport(),
            GsonFactory.getDefaultInstance(),
            credential
        )
            .setApplicationName("YT Archive Sync")
            .build()

        Log.i(TAG, "Drive client initialized")
    }

    suspend fun disconnect() = withContext(Dispatchers.IO) {
        try {
            googleSignInClient?.signOut()?.await()
            driveClient = null
            settingsManager.setConnected(false)
            Log.i(TAG, "Disconnected from Google Drive")
        } catch (e: Exception) {
            Log.e(TAG, "Error disconnecting: ${e.message}")
        }
    }

    suspend fun listFiles(folderName: String): List<DriveFile> = withContext(Dispatchers.IO) {
        try {
            val client = driveClient ?: run {
                Log.e(TAG, "Drive client not initialized")
                return@withContext emptyList()
            }

            // Find the folder
            val folderId = findFolderId(folderName) ?: run {
                Log.w(TAG, "Folder not found: $folderName")
                return@withContext emptyList()
            }

            // List files in folder
            val result = client.files().list()
                .setQ("'$folderId' in parents and mimeType='video/mp4' and trashed=false")
                .setFields("files(id, name, size, mimeType)")
                .setPageSize(100)
                .execute()

            result.files.map { file ->
                DriveFile(
                    id = file.id,
                    name = file.name,
                    size = file.getSize() ?: 0,
                    mimeType = file.mimeType ?: "unknown"
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error listing files: ${e.message}", e)
            emptyList()
        }
    }

    private fun findFolderId(folderName: String): String? {
        return try {
            val client = driveClient ?: return null

            val result = client.files().list()
                .setQ("name='$folderName' and mimeType='application/vnd.google-apps.folder' and trashed=false")
                .setFields("files(id)")
                .setPageSize(1)
                .execute()

            result.files.firstOrNull()?.id
        } catch (e: Exception) {
            Log.e(TAG, "Error finding folder: ${e.message}")
            null
        }
    }

    suspend fun downloadFile(fileId: String, destFile: File) = withContext(Dispatchers.IO) {
        try {
            val client = driveClient ?: throw IllegalStateException("Drive client not initialized")

            val outputStream = FileOutputStream(destFile)
            client.files().get(fileId).executeMediaAndDownloadTo(outputStream)
            outputStream.close()

            Log.i(TAG, "Downloaded file: ${destFile.name}")
        } catch (e: Exception) {
            Log.e(TAG, "Error downloading file: ${e.message}", e)
            throw e
        }
    }

    fun getSignInIntent(): Intent? {
        return googleSignInClient?.signInIntent
    }
}
