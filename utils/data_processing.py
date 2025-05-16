import pandas as pd
import streamlit as st


@st.cache_data
def load_kicks_data():
    """
    Load and preprocess the kicks data.

    Returns:
        DataFrame: Processed kicks data
    """
    df = pd.read_csv("data/kicks.csv")
    return df


@st.cache_data
def load_fixtures_data():
    """
    Load fixtures data containing round information.

    Returns:
        DataFrame: Fixtures data
    """
    fixtures_df = pd.read_csv("data/fixtures.csv")
    return fixtures_df


def filter_kicks_data(df, fixtures_df, filters):
    """
    Apply filters to the kicks data.

    Args:
        df: Original kicks DataFrame
        fixtures_df: Fixtures DataFrame with round information
        filters: Dictionary of filter values

    Returns:
        DataFrame: Filtered kicks data
    """
    filtered_df = df.copy()

    # Apply round filter if selected
    if "round_range" in filters and len(fixtures_df) > 0:
        min_round, max_round = filters["round_range"]

        # Get game IDs that match the round range
        filtered_fixtures = fixtures_df[
            (fixtures_df["roundId"] >= min_round) &
            (fixtures_df["roundId"] <= max_round)
            ]

        # Apply venue filter
        if filters["venue"] != "All":
            filtered_fixtures = filtered_fixtures[filtered_fixtures["venueName"].astype(str) == filters["venue"]]

        # Apply ground condition filter
        if filters["ground_condition"] != "All":
            filtered_fixtures = filtered_fixtures[
                filtered_fixtures["groundConditionName"].astype(str) == filters["ground_condition"]]

        # Apply weather filter
        if filters["weather"] != "All":
            filtered_fixtures = filtered_fixtures[filtered_fixtures["weatherName"].astype(str) == filters["weather"]]

        # Get the remaining game IDs after all fixture filters
        round_games = filtered_fixtures["gameId"].unique()

        # Filter kicks by matching game IDs
        filtered_df = filtered_df[filtered_df["GameId"].isin(round_games)]

    # Apply team filters
    if filters["kicking_team"] != "All":
        filtered_df = filtered_df[filtered_df["TeamName"] == filters["kicking_team"]]
    if filters["receiving_team"] != "All":
        filtered_df = filtered_df[filtered_df["OppositionName"] == filters["receiving_team"]]

    # Apply player filter
    if filters["player"] != "All":
        filtered_df = filtered_df[filtered_df["PN"] == filters["player"]]

    # Apply type and outcome filters
    if filters["kick_type"] != "All":
        filtered_df = filtered_df[filtered_df["Type"] == filters["kick_type"]]
    if filters["kick_outcome"] != "All":
        filtered_df = filtered_df[filtered_df["Outcome"] == filters["kick_outcome"]]

    # Apply coordinate filters
    filtered_df = filtered_df[
        (filtered_df["NX"] >= filters["start_x_range"][0]) & (filtered_df["NX"] <= filters["start_x_range"][1]) &
        (filtered_df["NY"] >= filters["start_y_range"][0]) & (filtered_df["NY"] <= filters["start_y_range"][1]) &
        (filtered_df["nEX"] >= filters["end_x_range"][0]) & (filtered_df["nEX"] <= filters["end_x_range"][1]) &
        (filtered_df["nEY"] >= filters["end_y_range"][0]) & (filtered_df["nEY"] <= filters["end_y_range"][1])
        ]

    # Apply game time filters
    filtered_df = filtered_df[
        (filtered_df["GS"] >= filters["game_time_range"][0]) &
        (filtered_df["GS"] <= filters["game_time_range"][1])
        ]

    return filtered_df