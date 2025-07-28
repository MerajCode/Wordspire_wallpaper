<h1 align="center">W O R D S P I R E</h1>



<h3 align="center">One Word, One Quote, Endless Inspiration</h3>

---

> A minimalist desktop companion that refreshes your wallpaper with motivational quotes and vocabulary — whenever your desktop is in focus.

---

## ✨ Features

- 🎯 **Smart Wallpaper Changer**  
  Automatically detects when you're on the desktop and updates the wallpaper.

- 💡 **Motivational & Educational**  
  Displays a meaningful quote and a vocabulary word with meaning & example.

- 🛠️ **Custom Content Management**  
  Add, edit, or delete your own quotes and words via a simple UI.

- 🕶️ **Runs Silently**  
  Starts with Windows and works in the background without interrupting your workflow.

- 🌙 **Modern UI**  
  Beautiful dark-themed interface for easy interaction.

---

## 🚀 Getting Started

### 🧩 Requirements

- Python 3.8+
- [`pystray`](https://pypi.org/project/pystray/)
- `pillow`, `pywin32`, `tkinter`
- `wkhtmltoimage.exe` in root directory for image rendering

```bash
pip install pystray pillow pywin32 pyinstaller
```
Build exe file
```bash
pyinstaller start.spec
```
#### 🧰 Creating an Installer (Optional)
- Install [NSIS](https://nsis.sourceforge.io/Download).
- Use your installer.nsi script to define how files should be copied (e.g., to %APPDATA%).

- Compile the installer.nsi script via the NSIS compiler to generate the installer.


## 📌 License

This project is licensed under a **custom license** designed to allow open collaboration while protecting the original author's rights.

You are free to:
- View, modify, and use the code for personal or educational purposes
- Contribute improvements via pull requests

You are **not allowed** to:
- Publish, distribute, or re-upload this project (even modified) to any app store or public platform
- Use the original name, branding, or UI/UX for redistribution
- Use the project commercially without permission

Only the original author holds the rights to officially publish or distribute this app.

➡️ See the full [LICENSE](./LICENSE) file for detailed terms.


 About the Developer 
--------------------------------------------------------------------------------

Wordspire was created with by merajcode.

To find more projects or to get in touch, please visit:

-   **YouTube:** https://www.youtube.com/@merajcode

================================================================================
          Thank you for being a part of the Wordspire community!
================================================================================
