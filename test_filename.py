#!/usr/bin/env python3
"""Test filename sanitization."""

from tools import sanitize_filename

# Test various video titles
test_cases = [
    ("How to Build a YouTube Archiver", "abc123"),
    ("Python Tutorial 2024 - Full Course!", "xyz789"),
    ("测试视频 Test Video", "def456"),
    ("My Cool Video!!! (Best Quality) [HD]", "ghi789"),
    ("This is a very long video title that should be shortened because it exceeds the maximum length allowed", "jkl012"),
    ("Special chars: #$%^&*()@!~`", "mno345"),
    ("   Multiple   Spaces   ", "pqr678"),
]

print("Filename Sanitization Examples:")
print("=" * 70)

for title, video_id in test_cases:
    clean_name = sanitize_filename(title, video_id)
    full_filename = f"{clean_name}.mp4"
    print(f"\nOriginal: {title}")
    print(f"Sanitized: {full_filename}")
    print(f"Length: {len(clean_name)} chars")

print("\n" + "=" * 70)
