"""Main Script for FPL Stats."""
from json import loads
from typing import Dict

import httpx
import numpy as np
import pandas as pd
import streamlit as st
import urllib

from constants import (
    POS_ID_TO_NAME,
    POS_NAME_TO_ID,
    TEAMS_NAME_TO_ID,
    TEAMS_ID_TO_NAME,
    TEAM_FULL_NAME_TO_ABBR,
)

OFFICIAL_STATS_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

VAASTAV_CSV_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/gw{gw}.csv"


@st.cache_data(ttl="6h")
def get_official_stats() -> Dict:
    """Get official stats as dictionary.

    Returns:
        Dict: official stats
    """
    response = httpx.get(OFFICIAL_STATS_URL)
    return loads(response.text)


@st.cache_data(ttl="6h")
def get_current_gw() -> int:
    """Get the current game week from the official stats

    Returns:
        int: 1-based game week count
    """

    stats = get_official_stats()

    events = stats.get("events", [])

    return max(
        (_["id"] if not _["finished"] else (_["id"] + 1))
        for _ in events
        if _["is_current"]
    )


def preprocess_players_df(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess official player stats dataframe.

    Args:
        df (pd.DataFrame): Raw player dataframe

    Returns:
        pd.DataFrame: Pre-processed player dataframe
    """
    df.index = pd.Series(df["first_name"] + " " + df["second_name"], name="Player")

    df["element_type"] = df["element_type"].map(POS_ID_TO_NAME)
    df["team"] = df["team"].map(TEAMS_ID_TO_NAME)

    df.insert(
        0,
        "Price Change",
        (
            df["cost_change_event"].apply(np.sign)
            + df["cost_change_start"].apply(np.sign)
        )
        .apply(np.sign)
        .map({-1: "⬇️", 0: " ", 1: "⬆️"}),
    )

    df = df.drop(
        [
            "id",
            "code",
            "photo",
            "first_name",
            "second_name",
            "squad_number",
            "team_code",
            "web_name",
            "chance_of_playing_next_round",
            "chance_of_playing_this_round",
            "cost_change_event",
            "cost_change_event_fall",
            "cost_change_start",
            "cost_change_start_fall",
            "selected_rank",
            "selected_rank_type",
            "points_per_game_rank",
            "points_per_game_rank_type",
            "form_rank",
            "form_rank_type",
            "now_cost_rank",
            "now_cost_rank_type",
            "ict_index_rank",
            "ict_index_rank_type",
            "threat_rank",
            "threat_rank_type",
            "creativity_rank",
            "creativity_rank_type",
            "influence_rank",
            "influence_rank_type",
        ],
        axis=1,
    )

    df = df.rename(
        {
            "element_type": "POS",
            "team": "Team",
            "status": "Status",
            "dreamteam_count": "No. Dream Team Entry",
            "in_dreamteam": "Dream Team Last Week?",
            "ep_this": "xPoint This GW",
            "ep_next": "xPoint Next GW",
            "now_cost": "Price",
        },
        axis=1,
    )

    df["Price"] /= 10
    return df


def get_gw_stats(gw: int):
    df = pd.read_csv(VAASTAV_CSV_URL.format(gw=gw))
    df["team"] = df["team"].map(TEAM_FULL_NAME_TO_ABBR)

    df = df.rename(
        {"name": "Player", "position": "POS", "team": "Team"},
        axis=1,
    )

    df = df.set_index("Player")

    return df


def increment_stat_gw(increment: int = 1) -> None:
    st.session_state["stat_gw"] += increment


def get_official_df() -> pd.DataFrame:
    response = get_official_stats()

    df = pd.DataFrame(response["elements"])

    df = preprocess_players_df(df)

    return df


def combine_df(df_filtered: pd.DataFrame, df_gw_stats: pd.DataFrame) -> pd.DataFrame:
    df_combined = df_filtered[
        ["Price Change", "Price", "xPoint This GW", "Dream Team Last Week?"]
    ].join(df_gw_stats)
    df_combined = df_combined.rename(
        {
            "Price Change": f"Price Change (GW{st.session_state['current_gw'] - 1} to GW{st.session_state['current_gw']})",
            "Price": f"Price (GW{st.session_state['current_gw']})",
            "xPoint This GW": f"xPoint (GW{st.session_state['current_gw']})",
            "Dream Team Last Week?": f"Dream Team GW{st.session_state['current_gw'] - 1}",
        },
        axis=1,
    )

    return df_combined


def main() -> None:
    """Render webapp."""
    st.title("FPL Stats")

    if "current_gw" not in st.session_state:
        current_gw = get_current_gw()
        stat_gw = current_gw - 1
        st.session_state["current_gw"] = current_gw
        st.session_state["stat_gw"] = current_gw - 1
    else:
        current_gw = st.session_state["current_gw"]
        stat_gw = st.session_state["stat_gw"]

    st.subheader(f"Game Week {current_gw}")

    pos = st.multiselect(label="Position", options=POS, default=POS)
    team = st.multiselect(label="Team", options=TEAMS, default=TEAMS)
    injured = st.checkbox("Include Injured Players?", value=False)
    unavailable = st.checkbox("Include Unavailable Player?", value=False)
    doubt = st.checkbox("Include Player in Doubt?", value=False)
    price_range = st.slider(
        "Price Range",
        float(df_all_players["Price"].min()),
        float(df_all_players["Price"].max()),
        (float(df_all_players["Price"].min()), float(df_all_players["Price"].max())),
        step=0.1,
    )

    df_filtered = df_all_players[df_all_players["POS"].isin(pos)]
    df_filtered = df_filtered[df_filtered["Team"].isin(team)]

    try:
        df_gw_stats = get_gw_stats(stat_gw)
        df_gw_stats = df_gw_stats[df_gw_stats["POS"].isin(pos)]
        df_gw_stats = df_gw_stats[df_gw_stats["Team"].isin(team)]

        if not injured:
            df_filtered = df_filtered[df_filtered["Status"] != "i"]

        if not unavailable:
            df_filtered = df_filtered[df_filtered["Status"] != "u"]

        if not doubt:
            df_filtered = df_filtered[df_filtered["Status"] != "d"]

        df_filtered = df_filtered[
            (df_filtered["Price"] >= price_range[0])
            & (df_filtered["Price"] <= price_range[1])
        ]

        st.subheader("Stats History")

        _ = st.columns((1.5, 3, 1.2, 3, 1.5))
        _[0].button(
            "⬅️ Previous Game Week",
            on_click=increment_stat_gw,
            args=(-1,),
            disabled=stat_gw <= 1,
        )
        _[2].caption(f"Stats from Game Week {stat_gw}")
        _[-1].button(
            "Next Game Week ➡️",
            on_click=increment_stat_gw,
            disabled=stat_gw >= current_gw - 1,
        )

        df_combined = combine_df(df_filtered, df_gw_stats)

        # Show the df broken down by player positions
        tabs = st.tabs(POS_NAME_TO_ID.keys())

        for t, p in zip(tabs, POS_NAME_TO_ID.keys()):
            with t:
                st.dataframe(df_combined[df_combined["POS"] == p].drop(["POS"], axis=1))

    except urllib.error.HTTPError:
        st.warning(f"Stats for GW {current_gw - 1} is not available yet.")


if __name__ == "__main__":
    st.set_page_config(page_title="FPL Stats", page_icon="⚽", layout="wide")

    POS = POS_NAME_TO_ID.keys()
    TEAMS = TEAMS_NAME_TO_ID.keys()

    df_all_players = get_official_df()

    main()
