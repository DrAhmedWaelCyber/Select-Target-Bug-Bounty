#!/usr/bin/env python3
"""
Select-Target: Intelligent Bug Bounty Target Selector & Surface Engine
Developed by: Ahmed Wael
Version: 2.0.0 Pro
"""

import argparse
import random
import sys
import time
from typing import List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich import box
except ImportError:
    print("[!] Error: 'rich' library is required. Please install it using: pip install rich")
    sys.exit(1)

from config import (
    TOOL_NAME,
    DEVELOPER,
    VERSION,
    DESCRIPTION,
    DATA_SOURCES
)
from data_manager import TargetDataManager

console = Console()

def display_banner():
    """Renders the cyber ASCII banner for Ahmed Wael."""
    ascii_art = r"""
 ███████╗███████╗██╗     ███████╗ ██████╗████████╗   ████████╗ █████╗ ██████╗  ██████╗ ███████╗████████╗
 ██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝ ██╔════╝╚══██╔══╝
 ███████╗█████╗  ██║     █████╗  ██║        ██║         ██║   ███████║██████╔╝██║  ███╗█████╗     ██║   
 ╚════██║██╔══╝  ██║     ██╔══╝  ██║        ██║         ██║   ██╔══██║██╔══██╗██║   ██║██╔══╝     ██║   
 ███████║███████╗███████╗███████╗╚██████╗   ██║         ██║   ██║  ██║██║  ██║╚██████╔╝███████╗   ██║   
 ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝         ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
"""
    banner_text = Text(ascii_art, style="bold cyan")
    banner_text.append(f"\n   ⚡ {DESCRIPTION} ⚡\n", style="italic bright_white")
    banner_text.append("   👑 Developed by: ", style="bold white")
    banner_text.append(f"{DEVELOPER}", style="bold yellow underline")
    banner_text.append(" | Version: ", style="bold white")
    banner_text.append(f"v{VERSION}\n", style="bold green")

    panel = Panel(
        banner_text,
        border_style="bold bright_blue",
        box=box.DOUBLE,
        padding=(0, 2)
    )
    console.print(panel)

def render_stats_dashboard(
    total_targets: int,
    platform_name: str,
    category_name: str,
    hunted_count: int,
    new_targets_count: int
):
    """Displays an intelligence summary dashboard."""
    table = Table(box=box.ROUNDED, expand=True, show_header=True, header_style="bold magenta")
    table.add_column("📊 Intelligence Metric", style="cyan", justify="left")
    table.add_column("📌 Value", justify="right")

    table.add_row("Active Platform Scope", f"[bold yellow]{platform_name.upper()}[/bold yellow]")
    table.add_row("Scope Filter Applied", f"[bold green]{category_name.upper()}[/bold green]")
    table.add_row("Qualified Targets Available", f"[bold white]{total_targets}[/bold white]")
    table.add_row("Previously Hunted Targets", f"[bold dim white]{hunted_count}[/bold dim white]")

    if new_targets_count > 0:
        table.add_row("🔥 Fresh Targets Detected", f"[bold red blink]{new_targets_count} NEW[/bold red blink]")

    console.print(Panel(table, title="[bold white]🎯 Live Catalog Overview[/bold white]", border_style="bold magenta"))

def display_target_card(target: dict, rank: Optional[int] = None):
    """Renders a beautiful detailed card for a selected target."""
    platform_colors = {
        "hackerone": "bold bright_cyan",
        "bugcrowd": "bold bright_yellow",
        "yeswehack": "bold bright_green"
    }
    plat_color = platform_colors.get(target["platform"], "bold white")
    
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Property", style="bold cyan", justify="right", width=18)
    table.add_column("Value", style="bold white")

    table.add_row("🎯 Target :", f"[bold bright_green]{target['identifier']}[/bold bright_green]")
    table.add_row("🏢 Program :", f"[bold white]{target['program']}[/bold white]")
    table.add_row("🌐 Platform :", f"[{plat_color}]{target['platform'].upper()}[/{plat_color}]")
    table.add_row("📦 Scope Category :", f"[bold yellow]{target['category'].upper()}[/bold yellow]")
    
    # Bounty Information
    if target.get("offers_bounty") or target.get("max_payout", 0) > 0:
        max_p = target.get("max_payout", 0)
        payout_str = f"[bold green]Cash Bounty Eligible (Max: ${max_p:,})[/bold green]" if max_p else "[bold green]Cash Bounty Eligible[/bold green]"
    else:
        payout_str = "[dim yellow]VDP / Hall of Fame[/dim yellow]"
    table.add_row("💰 Bounty Status :", payout_str)

    # Program Link
    prog_url = target.get("program_url", "")
    if prog_url:
        table.add_row("🔗 Program URL :", f"[u bright_blue]{prog_url}[/u bright_blue]")

    # AI Score Breakdown
    score = target.get("score", 0)
    prog_s = target.get("program_score", 0)
    juicy_s = target.get("juicy_score", 0)
    score_desc = f"[bold bright_yellow]{score} pts[/bold bright_yellow] [dim](Program: {prog_s} | Juiciness: {juicy_s})[/dim]"
    table.add_row("⭐ AI Score :", score_desc)

    # Tags
    tags = target.get("tags", [])
    if tags:
        tag_str = " ".join([f"[black on bright_cyan] {t} [/black on bright_cyan]" for t in tags])
        table.add_row("🏷️ Attributes :", tag_str)

    title_rank = f" [Rank #{rank}]" if rank else ""
    panel = Panel(
        table,
        title=f"[bold bright_white]🔥 RECOMMENDED TARGET{title_rank} 🔥[/bold bright_white]",
        border_style="bold bright_green",
        box=box.HEAVY,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)
    console.print()

