# Add project specific ProGuard rules here.
# Keep Google API classes
-keep class com.google.api.** { *; }
-keep class com.google.android.gms.** { *; }

# Keep Kotlin coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}

# Keep data classes
-keep class com.ytarchive.sync.DriveFile { *; }

# Keep WorkManager classes
-keep class * extends androidx.work.Worker
-keep class * extends androidx.work.CoroutineWorker

# Remove logging in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}
