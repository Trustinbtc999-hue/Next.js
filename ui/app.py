"""System UI — Streamlit dashboard for the Next.js / MCP workspace."""

import json
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "cline_mcp_config.json")
DATA_PATH = os.path.join(ROOT, "data", "atlantis.csv")
# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="System UI",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("🛠️ System UI")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "MCP Servers", "Population Data", "Gnome Sort"],
)

# ══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.title("System Dashboard")

    col1, col2, col3 = st.columns(3)

    # MCP server count
    with col1:
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            n_servers = len(cfg.get("mcpServers", {}))
        except Exception:
            n_servers = "—"
        st.metric("MCP Servers", n_servers)

    # Data rows
    with col2:
        try:
            df = pd.read_csv(DATA_PATH)
            st.metric("Atlantis Records", len(df))
        except Exception:
            st.metric("Atlantis Records", "—")

    # Python version
    with col3:
        ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        st.metric("Python", ver)

    st.divider()
    st.subheader("Population trend (Atlantis)")
    try:
        df = pd.read_csv(DATA_PATH)
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(df["year"], df["population"], marker="o", linewidth=2, color="#4f8bf9")
        ax.fill_between(df["year"], df["population"], alpha=0.15, color="#4f8bf9")
        ax.set_xlabel("Year")
        ax.set_ylabel("Population")
        ax.set_title("Atlantis Population Over Time")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as exc:
        st.error(f"Could not load data: {exc}")

# ══════════════════════════════════════════════════════════════════════════════
# MCP Servers
# ══════════════════════════════════════════════════════════════════════════════
elif page == "MCP Servers":
    st.title("MCP Server Configuration")

    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        servers = cfg.get("mcpServers", {})
    except Exception as exc:
        st.error(f"Failed to load config: {exc}")
        st.stop()

    st.caption(f"Config file: `{CONFIG_PATH}`")
    st.write(f"**{len(servers)} server(s) registered**")

    for name, details in servers.items():
        with st.expander(f"🔌 {name}", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Command:** `{details.get('command', '—')}`")
                args = details.get("args", [])
                if args:
                    st.write("**Args:**")
                    st.code(" ".join(args), language="bash")
            with col_b:
                env = details.get("env", {})
                if env:
                    st.write("**Environment variables:**")
                    for k, v in env.items():
                        st.write(f"- `{k}` = `{v}`")

    st.divider()
    st.subheader("Raw JSON")
    st.json(cfg)

# ══════════════════════════════════════════════════════════════════════════════
# Population Data
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Population Data":
    st.title("Atlantis Population Data")

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        st.stop()

    col1, col2 = st.columns([3, 1])

    with col1:
        chart_type = st.selectbox("Chart type", ["Line", "Bar", "Area"])
        fig, ax = plt.subplots(figsize=(10, 4))
        if chart_type == "Line":
            ax.plot(df["year"], df["population"], marker="o", color="#4f8bf9", linewidth=2)
        elif chart_type == "Bar":
            ax.bar(df["year"], df["population"], color="#4f8bf9", alpha=0.8)
        else:
            ax.fill_between(df["year"], df["population"], alpha=0.4, color="#4f8bf9")
            ax.plot(df["year"], df["population"], color="#4f8bf9", linewidth=2)
        ax.set_xlabel("Year")
        ax.set_ylabel("Population")
        ax.set_title(f"Atlantis Population — {chart_type} Chart")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.write("**Statistics**")
        st.write(f"Min: **{df['population'].min():,}**")
        st.write(f"Max: **{df['population'].max():,}**")
        st.write(f"Mean: **{df['population'].mean():,.0f}**")
        growth = df["population"].iloc[-1] - df["population"].iloc[0]
        st.write(f"Total growth: **{growth:,}**")

    st.subheader("Data Table")
    st.dataframe(df, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# Gnome Sort
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Gnome Sort":
    st.title("Gnome Sort")
    st.markdown(
        "Enter a list of numbers to sort using the "
        "[gnome sort](https://en.wikipedia.org/wiki/Gnome_sort) algorithm."
    )

    def gnome_sort(arr: list) -> list:
        arr = arr[:]
        n = len(arr)
        index = 0
        while index < n:
            if index == 0 or arr[index] >= arr[index - 1]:
                index += 1
            else:
                arr[index], arr[index - 1] = arr[index - 1], arr[index]
                index -= 1
        return arr

    user_input = st.text_input(
        "Numbers (comma-separated)",
        value="5, 3, 8, 1, 9, 2",
        placeholder="e.g. 5, 3, 8, 1",
    )

    if st.button("Sort", type="primary"):
        try:
            nums = [int(x.strip()) for x in user_input.split(",") if x.strip()]
            if not nums:
                st.warning("Please enter at least one number.")
            else:
                result = gnome_sort(nums)
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Input**")
                    st.code(str(nums))
                with col2:
                    st.write("**Sorted**")
                    st.code(str(result))

                # visualise
                fig, axes = plt.subplots(1, 2, figsize=(10, 3))
                axes[0].bar(range(len(nums)), nums, color="#f97b4f", alpha=0.8)
                axes[0].set_title("Before")
                axes[0].set_xticks(range(len(nums)))
                axes[0].set_xticklabels(nums)
                axes[1].bar(range(len(result)), result, color="#4f8bf9", alpha=0.8)
                axes[1].set_title("After")
                axes[1].set_xticks(range(len(result)))
                axes[1].set_xticklabels(result)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        except ValueError:
            st.error("Please enter valid integers separated by commas.")
