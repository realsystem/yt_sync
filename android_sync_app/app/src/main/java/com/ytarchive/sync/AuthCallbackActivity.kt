package com.ytarchive.sync

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity

class AuthCallbackActivity : AppCompatActivity() {

    private val TAG = "AuthCallbackActivity"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Handle OAuth callback from Google
        val intent = intent
        val data = intent.data

        if (data != null) {
            val code = data.getQueryParameter("code")
            val error = data.getQueryParameter("error")

            if (code != null) {
                Log.i(TAG, "Authorization successful")
                // Store authorization code and exchange for tokens
                val resultIntent = Intent().apply {
                    putExtra("auth_code", code)
                }
                setResult(Activity.RESULT_OK, resultIntent)
            } else if (error != null) {
                Log.e(TAG, "Authorization failed: $error")
                setResult(Activity.RESULT_CANCELED)
            }
        }

        finish()
    }
}
