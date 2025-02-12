"""
ClipboardTextRetriever Module

This module defines the ClipboardTextRetriever class, which provides an OS-aware mechanism
for retrieving the currently selected text from the system clipboard. By simulating the copy
command via the pyautogui library, it ensures that the correct keyboard shortcut is used
depending on the operating system: 'ctrl+c' on Windows, 'command+c' on macOS, and 'ctrl+c' on
Linux or other platforms. The selected text is then fetched using pyperclip, enabling seamless
automation of text extraction from the clipboard across various environments.

Summary: Retrieves selected text from the clipboard using OS-specific copy commands.
"""

import sys
import time
import pythoncom
import pyperclip

class ClipboardTextRetriever:
    def __init__(self):
        self.app = None
        self.window = None
    
    def get_selected_text(self):
        # Decide which method to call based on the OS
        if sys.platform.startswith('win'):
            import pyautogui
            pyautogui.hotkey('ctrl', 'c')
            # time.sleep(0.1)
            clipboard_content = pyperclip.paste().strip()
            return clipboard_content
        else:
            return self._get_selected_text_generic()

    def _get_selected_text_generic(self):
        """
        Fallback for non-Windows platforms.
        Simulates copying the selection via keyboard, then grabs clipboard text.
        """
        # macOS typically uses Command+C, Linux often uses Ctrl+C, but let's guess:
        # macOS:
        if sys.platform == 'darwin':
            import pyautogui
            pyautogui.hotkey('command', 'c')
        else:
            # Linux or other
            import pyautogui
            pyautogui.hotkey('ctrl', 'c')

        # time.sleep(0.1)
        return pyperclip.paste()