def display_leaderboard_table(targets: List[dict], limit: int = 15):
    """Displays a leaderboard table of top-scoring targets."""
    table = Table(
        title=f"\n🏆 Top {min(limit, len(targets))} Best Bug Bounty Targets",
        box=box.ROUNDED,
        header_style="bold magenta",
        expand=True
    )
    table.add_column("#", justify="center", style="bold dim", width=4)
    table.add_column("Target (Scope)", style="bold bright_green", overflow="fold", min_width=25)
    table.add_column("Program", style="bold white", overflow="ellipsis", min_width=20)
    table.add_column("Platform", justify="center", style="bold yellow", width=12)
    table.add_column("Type", justify="center", style="cyan", width=10)
    table.add_column("Score", justify="right", style="bold bright_yellow", width=8)
    table.add_column("Key Tags", style="dim cyan", overflow="fold", min_width=15)

    for idx, t in enumerate(targets[:limit], 1):
        tags_preview = ", ".join(t.get("tags", [])[:3])
        table.add_row(
            str(idx),
            t["identifier"],
            t["program"][:28] + ("…" if len(t["program"]) > 28 else ""),
            t["platform"].upper(),
            t["category"],
            str(t.get("score", 0)),
            tags_preview
        )

    console.print(table)
    console.print()

