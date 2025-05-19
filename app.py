import streamlit as st
import pandas as pd
from utils.data_processing import load_kicks_data, load_fixtures_data, filter_kicks_data
from utils.visualisation import create_kicks_visualization

# Page config
st.set_page_config(layout="wide", page_title="Rugby League Kicks Analyzer")
st.title("Rugby League Kicks Visualisation")

# Load data
df = load_kicks_data()
fixtures_df = load_fixtures_data()

# Get slider ranges
x_min, x_max = -100, 1100
y_min, y_max = 0, 700
end_x_min, end_x_max = -100, 1100
end_y_min, end_y_max = 0, 700
game_time_min, game_time_max = 0, 4800

# Get round range from fixtures data
if not fixtures_df.empty:
    round_min, round_max = int(fixtures_df["roundId"].min()), int(fixtures_df["roundId"].max())
else:
    round_min, round_max = 1, 30  # Default range if fixtures data is missing

# Create sidebar filters
with st.sidebar:
    st.header("Filters")

    # Round filter
    st.subheader("Round Filter")
    round_range = st.slider("Round Number",
                            round_min,
                            round_max,
                            (round_min, round_max),
                            step=1)

    # Team filters
    st.subheader("Team Filters")
    kicking_team = st.selectbox("Kicking Team", options=["All"] + sorted(df["TeamName"].unique().tolist()))
    receiving_team = st.selectbox("Receiving Team", options=["All"] + sorted(df["OppositionName"].unique().tolist()))

    # Filter data for player dropdown based on team selection
    if kicking_team != "All":
        team_players = df[df["TeamName"] == kicking_team]["PN"].unique()
    else:
        team_players = df["PN"].unique()

    player = st.selectbox("Kicking Player", options=["All"] + sorted(team_players))

    # Type and outcome filters
    st.subheader("Kick Filters")
    kick_type = st.selectbox("Kick Type", options=["All"] + sorted(df["Type"].unique().tolist()))
    kick_outcome = st.selectbox("Kick Outcome", options=["All"] + sorted(df["Outcome"].unique().tolist()))

    # Create a mini map reference for coordinate filtering
    st.subheader("Field Position Filters")

    # Start position filters
    st.write("Start Position (x, y)")
    start_x_range = st.slider("Start Length", x_min, x_max, (x_min, x_max))
    start_y_range = st.slider("Start Width", y_min, y_max, (y_min, y_max))

    # End position filters
    st.write("End Position (x, y)")
    end_x_range = st.slider("End Length", end_x_min, end_x_max, (end_x_min, end_x_max))
    end_y_range = st.slider("End Width", end_y_min, end_y_max, (end_y_min, end_y_max))


    # Condition filters
    st.subheader("Match Condition Filters")

    # Tackle Number filter
    tackle_number_range = st.slider("Tackle Number",
                                0,
                                6,
                                (0, 6))

    # Game time filter
    game_time_range = st.slider("Game Time (seconds)",
                                game_time_min,
                                game_time_max,
                                (game_time_min, game_time_max))



    # Venue filter
    venue_values = fixtures_df["venueName"].dropna().unique()
    venue_options = ["All"] + sorted([str(v) for v in venue_values if v])
    venue = st.selectbox("Venue", options=venue_options)

    # Ground condition filter
    ground_condition_values = fixtures_df["groundConditionName"].dropna().unique()
    ground_condition_options = ["All"] + sorted([str(g) for g in ground_condition_values if g])
    ground_condition = st.selectbox("Ground Condition", options=ground_condition_options)

    # Weather filter
    weather_values = fixtures_df["weatherName"].dropna().unique()
    weather_options = ["All"] + sorted([str(w) for w in weather_values if w])
    weather = st.selectbox("Weather", options=weather_options)



