#!/bin/bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
/Users/segorov/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager --licenses <<EOF
y
y
y
y
y
y
y
EOF
