"""Main Script for FPL Stats."""
from json import loads
from typing import Dict

import httpx
import numpy as np
import pandas as pd
import streamlit as st

POS = ["GK", "DEF", "MID", "FWD"]

POS_ID_TO_NAME = {k + 1: v for k, v in enumerate(POS)}
POS_NAME_TO_ID = {v: k + 1 for k, v in enumerate(POS)}

TEAMS = [
    "ARS",
    "AVL",
    "BOU",
    "BRE",
    "BHA",
    "BUR",
    "CHE",
    "CRY",
    "EVE",
    "FUL",
    "LIV",
    "LUT",
    "MCI",
    "MUN",
    "NEW",
    "NFO",
    "SHU",
    "TOT",
    "WHU",
    "WOL",
]

TEAMS_ID_TO_NAME = {k + 1: v for k, v in enumerate(TEAMS)}
TEAMS_NAME_TO_ID = {v: k + 1 for k, v in enumerate(TEAMS)}

OFFICIAL_STATS_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"


@st.cache_data(ttl="6h")
def get_official_stats() -> Dict:
    """Get official stats as dictionary.

    Returns:
        Dict: official stats
    """
    response = httpx.get(OFFICIAL_STATS_URL)
    return loads(response.text)


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
        1,
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


def main() -> None:
    """Render webapp."""
    st.title("FPL Stats")

    response = get_official_stats()

    all_players = pd.DataFrame(response["elements"])

    all_players = preprocess_players_df(all_players)

    pos = st.multiselect(label="Position", options=POS, default=POS)
    team = st.multiselect(label="Team", options=TEAMS, default=TEAMS)
    injured = st.checkbox("Include Injured Players?", value=False)
    unavailable = st.checkbox("Include Unavailable Player?", value=False)
    doubt = st.checkbox("Include Player in Doubt?", value=False)
    price_range = st.slider(
        "Price Range",
        float(all_players["Price"].min()),
        float(all_players["Price"].max()),
        (float(all_players["Price"].min()), float(all_players["Price"].max())),
        step=0.1,
    )

    all_players = all_players[all_players["POS"].isin(pos)]
    all_players = all_players[all_players["Team"].isin(team)]

    if not injured:
        all_players = all_players[all_players["Status"] != "i"]

    if not unavailable:
        all_players = all_players[all_players["Status"] != "u"]

    if not doubt:
        all_players = all_players[all_players["Status"] != "d"]

    all_players = all_players[
        (all_players["Price"] >= price_range[0])
        & (all_players["Price"] <= price_range[1])
    ]

    st.dataframe(all_players)


if __name__ == "__main__":
    st.set_page_config(page_title="FPL Stats", page_icon="⚽", layout="wide")
    main()
