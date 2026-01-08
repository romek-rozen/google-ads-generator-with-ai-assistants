#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text length checker - returns character count for each input string.
"""
import sys


def main():
    texts = []

    # From command line arguments
    if len(sys.argv) > 1:
        texts = sys.argv[1:]
    # Or from stdin (one text per line)
    elif not sys.stdin.isatty():
        texts = [line.rstrip('\n\r') for line in sys.stdin if line.strip()]

    if not texts:
        print("Usage: check_length.py \"text1\" \"text2\" ...")
        print("   or: echo -e \"text1\\ntext2\" | check_length.py")
        sys.exit(0)

    for text in texts:
        print(f'"{text}" - {len(text)}')


if __name__ == "__main__":
    main()