"""Run this once to create the ReadVault desktop shortcut with icon."""
import os
import sys
import urllib.request
import winreg

def get_desktop():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
              r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        desktop, _ = winreg.QueryValueEx(key, "Desktop")
        return desktop
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Desktop")

def download_icon():
    """Download a book icon (.ico) for the shortcut."""
    icon_path = os.path.join(os.path.dirname(__file__), "bookshelf.ico")
    if os.path.exists(icon_path):
        return icon_path

    # Create a simple ICO file using Pillow if available
    try:
        from PIL import Image, ImageDraw, ImageFont
        size = 256
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle
        draw.ellipse([4, 4, size-4, size-4], fill="#1a0e0b")

        # Book shape
        bx, by, bw, bh = 60, 55, 136, 155
        # Book cover
        draw.rectangle([bx, by, bx+bw, by+bh], fill="#fb923c", outline="#f97316", width=3)
        # Spine
        draw.rectangle([bx, by, bx+18, by+bh], fill="#ea6c0a")
        # Lines (pages)
        for i in range(4):
            y = by + 35 + i * 26
            draw.rectangle([bx+28, y, bx+bw-12, y+8], fill="#1a0e0b", outline=None)
        # Small "B" letter
        draw.ellipse([bx+bw-38, by+bh-40, bx+bw-8, by+bh-8], fill="#1a0e0b")

        img.save(icon_path, format="ICO", sizes=[(256,256),(64,64),(32,32),(16,16)])
        print("Icon created with Pillow.")
        return icon_path
    except ImportError:
        pass

    # Fallback: use Python's own icon
    python_ico = os.path.join(os.path.dirname(sys.executable), "DLLs", "py.ico")
    if os.path.exists(python_ico):
        return python_ico

    return None


def create_shortcut():
    import winshell
    desktop   = get_desktop()
    icon_path = download_icon()
    app_script= os.path.abspath(os.path.join(os.path.dirname(__file__), "app.pyw"))
    pythonw   = sys.executable.replace("python.exe", "pythonw.exe")
    shortcut_path = os.path.join(desktop, "ReadVault.lnk")

    with winshell.shortcut(shortcut_path) as sc:
        sc.path        = pythonw
        sc.arguments   = f'"{app_script}"'
        sc.working_directory = os.path.dirname(app_script)
        sc.description = "ReadVault — My Reading Collection"
        if icon_path:
            sc.icon_location = (icon_path, 0)

    print(f"Shortcut created on Desktop: {shortcut_path}")


if __name__ == "__main__":
    try:
        import winshell
    except ImportError:
        print("Installing winshell...")
        os.system(f'"{sys.executable}" -m pip install winshell pywin32')
        import winshell

    try:
        from PIL import Image
    except ImportError:
        print("Installing Pillow for icon...")
        os.system(f'"{sys.executable}" -m pip install Pillow')

    create_shortcut()
    input("\nDone! Press Enter to close...")
