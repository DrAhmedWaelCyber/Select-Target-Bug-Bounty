<div align="center">

# 🎯 Select-Target

**The Next-Generation Intelligent Bug Bounty Target Selector & Surface Engine**

<p align="center">
  <a href="https://github.com/DrAhmedWaelCyber/Select-Target-Bug-Bounty/releases">
    <img src="https://img.shields.io/badge/Version-2.0.0_Pro-blue.svg?style=for-the-badge&logo=github" alt="Version">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://github.com/DrAhmedWaelCyber/Select-Target-Bug-Bounty/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="License">
  </a>
</p>

<p align="center">
  <i>Stop wasting time on saturated targets. Let AI find your next critical bug.</i>
</p>

<p align="center">
  Developed with ❤️ by <b><a href="https://github.com/DrAhmedWaelCyber">Ahmed Wael</a></b>
</p>

<hr>
</div>

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [How The Engine Works](#-how-the-engine-works)
- [Installation](#-installation)
- [Usage & Commands](#-usage--commands)
- [Developer & Contributions](#-developer--contributions)
- [License](#-license)

---

## 🚀 About the Project

**Select-Target** is an advanced reconnaissance orchestrator designed to eliminate "target fatigue." Built specifically for modern bug bounty hunters, it dynamically aggregates, filters, and intelligently scores bug bounty programs from the world's top platforms (**HackerOne, Bugcrowd, YesWeHack**).

Instead of manually scrolling through hundreds of programs, **Select-Target** acts as your personal AI assistant. By analyzing attack surfaces, payout structures, historical saturation, and environmental keywords (e.g., `api`, `staging`, `k8s`), the engine surfaces the absolute most lucrative and least-saturated targets—allowing you to focus exclusively on hacking.

---

## ✨ Key Features

- 🧠 **Intelligent Heuristic Scoring:** Automatically ranks targets based on "juiciness" (API, Staging, Cloud infra), bounty limits, and program triage responsiveness.
- 🔄 **Smart Freshness Engine:** Detects newly added scope across all platforms and applies an instant priority boost, ensuring you're always the first to attack.
- 🙈 **Session History & Hide Mode:** A built-in tracking system remembers your "hunted" targets and hides them from future runs, acting as a continuously refreshing pipeline of untouched scopes.
- 🎛️ **Granular Scope Filtering:** Seamlessly toggle between **Wildcards** (for broad attack surface discovery) and **Single Domains** (for deep-dive app focus).
- 📊 **Real-time Terminal Dashboard:** Experience a beautiful, interactive CLI built with `rich`, featuring dashboards, top 15 leaderboards, and detailed target intel cards.
- ⚡ **Offline-Capable Cache:** Automatically syncs the latest data from GitHub and caches it locally for ultra-fast, offline-capable querying.

---

## 🔬 How The Engine Works

The core scoring engine (`scoring_engine.py`) goes far beyond simple sorting. It evaluates targets using a multi-layered algorithmic approach:

1. **Keyword Analysis:** Awards massive priority points to subdomains mentioning high-value targets like `dev`, `uat`, `api`, `graphql`, `vpn`, and `admin`.
2. **Saturation Penalties:** Intelligently down-ranks heavily hardened "giant" companies where low-hanging fruit has long been exhausted.
3. **Bounty Economics:** Favors programs offering direct cash bounties and fast, managed triage over slow VDPs.
4. **Subdomain Depth Detection:** Identifies deep, complex subdomains that automated mass-scanners typically overlook.
5. **Freshness Multiplier:** Applies a $+1000$ point boost to brand-new targets appearing in the latest data sync.
6. **Anti-Stagnation Jitter:** Injects micro-randomization into rankings to ensure you never stare at the exact same leaderboard twice.

---

## 🛠️ Installation

**Select-Target** is lightweight and easy to set up on Linux, macOS, or Windows (WSL).

```bash
# 1. Clone the repository
git clone https://github.com/DrAhmedWaelCyber/Select-Target-Bug-Bounty.git
cd Select-Target-Bug-Bounty

# 2. Install the required dependencies
pip install -r requirements.txt
```

---

## 🎮 Usage & Commands

You can use the tool interactively or via command-line arguments for headless automation.

### 🌟 Interactive Mode
Simply run the script with no arguments to launch the beautiful terminal dashboard:
```bash
python3 main.py
```

### ⚡ CLI Quick Automation
Integrate **Select-Target** directly into your bash scripts and recon pipelines (like `subfinder` or `httpx`):

```bash
# Instantly grab the #1 recommended target
python3 main.py --best

# Display the top 20 targets across all aggregated platforms
python3 main.py --top 20

# Export targets to a text file to feed into your recon workflow
python3 main.py -e targets.txt

# Force refresh the local database with upstream changes
python3 main.py --refresh
```

---

## 👨‍💻 Developer & Contributions

**Ahmed Wael**  
*Cyber Security Researcher & Bug Bounty Hunter*  
- GitHub: [@DrAhmedWaelCyber](https://github.com/DrAhmedWaelCyber)

Pull requests, feature suggestions, and bug reports are highly welcome! Feel free to open an issue or submit a PR to help improve the tool.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br>

<div align="center">
<i>"The best bug is the one no one else is looking for."</i>
</div>