# Collect all filters in a dictionary
filters = {
    "round_range": round_range,
    "kicking_team": kicking_team,
    "receiving_team": receiving_team,
    "player": player,
    "kick_type": kick_type,
    "kick_outcome": kick_outcome,
    "start_x_range": start_x_range,
    "start_y_range": start_y_range,
    "end_x_range": end_x_range,
    "end_y_range": end_y_range,
    "venue": venue,
    "ground_condition": ground_condition,
    "weather": weather,
    "game_time_range": game_time_range,
    "tackle_number_range": tackle_number_range,
}

# Apply filters
filtered_df = filter_kicks_data(df, fixtures_df, filters)

# Display kicks visualization
fig = create_kicks_visualization(filtered_df, x_min, x_max, y_min, y_max)
st.plotly_chart(fig, use_container_width=True)

# Show filtered round and match condition info
if not fixtures_df.empty:
    st.header("Match Information")

    # Filter fixtures to selected rounds and conditions
    min_round, max_round = round_range
    filtered_fixtures = fixtures_df[(fixtures_df["roundId"] >= min_round) & (fixtures_df["roundId"] <= max_round)]

    if venue != "All":
        filtered_fixtures = filtered_fixtures[filtered_fixtures["venueName"].astype(str) == venue]

    if ground_condition != "All":
        filtered_fixtures = filtered_fixtures[filtered_fixtures["groundConditionName"].astype(str) == ground_condition]

    if weather != "All":
        filtered_fixtures = filtered_fixtures[filtered_fixtures["weatherName"].astype(str) == weather]

    # Apply team filters to match information
    if kicking_team != "All":
        # A team can be either home or away
        team_fixtures = filtered_fixtures[
            (filtered_fixtures["teamName_home"] == kicking_team) |
            (filtered_fixtures["teamName_away"] == kicking_team)
            ]
        filtered_fixtures = team_fixtures

    if receiving_team != "All":
        # A team can be either home or away
        team_fixtures = filtered_fixtures[
            (filtered_fixtures["teamName_home"] == receiving_team) |
            (filtered_fixtures["teamName_away"] == receiving_team)
            ]
        filtered_fixtures = team_fixtures

    # Show applied filters
    conditions = []
    if venue != "All":
        conditions.append(f"Venue: {venue}")
    if ground_condition != "All":
        conditions.append(f"Ground: {ground_condition}")
    if weather != "All":
        conditions.append(f"Weather: {weather}")
    if kicking_team != "All":
        conditions.append(f"Team: {kicking_team}")
    if receiving_team != "All":
        conditions.append(f"Opposition: {receiving_team}")

    if conditions:
        st.write("**Applied Conditions:** " + ", ".join(conditions))

    # Get the game IDs from the filtered kicks to highlight which matches have kicks in the data
    games_with_kicks = set(filtered_df["GameId"].unique())

    # Show number of matches and kicks
    st.write(f"**Matches:** {len(filtered_fixtures)} | **Kicks:** {len(filtered_df)}")

    # Show fixtures in selected rounds
    with st.expander("View Fixtures"):
        if len(filtered_fixtures) > 0:
            for _, fixture in filtered_fixtures.iterrows():
                # Highlight games that have kicks in the dataset
                has_kicks = fixture["gameId"] in games_with_kicks
                prefix = "🏉 " if has_kicks else "   "

                st.write(
                    f"{prefix}**{fixture['roundName']}**: {fixture['teamName_home']} ({fixture['teamFinalScore_home']}) vs {fixture['teamName_away']} ({fixture['teamFinalScore_away']}) at {fixture['venueName']} | Ground: {fixture['groundConditionName']} | Weather: {fixture['weatherName']}")
        else:
            st.write("No matches match the selected criteria.")

# Show data table with filtered kicks
with st.expander("View Detailed Kick Data"):
    display_cols = ["TeamName", "OppositionName", "PN", "Type", "Outcome", "GM", "NX", "NY", "nEX", "nEY"]
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    st.dataframe(filtered_df[display_cols])