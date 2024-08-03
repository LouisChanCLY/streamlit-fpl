"""Main Script for FPL Stats."""

from typing import Dict

import httpx
import numpy as np
import pandas as pd
import streamlit as st
from constants import (
    POS_ID_TO_NAME,
    TEAMS_ID_TO_NAME,
)
from models import (
    Event,
    Player,
    Team,
    Position,
    PositionList,
    PlayerList,
    EventList,
    TeamList,
)

BASE_URL = "https://fantasy.premierleague.com/api"
STATIC_DATA_URL = BASE_URL + "/bootstrap-static/"


@st.cache_data(ttl="6h")
def get_official_stats() -> Dict:
    """Get official stats as dictionary.

    Returns:
        Dict: official stats
    """
    response = httpx.get(STATIC_DATA_URL)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl="6h")
def parse_official_stats() -> None:

    response = get_official_stats()
    teams = [Team.model_validate(team) for team in response["teams"]]
    players = [Player.model_validate(player) for player in response["elements"]]
    events = [Event.model_validate(event) for event in response["events"]]
    positions = [
        Position.model_validate(position) for position in response["element_types"]
    ]
    st.session_state["teams"] = TeamList(teams=teams)
    st.session_state["players"] = PlayerList(players=players)
    st.session_state["events"] = EventList(events=events)
    st.session_state["positions"] = PositionList(positions=positions)


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

    with st.sidebar:
        st.session_state  # pylint: disable=pointless-statement

    parse_official_stats()
    events: EventList = st.session_state["events"]

    st.subheader(events.current_event_name)

    pos = st.multiselect(
        label="Position",
        options=st.session_state["positions"].plural_names,
        default=st.session_state["positions"].plural_names,
    )
    # team = st.multiselect(label="Team", options=TEAMS, default=TEAMS)
    # injured = st.checkbox("Include Injured Players?", value=False)
    # unavailable = st.checkbox("Include Unavailable Player?", value=False)
    # doubt = st.checkbox("Include Player in Doubt?", value=False)
    # price_range = st.slider(
    #     "Price Range",
    #     float(df_all_players["Price"].min()),
    #     float(df_all_players["Price"].max()),
    #     (float(df_all_players["Price"].min()), float(df_all_players["Price"].max())),
    #     step=0.1,
    # )

    # df_filtered = df_all_players[df_all_players["POS"].isin(pos)]
    # df_filtered = df_filtered[df_filtered["Team"].isin(team)]

    # try:
    #     df_gw_stats = get_gw_stats(stat_gw)
    #     df_gw_stats = df_gw_stats[df_gw_stats["POS"].isin(pos)]
    #     df_gw_stats = df_gw_stats[df_gw_stats["Team"].isin(team)]

    #     if not injured:
    #         df_filtered = df_filtered[df_filtered["Status"] != "i"]

    #     if not unavailable:
    #         df_filtered = df_filtered[df_filtered["Status"] != "u"]

    #     if not doubt:
    #         df_filtered = df_filtered[df_filtered["Status"] != "d"]

    #     df_filtered = df_filtered[
    #         (df_filtered["Price"] >= price_range[0])
    #         & (df_filtered["Price"] <= price_range[1])
    #     ]

    #     st.subheader("Stats History")

    #     _ = st.columns((1.5, 3, 1.2, 3, 1.5))
    #     _[0].button(
    #         "⬅️ Previous Game Week",
    #         on_click=increment_stat_gw,
    #         args=(-1,),
    #         disabled=stat_gw <= 1,
    #     )
    #     _[2].caption(f"Stats from Game Week {stat_gw}")
    #     _[-1].button(
    #         "Next Game Week ➡️",
    #         on_click=increment_stat_gw,
    #         disabled=stat_gw >= current_gw - 1,
    #     )

    #     df_combined = combine_df(df_filtered, df_gw_stats)

    #     # Show the df broken down by player positions
    #     tabs = st.tabs(POS_NAME_TO_ID.keys())

    #     for tab, pos in zip(tabs, POS_NAME_TO_ID.keys()):
    #         with tab:
    #             st.dataframe(
    #                 df_combined[df_combined["POS"] == pos].drop(
    #                     ["POS"],
    #                     axis=1,
    #                 )
    #             )

    # except urllib.error.HTTPError:
    #     st.warning(f"Stats for GW {current_gw - 1} is not available yet.")


if __name__ == "__main__":
    st.set_page_config(page_title="FPL Stats", page_icon="⚽", layout="wide")

    main()
