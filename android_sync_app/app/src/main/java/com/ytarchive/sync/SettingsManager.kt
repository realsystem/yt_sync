package com.ytarchive.sync

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

class SettingsManager(private val context: Context) {

    private object PreferenceKeys {
        val IS_CONNECTED = booleanPreferencesKey("is_connected")
        val WIFI_ONLY = booleanPreferencesKey("wifi_only")
        val SYNC_INTERVAL = longPreferencesKey("sync_interval")
        val LAST_SYNC_TIME = stringPreferencesKey("last_sync_time")
        val STORAGE_PATH = stringPreferencesKey("storage_path")
    }

    // Flows for observing settings
    val isConnected: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[PreferenceKeys.IS_CONNECTED] ?: false
    }

    val wifiOnly: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[PreferenceKeys.WIFI_ONLY] ?: true  // Default to WiFi only
    }

    val syncInterval: Flow<Long> = context.dataStore.data.map { preferences ->
        preferences[PreferenceKeys.SYNC_INTERVAL] ?: 60L  // Default 1 hour
    }

    val lastSyncTime: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[PreferenceKeys.LAST_SYNC_TIME] ?: ""
    }

    val storagePath: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[PreferenceKeys.STORAGE_PATH] ?: "/storage/emulated/0/Videos/YouTube"
    }

    // Suspend functions to update settings
    suspend fun setConnected(connected: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[PreferenceKeys.IS_CONNECTED] = connected
        }
    }

    suspend fun setWifiOnly(wifiOnly: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[PreferenceKeys.WIFI_ONLY] = wifiOnly
        }
    }

    suspend fun setSyncInterval(minutes: Long) {
        context.dataStore.edit { preferences ->
            preferences[PreferenceKeys.SYNC_INTERVAL] = minutes
        }
    }

    suspend fun setLastSyncTime(time: String) {
        context.dataStore.edit { preferences ->
            preferences[PreferenceKeys.LAST_SYNC_TIME] = time
        }
    }

    suspend fun setStoragePath(path: String) {
        context.dataStore.edit { preferences ->
            preferences[PreferenceKeys.STORAGE_PATH] = path
        }
    }

    // Synchronous getters (use carefully, prefer flows)
    suspend fun getWifiOnly(): Boolean {
        return wifiOnly.first()
    }

    suspend fun getSyncInterval(): Long {
        return syncInterval.first()
    }

    suspend fun getIsConnected(): Boolean {
        return isConnected.first()
    }
}