def export_targets_to_file(targets: List[dict], filepath: str = "targets.txt"):
    """Exports target identifiers to a clean text file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for t in targets:
                f.write(f"{t['identifier']}\n")
        console.print(f"[bold green]✔ Successfully exported {len(targets)} targets to: [bold white]{filepath}[/bold white][/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]✘ Failed to export targets: {e}[/bold red]\n")

def interactive_loop():
    """Main interactive terminal flow."""
    display_banner()
    dm = TargetDataManager()

    # Step 1: Select Platform
    console.print("[bold bright_white]─── Step 1: Select Bounty Platform ───[/bold bright_white]")
    console.print("[1] 🦊 [bold]YesWeHack[/bold] (European & Global Programs)")
    console.print("[2] 🐛 [bold]Bugcrowd[/bold] (Managed & Enterprise Programs)")
    console.print("[3] 🎯 [bold]HackerOne[/bold] (Largest Global Programs)")
    console.print("[4] 🌐 [bold]All Platforms Combined[/bold] (Aggregated Intelligence)")
    
    plat_choice = Prompt.ask("\nChoose Platform", choices=["1", "2", "3", "4"], default="4")
    plat_map = {"1": "yeswehack", "2": "bugcrowd", "3": "hackerone", "4": "all"}
    selected_platform = plat_map[plat_choice]

    # Step 2: Select Scope Type
    console.print("\n[bold bright_white]─── Step 2: Select Target Scope Type ───[/bold bright_white]")
    console.print("[1] 🌐 [bold]Wildcards Only[/bold] (*.example.com - Broad Attack Surface)")
    console.print("[2] 🎯 [bold]Single Domains Only[/bold] (specific hostnames / APIs / apps)")
    console.print("[3] ⚡ [bold]Both / All[/bold] (Wildcards & Specific Domains)")
    
    type_choice = Prompt.ask("\nChoose Scope Type", choices=["1", "2", "3"], default="1")
    type_map = {"1": "wildcard", "2": "domain", "3": "all"}
    selected_category = type_map[type_choice]

    # Data Fetching & Sync
    console.print()
    with console.status("[bold green]📡 Checking GitHub for updates & analyzing targets...", spinner="dots12"):
        targets = dm.get_processed_targets(
            platform_choice=selected_platform,
            category_filter=selected_category,
            force_refresh=False
        )
        time.sleep(0.5)

    if not targets:
        console.print("[bold red]❌ No targets found matching your criteria. Try different options.[/bold red]")
        return

    # Dashboard overview
    hunted_count = dm.get_known_history_count()
    new_count = len([t for t in targets if t.get("is_new")])
    render_stats_dashboard(
        len(targets),
        selected_platform,
        selected_category,
        hunted_count,
        new_count
    )

    # Action Menu
    while True:
        console.print("[bold bright_white]─── Choose What To Do Next ───[/bold bright_white]")
        console.print("[1] 🎯 [bold bright_green]Recommend The #1 Best Target[/bold bright_green] (AI Top Pick)")
        console.print("[2] 🏆 [bold bright_yellow]Top 15 Leaderboard Table[/bold bright_yellow] (Ranked List)")
        console.print("[3] 🎲 [bold bright_cyan]Smart Random Pick[/bold bright_cyan] (From Top 10% Tier)")
        console.print("[4] 🔍 [bold bright_white]Search & Filter by Keyword[/bold bright_white] (e.g. 'api', 'pay', 'cloud')")
        console.print("[5] 💾 [bold magenta]Export In-Scope Targets[/bold magenta] (Save to targets.txt)")
        console.print("[6] 🔄 [bold blue]Force Database Re-Sync[/bold blue] (Pull latest GitHub commits)")
        console.print("[0] 🚪 [bold red]Exit[/bold red]")

        action = Prompt.ask("\nSelect Action", choices=["1", "2", "3", "4", "5", "6", "0"], default="1")

        if action == "1":
            top_target = targets[0]
            display_target_card(top_target, rank=1)
            
            # Offer to mark as hunted
            if Confirm.ask("[bold dim]Mark this target as hunted in your session history?[/bold dim]", default=False):
                dm.record_hunted_target(top_target["identifier"])
                console.print("[bold green]✔ Saved to history.[/bold green]\n")

        elif action == "2":
            display_leaderboard_table(targets, limit=15)
            
            # Offer to mark all displayed targets as seen
            displayed_targets = targets[:15]
            if Confirm.ask("\n[bold dim]Hide these targets so they don't appear again?[/bold dim]", default=False):
                for t in displayed_targets:
                    dm.record_hunted_target(t["identifier"])
                console.print(f"[bold green]✔ {len(displayed_targets)} targets hidden. They won't appear next time.[/bold green]\n")
                # Remove them from current session list too so subsequent actions don't show them
                targets = [t for t in targets if t not in displayed_targets]

        elif action == "3":
            top_tier_size = max(5, len(targets) // 10)
            pool = targets[:top_tier_size]
            selected = random.choice(pool)
            rank = targets.index(selected) + 1
            display_target_card(selected, rank=rank)
            
            if Confirm.ask("[bold dim]Hide this target so it doesn't appear again?[/bold dim]", default=False):
                dm.record_hunted_target(selected["identifier"])
                console.print("[bold green]✔ Target hidden.[/bold green]\n")
                targets.remove(selected)

        elif action == "4":
            keyword = Prompt.ask("[bold cyan]Enter keyword to search (domain, program, or tag)[/bold cyan]").strip().lower()
            if keyword:
                matches = [
                    t for t in targets
                    if keyword in t["identifier"].lower()
                    or keyword in t["program"].lower()
                    or any(keyword in tag.lower() for tag in t.get("tags", []))
                ]
                if matches:
                    console.print(f"\n[bold green]Found {len(matches)} targets matching '{keyword}':[/bold green]")
                    display_leaderboard_table(matches, limit=15)
                else:
                    console.print(f"[bold yellow]No targets matched '{keyword}'.[/bold yellow]\n")

        elif action == "5":
            out_file = Prompt.ask("[bold cyan]Enter export filename[/bold cyan]", default="targets.txt").strip()
            export_targets_to_file(targets, filepath=out_file)

        elif action == "6":
            with console.status("[bold blue]🔄 Force refreshing all data directly from GitHub...", spinner="aesthetic"):
                targets = dm.get_processed_targets(
                    platform_choice=selected_platform,
                    category_filter=selected_category,
                    force_refresh=True
                )
            console.print("[bold green]✔ Successfully refreshed from GitHub![/bold green]\n")

        elif action == "0":
            console.print(f"\n[bold green]Happy Hacking, {DEVELOPER}! Hunt well![/bold green]\n")
            break

def main():
    parser = argparse.ArgumentParser(
        description=f"{TOOL_NAME} - Bug Bounty Target Selector by {DEVELOPER}"
    )
    parser.add_argument(
        "-p", "--platform",
        choices=["yeswehack", "bugcrowd", "hackerone", "all"],
        help="Specify platform to search"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["wildcard", "domain", "all"],
        help="Target scope type: wildcard or domain"
    )
    parser.add_argument(
        "--best",
        action="store_true",
        help="Instantly pick the #1 best target"
    )
    parser.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="Display top N targets"
    )
    parser.add_argument(
        "-e", "--export",
        metavar="FILE",
        help="Export targets to file"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-sync data from GitHub"
    )

    args = parser.parse_args()

    # If no flags passed, launch the interactive UI
    if not any([args.platform, args.type, args.best, args.top, args.export, args.refresh]):
        interactive_loop()
        return

    # CLI headless mode
    display_banner()
    dm = TargetDataManager()
    platform = args.platform or "all"
    category = args.type or "all"

    with console.status("[bold green]Fetching & ranking targets...", spinner="dots12"):
        targets = dm.get_processed_targets(
            platform_choice=platform,
            category_filter=category,
            force_refresh=args.refresh
        )

    if not targets:
        console.print("[bold red]No targets found.[/bold red]")
        return

    if args.best:
        display_target_card(targets[0], rank=1)
    elif args.top:
        display_leaderboard_table(targets, limit=args.top)
    else:
        display_leaderboard_table(targets, limit=10)

    if args.export:
        export_targets_to_file(targets, filepath=args.export)

if __name__ == "__main__":
    main()
