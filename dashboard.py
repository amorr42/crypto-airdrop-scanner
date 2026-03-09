"""
DASHBOARD - Terminal earnings panel (powered by the Rich library)
"""
import sqlite3
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
from config import WALLET_ADDRESS, DB_FILE

console = Console()


def get_total_earnings() -> dict:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT currency, SUM(usd_value), COUNT(*)
        FROM faucet_claims WHERE status != 'FAIL'
        GROUP BY currency
    """)
    rows = c.fetchall()
    conn.close()
    return {r[0]: {"usd": r[1] or 0, "count": r[2]} for r in rows}


def get_today_earnings() -> float:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(SUM(usd_value), 0)
        FROM faucet_claims
        WHERE date(claimed_at) = date('now') AND status != 'FAIL'
    """)
    val = c.fetchone()[0]
    conn.close()
    return val


def get_airdrop_count() -> dict:
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*), SUM(participated) FROM airdrops")
        total, participated = c.fetchone()
        conn.close()
        return {"total": total or 0, "participated": participated or 0}
    except Exception:
        return {"total": 0, "participated": 0}


def render_dashboard():
    """Single-pass dashboard view."""
    earnings = get_total_earnings()
    today_usd = get_today_earnings()
    total_usd = sum(v["usd"] for v in earnings.values())
    airdrops = get_airdrop_count()

    console.clear()

    # Header
    console.print(Panel.fit(
        f"[bold cyan]AUTONOMOUS EARNINGS SYSTEM[/bold cyan]\n"
        f"[dim]Wallet: {WALLET_ADDRESS[:20]}...{WALLET_ADDRESS[-6:] if len(WALLET_ADDRESS) > 26 else WALLET_ADDRESS}[/dim]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        box=box.DOUBLE_EDGE,
        style="cyan"
    ))

    # Summary cards
    console.print()
    console.print(f"  [bold green]Today:[/bold green] ${today_usd:.4f}  "
                  f"[bold yellow]Total:[/bold yellow] ${total_usd:.4f}  "
                  f"[bold blue]Airdrops:[/bold blue] {airdrops['total']} found / {airdrops['participated']} joined")
    console.print()

    # Faucet table
    if earnings:
        table = Table(title="Faucet Earnings by Coin", box=box.ROUNDED)
        table.add_column("Coin", style="cyan", width=8)
        table.add_column("Claims", justify="right")
        table.add_column("USD Value", justify="right", style="green")
        for currency, data in earnings.items():
            table.add_row(currency, str(data["count"]), f"${data['usd']:.6f}")
        console.print(table)
    else:
        console.print("  [yellow]No faucet claim records yet. Data will appear once the bots start running.[/yellow]")

    # Airdrop table
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT project, chain, est_value_usd, deadline, participated
            FROM airdrops ORDER BY est_value_usd DESC LIMIT 10
        """)
        rows = c.fetchall()
        conn.close()
        if rows:
            at = Table(title="Top 10 Airdrops by Estimated Value", box=box.ROUNDED)
            at.add_column("Project", style="magenta")
            at.add_column("Chain", width=8)
            at.add_column("~Value", justify="right", style="yellow")
            at.add_column("Deadline", width=12)
            at.add_column("Joined", justify="center")
            for row in rows:
                p, ch, val, dl, part = row
                at.add_row(
                    p, ch,
                    f"${val:.0f}" if val else "?",
                    (dl or "")[:10],
                    "Yes" if part else "No"
                )
            console.print(at)
    except Exception:
        pass

    console.print()
    console.print("  [dim]Press CTRL+C and re-run to refresh. Bots are active in the background.[/dim]")


if __name__ == "__main__":
    render_dashboard()
