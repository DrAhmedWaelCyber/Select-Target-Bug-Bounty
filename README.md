<div align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0%20Pro-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8%2B-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
  
  <h1>🎯 Select-Target</h1>
  <p><strong>Intelligent Bug Bounty Target Selector & Surface Engine</strong></p>
  <p><i>Stop wasting time on saturated targets. Let AI find your next critical bug.</i></p>

  <p>Developed with ❤️ by <b>Ahmed Wael</b></p>
</div>

<hr>

## 🚀 Overview

**Select-Target** is a next-generation bug bounty reconnaissance orchestrator designed to eliminate target fatigue. Built for modern hunters, it dynamically aggregates, filters, and intelligently scores bug bounty programs from top platforms (**HackerOne, Bugcrowd, YesWeHack**). 

By analyzing attack surfaces, payout structures, historical saturation, and environmental keywords (like `api`, `staging`, `k8s`), the intelligent engine surfaces the absolute most lucrative and least-saturated targets—allowing you to focus on hacking, not scrolling.

## ✨ Key Features

- **🧠 Intelligent Heuristic Scoring:** Ranks targets automatically based on juiciness (API, Staging, Cloud infra), bounty limits, and program responsiveness.
- **🔄 Smart Freshness Engine:** Detects newly added scope and boosts its score instantly so you're always the first to attack.
- **🙈 Session History & Hide Mode:** Say goodbye to repetitive results. The tool automatically tracks your "hunted" targets and hides them from future runs, acting as a continuously refreshing pipeline of fresh scopes.
- **🎛️ Scope Filtering:** Seamlessly toggle between **Wildcards** (broad recon) and **Single Domains** (deep-dive focus).
- **📊 Real-time Dashboard:** Beautiful interactive terminal UI built with `rich`, featuring dashboards, top 15 leaderboards, and detailed target cards.
- **⚡ Offline-Capable Cache:** Automatically syncs the latest data from GitHub and caches it locally for ultra-fast, offline querying.

## 🛠️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/DrAhmedWaelCyber/Select-Target-Bug-Bounty.git
cd Select-Target-Bug-Bounty

# 2. Install required dependencies
pip install -r requirements.txt
```

## 🎮 Usage

Simply run the tool without any flags to enter the **Interactive Dashboard Mode**:

```bash
python3 main.py
```

### ⚡ CLI Quick Options
For headless operations, you can pass arguments directly:
```bash
# Get the #1 best recommended target instantly
python3 main.py --best

# Display the top 20 targets across all platforms
python3 main.py --top 20

# Export targets to a text file for your recon pipelines (e.g. subfinder)
python3 main.py -e targets.txt

# Force refresh local database with upstream changes
python3 main.py --refresh
```

## 💡 How The Scoring Works

The engine (`scoring_engine.py`) isn't just sorting alphabetically. It evaluates:
1. **Keyword Analysis:** Awards massive points to endpoints mentioning `dev`, `uat`, `api`, `graphql`, `vpn`, and more.
2. **Saturation Penalties:** Down-ranks heavily hardened "giant" companies where low-hanging fruit is exhausted.
3. **Bounty Economics:** Favors programs offering cash bounties and managed triage.
4. **Subdomain Depth:** Identifies deep subdomains that automated scanners often miss.
5. **Freshness:** Gives a $+1000$ point boost to brand-new targets appearing in the latest sync.

## 👨‍💻 Developer

**Ahmed Wael**  
Cyber Security Researcher & Bug Bounty Hunter  
GitHub: [@DrAhmedWaelCyber](https://github.com/DrAhmedWaelCyber)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
<i>"The best bug is the one no one else is looking for."</i>
</div>
