package com.ytarchive.sync

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.work.*
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity() {

    private lateinit var settingsManager: SettingsManager
    private lateinit var driveService: DriveService
    private lateinit var notificationHelper: NotificationHelper

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            // Permissions granted, proceed
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize services
        settingsManager = SettingsManager(this)
        driveService = DriveService(this, settingsManager)
        notificationHelper = NotificationHelper(this)

        // Request necessary permissions
        requestPermissions()

        setContent {
            YTArchiveSyncTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(
                        settingsManager = settingsManager,
                        driveService = driveService,
                        onSyncNow = { startImmediateSync() }
                    )
                }
            }
        }
    }

    private fun requestPermissions() {
        val permissions = mutableListOf<String>()

        // Notification permission for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        // Storage permissions
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.READ_MEDIA_VIDEO
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.READ_MEDIA_VIDEO)
            }
        } else {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        }

        if (permissions.isNotEmpty()) {
            permissionLauncher.launch(permissions.toTypedArray())
        }
    }

    private fun startImmediateSync() {
        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
            .build()

        WorkManager.getInstance(this).enqueue(syncRequest)

        notificationHelper.showSyncStarted()
    }

    fun schedulePeriodicSync(intervalMinutes: Long, wifiOnly: Boolean) {
        val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
            intervalMinutes, TimeUnit.MINUTES
        )
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(
                        if (wifiOnly) {
                            NetworkType.UNMETERED
                        } else {
                            NetworkType.CONNECTED
                        }
                    )
                    .build()
            )
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "sync_periodic",
            ExistingPeriodicWorkPolicy.REPLACE,
            syncRequest
        )
    }
}

@Composable
fun MainScreen(
    settingsManager: SettingsManager,
    driveService: DriveService,
    onSyncNow: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val isConnected by settingsManager.isConnected.collectAsState(initial = false)
    val wifiOnly by settingsManager.wifiOnly.collectAsState(initial = true)
    val syncInterval by settingsManager.syncInterval.collectAsState(initial = 60L)
    val lastSyncTime by settingsManager.lastSyncTime.collectAsState(initial = "")
    var showingAuth by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header
        Text(
            text = "YouTube Archive Sync",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )

        Divider()

        // Connection Status
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Google Drive Connection",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = if (isConnected) "Connected" else "Not Connected",
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (isConnected) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            MaterialTheme.colorScheme.error
                        }
                    )

                    Button(
                        onClick = {
                            if (isConnected) {
                                scope.launch {
                                    driveService.disconnect()
                                }
                            } else {
                                showingAuth = true
                                scope.launch {
                                    driveService.authenticate()
                                    showingAuth = false
                                }
                            }
                        },
                        enabled = !showingAuth
                    ) {
                        Text(if (isConnected) "Disconnect" else "Connect")
                    }
                }

                if (lastSyncTime.isNotEmpty()) {
                    Text(
                        text = "Last sync: $lastSyncTime",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        // Sync Settings
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Sync Settings",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )

                // WiFi Only Toggle
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("WiFi Only")
                        Text(
                            "Download only on WiFi to save mobile data",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Switch(
                        checked = wifiOnly,
                        onCheckedChange = {
                            scope.launch {
                                settingsManager.setWifiOnly(it)
                            }
                        }
                    )
                }

                Divider()

                // Sync Interval
                Column {
                    Text("Sync Interval")
                    Text(
                        "How often to check for new videos",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        IntervalButton("15 min", 15, syncInterval) {
                            scope.launch { settingsManager.setSyncInterval(it) }
                        }
                        IntervalButton("1 hour", 60, syncInterval) {
                            scope.launch { settingsManager.setSyncInterval(it) }
                        }
                        IntervalButton("6 hours", 360, syncInterval) {
                            scope.launch { settingsManager.setSyncInterval(it) }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        // Sync Now Button
        Button(
            onClick = onSyncNow,
            modifier = Modifier.fillMaxWidth(),
            enabled = isConnected
        ) {
            Text("Sync Now")
        }
    }
}

@Composable
fun IntervalButton(
    label: String,
    minutes: Long,
    currentInterval: Long,
    onClick: (Long) -> Unit
) {
    OutlinedButton(
        onClick = { onClick(minutes) },
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = if (currentInterval == minutes) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surface
            }
        )
    ) {
        Text(label)
    }
}

@Composable
fun YTArchiveSyncTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(),
        content = content
    )
}
