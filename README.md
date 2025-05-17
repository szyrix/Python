# 🎮 Discord Priority Setter

A lightweight utility that ensures **Discord.exe** always runs with your desired CPU priority — even while gaming.

---

## ❗ Background – Why this tool?

Windows sometimes lowers the process priority of **Discord** when you launch or run CPU-heavy games.  
This can result in:

- Choppy or delayed voice chat
- Laggy screen sharing
- Slow Discord responsiveness

If you're gaming and using Discord to communicate, this can become a real issue.

---

## 🚀 How does it work?

This tool **replaces the standard Discord launcher**.

- You use this tool to launch Discord instead of clicking the regular shortcut.
- It monitors the `Discord.exe` process in the background.
- If Discord is not running, it starts it for you.
- If Discord is running at a lower-than-desired priority, it raises it automatically.

In short:  
✅ **You start Discord with this launcher — and it takes care of the rest.**

---

## ✅ Features

- 🧠 Auto-detects Discord and adjusts its process priority
- 🔄 Reload settings live (type `r` in terminal)
- 💾 Very low CPU and memory impact
- 🧩 Configurable via `config.txt`
- 👤 No admin required (unless your system needs it to change priorities)

---

## ⚙️ Configuration

On first run, a `config.txt` file will be created automatically:

- Configuration for Discord Priority Setter

- Set the full path to your Discord.exe below:

  discord_path=C:\Path\To\Discord.exe

- Priority options: low, below_normal, normal, above_normal, high, realtime

  priority=high

- Interval in seconds between priority checks

  interval=15

- To reload settings live, just type r and press Enter in the terminal. To quit and stop Discord, type q.

---

## 🖥️ How to Use

### 🐍 Option 1: Run with Python

Install Python 3.x if not already installed.

Install required dependencies:

```bash
pip install psutil
```

Run the launcher:

```bash
python discord_priority_launcher.py
```

### 📦 Option 2: Download the EXE

You can download the precompiled .exe from the Releases page.
Just double-click to launch Discord with priority control. No installation required.

Make a shortcut to the .exe and use that instead of your regular Discord shortcut.

---

## ❌ Limitations

Windows only

This is not a background service; it runs in a terminal window

You must start Discord through this tool for it to work

---

## 🔒 Safety & Behavior

This tool does not modify Discord itself

It does not inject into any processes or hook anything

It only watches for Discord.exe and adjusts its priority

---

## 🙋 Feedback or Questions?

Open an Issue or submit a Pull Request.

---

## 📄 License

MIT License — see LICENSE file for details.

---
