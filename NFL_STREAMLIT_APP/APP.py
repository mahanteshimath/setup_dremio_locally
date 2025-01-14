import streamlit as st
import pandas as pd
from dremio_simple_query.connect import DremioConnection
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import time
import streamlit.components.v1 as components
import plotly.express as px

st.logo(
    image="https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg",
    size="large",
    link="https://www.linkedin.com/in/mahantesh-hiremath/",
    icon_image="https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg"
)

st.set_page_config(
  page_title="Dremio 2025 Football Playoff Hackathon",
  page_icon="🏈",
  layout="wide",
  initial_sidebar_state="expanded",
) 
st.title(":blue[🏈 Dremio  Football Playoff analysis 🏈]")
# Dremio connection details
username = 'admin'
password = 'password123'
dremio_endpoint = 'localhost:9047'
flight_endpoint = 'localhost:32010'

# Authenticate with Dremio REST API
login_endpoint = f"http://{dremio_endpoint}/apiv2/login"
payload = {"userName": username, "password": password}

try:
    response = requests.post(login_endpoint, json=payload)
    response.raise_for_status()
    token = response.json().get('token')
    st.toast("Successfully authenticated with Dremio", icon='🎉')
    time.sleep(.5)
    st.balloons()
except requests.exceptions.RequestException as e:
    st.error(f"Failed to authenticate with Dremio: {e}")
    st.stop()

# Establish Dremio connection
arrow_endpoint = f"grpc://{flight_endpoint}"
try:
    dremio = DremioConnection(token, arrow_endpoint)
    st.toast("Successfully connected to Dremio", icon='🎉')
    time.sleep(.5)
    st.balloons()
except Exception as e:
    st.error(f"Failed to establish connection with Dremio: {e}")
    st.stop()

# Function to execute queries
def query_data(query):
    try:
        return dremio.toPandas(query)
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return pd.DataFrame()

# Sidebar options
options = ["NFL DataModel","Data Analysis","Top Performing Players", "Team Performance", "Play Formation Analysis","2024-25 NFL Analysis"]
selected_option = st.sidebar.selectbox("Select for analysis", options)


if selected_option == "NFL DataModel":
    st.markdown("-------")
    st.subheader("This is data model for NFL")
  
    # Load the HTML content from the file
    with open("./SRC/NFL_DATAMODEL.txt", "r") as file:
        html_content = file.read()
    components.html(html_content, width=1000, height=800, scrolling=True)
    st.markdown("-------")
    st.markdown("""
    ### **Explanation of the Data Model:**

    The provided data model consists of five main tables that represent different aspects of an NFL (National Football League) dataset. Below is an explanation of each table and its columns:

    ---

    ### **1. Players Table (`players`)**

    **Purpose:**  
    This table stores basic information about NFL players.

    **Columns:**
    - `nflId`: Unique identifier for each player (Primary Key).
    - `height`: Height of the player (in feet/inches).
    - `weight`: Weight of the player (in pounds).
    - `birthDate`: The birth date of the player.
    - `collegeName`: Name of the college the player attended.
    - `position`: The player's position on the field (e.g., QB for Quarterback, T for Tackle).
    - `displayName`: The name that is displayed for the player (e.g., Tom Brady, Jason Peters).

    This table allows us to track the personal information of the players and their career roles (positions) within the NFL.

    ---

    ### **2. Tackles Table (`tackles`)**

    **Purpose:**  
    This table records the tackle statistics of players in each game.

    **Columns:**
    - `gameId`: Unique identifier for each game (Foreign Key referencing `games` table).
    - `playId`: Unique identifier for each play (Foreign Key referencing `plays` table).
    - `nflId`: The player's unique identifier (Foreign Key referencing `players` table).
    - `tackle`: Indicates whether the player made a tackle (1 = tackle made).
    - `assist`: Indicates whether the player assisted in a tackle (1 = assist made).
    - `forcedFumble`: Indicates if the player caused a fumble during the tackle.
    - `pff_missedTackle`: Indicates if the player missed the tackle according to Pro Football Focus statistics.

    This table tracks defensive performance metrics for individual players, focusing on tackles, forced fumbles, and missed tackles.

    ---

    ### **3. Tracking All Weeks Table (`tracking_all_weeks`)**

    **Purpose:**  
    This table captures player position and movement on the field during the game, based on frame data from tracking systems.

    **Columns:**
    - `gameId`: Unique identifier for each game (Foreign Key referencing `games` table).
    - `playId`: Unique identifier for each play (Foreign Key referencing `plays` table).
    - `nflId`: The player's unique identifier (Foreign Key referencing `players` table).
    - `displayName`: Player’s name.
    - `frameId`: Unique identifier for each frame or tracking data point.
    - `time`: Timestamp of the tracking data.
    - `jerseyNumber`: Player's jersey number.
    - `club`: The team to which the player belongs (e.g., BUF for Buffalo Bills).
    - `playDirection`: Direction of the play (left/right).
    - `x`, `y`: Coordinates of the player on the field during the frame.
    - `s`, `a`: Speed and acceleration of the player.
    - `dis`: Distance covered by the player.
    - `o`, `dir`: Orientation and direction the player is facing.
    - `event`: Describes the event happening at the time (e.g., "pass_arrived").
    - `tracking_week`: The specific week of the tracking data.

    This table allows detailed analysis of player movements, their positioning on the field, speed, acceleration, and other in-game metrics, making it useful for player performance evaluation and game strategy analysis.

    ---

    ### **4. Plays Table (`plays`)**

    **Purpose:**  
    This table stores detailed information about each play in a game, such as the play description, yardage, teams involved, and game clock.

    **Columns:**
    - `gameId`: Unique identifier for each game (Foreign Key referencing `games` table).
    - `playId`: Unique identifier for each play (Primary Key).
    - `ballCarrierId`: NFL ID of the player carrying the ball.
    - `ballCarrierDisplayName`: Name of the player carrying the ball.
    - `playDescription`: A textual description of the play.
    - `quarter`: The quarter in which the play occurred.
    - `down`: The down number (1st, 2nd, etc.).
    - `yardsToGo`: The number of yards to the first down.
    - `possessionTeam`: The team that has possession of the ball during the play.
    - `defensiveTeam`: The team that is defending.
    - `yardlineSide`: The side of the field where the play occurred (e.g., ATL for Atlanta).
    - `yardlineNumber`: The specific yardline number where the play began.
    - `gameClock`: The time on the game clock when the play occurred.
    - `preSnapHomeScore`, `preSnapVisitorScore`: The score of the home and visitor teams before the play.
    - `passResult`: Result of the pass (e.g., completion, incomplete).
    - `passLength`: The length of the pass.
    - `penaltyYards`: The penalty yards for the play.
    - `expectedPoints`: The expected points from the play based on analytics.
    - `playResult`: The Result of the play (e.g., touchdown, gain, loss).
    - `playNullifiedByPenalty`: Indicates if the play Result was nullified by a penalty.

    This table allows detailed analysis of play-by-play data, including player involvement, field position, penalties, and other metrics. It can be used to assess team strategies, player performance, and game outcomes.

    ---

    ### **5. Games Table (`games`)**

    **Purpose:**  
    This table stores general information about each game, including teams, scores, and game details.

    **Columns:**
    - `gameId`: Unique identifier for each game (Primary Key).
    - `season`: The season year for the game.
    - `week`: The week in the season when the game occurred.
    - `homeTeamAbbr`: The abbreviation for the home team (e.g., LA for Los Angeles Rams).
    - `visitorTeamAbbr`: The abbreviation for the visiting team (e.g., BUF for Buffalo Bills).
    - `homeFinalScore`: The final score for the home team.
    - `visitorFinalScore`: The final score for the visitor team.
    - `gameDatetime`: The date and time when the game was played.

    This table provides an overview of each game's essential information, allowing us to track game Results, scores, and which teams played in each game. It forms the basis for analyzing matchups and game outcomes.

    ---

    ### **Relationships Between Tables:**

    - **`players` → `tackles`, `tracking_all_weeks`, `plays`**: The `nflId` from the `players` table is used in the `tackles`, `tracking_all_weeks`, and `plays` tables to link player performance data to specific events.
    
    - **`games` → `tackles`, `tracking_all_weeks`, `plays`**: The `gameId` from the `games` table is used in all other tables to link data to specific games.

    - **`plays` → `tackles`, `tracking_all_weeks`**: The `playId` is used to connect data from the `plays` table to the `tackles` and `tracking_all_weeks` tables.

    ---

    ### **Conclusion:**

    This data model provides a comprehensive structure to analyze various aspects of NFL games, including player statistics (height, weight, position), game Results (scores, teams), play-by-play data, and detailed player tracking information. By joining these tables, we can gain insights into player performance, team strategies, and overall game outcomes, which can be used for sports analytics, performance evaluation, and strategy optimization.
    """)

elif selected_option == "Data Analysis":
    st.subheader("Data Analysis for NFL data from Kaggle")
    st.markdown("-------")
    st.subheader("Top 5 Players by Tackles in a Game")
    top_5_tackles_query = """
    SELECT 
        g.gameId,
        p.displayName AS PlayerName,
        COUNT(t.tackle) AS TotalTackles,
        g.homeTeamAbbr || ' vs ' || g.visitorTeamAbbr AS GameDetails,
        g.gameDatetime
    FROM 
        lake."tackles.parq" t
    JOIN 
        lake."players_fixed.parq" p ON t.nflId = p.nflId
    JOIN 
        lake."games_fixed.parq" g ON t.gameId = g.gameId
    WHERE 
        t.tackle = 1
    GROUP BY 
        g.gameId, p.displayName, g.homeTeamAbbr, g.visitorTeamAbbr, g.gameDatetime
    ORDER BY 
        TotalTackles DESC
    LIMIT 5
    """
    top_5_tackles = query_data(top_5_tackles_query)
    fig_top_5 = px.bar(
        top_5_tackles, 
        x="PlayerName", 
        y="TotalTackles", 
        color="GameDetails",
        hover_data=["gameId", "gameDatetime"],
        title="Top 5 Players by Tackles in a Game"
    )
    st.plotly_chart(fig_top_5, use_container_width=True)

    overall_game_stats_query = """
    SELECT 
    g.gameId,
    g.homeTeamAbbr AS HomeTeam,
    g.visitorTeamAbbr AS VisitorTeam,
    g.homeFinalScore AS HomeScore,
    g.visitorFinalScore AS VisitorScore,
    g.gameDatetime,
    COUNT(t.tackle) AS TotalTackles,
    COUNT(t.pff_missedTackle) AS MissedTackles,
    COUNT(DISTINCT t.nflId) AS PlayersInvolved
    FROM 
        lake."games_fixed.parq" g
    LEFT JOIN 
        lake."tackles.parq" t ON g.gameId = t.gameId
    GROUP BY 
        g.gameId, g.homeTeamAbbr, g.visitorTeamAbbr, g.homeFinalScore, g.visitorFinalScore, g.gameDatetime
    ORDER BY 
        g.gameDatetime DESC """

    overall_stats = query_data(overall_game_stats_query)
    st.markdown("-------")
    # Visualization: Game-wise Tackle and Score Summary
    st.subheader("Game-Wise Tackle and Score Summary")
    fig_game_stats = px.scatter(
        overall_stats,
        x="gameDatetime",
        y="TotalTackles",
        size="PlayersInvolved",
        color="HomeTeam",
        hover_data=["HomeScore", "VisitorScore", "VisitorTeam"],
        title="Tackles and Scores Over Time"
    )
    st.plotly_chart(fig_game_stats, use_container_width=True)

    st.markdown("-------")
        # Load game Results data
    game_Results_query = """
     SELECT
        CASE
            WHEN homeFinalScore > visitorFinalScore THEN 'Home Win'
            WHEN homeFinalScore < visitorFinalScore THEN 'Visitor Win'
            ELSE 'Tie'
        END AS "Result",
        COUNT(*) AS GameCount
    FROM lake."games_fixed.parq"
    GROUP BY "Result"
    """
    game_Results = query_data(game_Results_query)

    # Game Results Distribution
    st.subheader("Game Results Distribution")
    fig_Results = px.pie(
        game_Results,
        names="Result",
        values="GameCount",
        title="Game Results Distribution"
    )
    st.plotly_chart(fig_Results, use_container_width=True)

    st.markdown("-------")

    # Load tackle performance data
    team_tackles_query = """
    SELECT 
        g.homeTeamAbbr AS Team, 
        COUNT(t.tackle) AS TotalTackles
    FROM  lake."games_fixed.parq" g
    LEFT JOIN  lake."tackles.parq" t ON g.gameId = t.gameId
    GROUP BY g.homeTeamAbbr
    ORDER BY TotalTackles DESC;
    """
    team_tackles = query_data(team_tackles_query)

    # Tackle Performance by Team
    st.subheader("Tackle Performance by Team")
    fig_team_tackles = px.bar(
        team_tackles,
        x="Team",
        y="TotalTackles",
        color="Team",
        title="Total Tackles by Team"
    )
    st.plotly_chart(fig_team_tackles, use_container_width=True)
    st.markdown("-------")

    # Load player performance data
    player_performance_query = """
    SELECT 
        p.displayName AS PlayerName,
        SUM(t.tackle) AS Tackles,
        SUM(t.pff_missedTackle) AS MissedTackles
    FROM lake."tackles.parq" t
    JOIN lake."players.parq"  p ON t.nflId = p.nflId
    GROUP BY p.displayName
    ORDER BY Tackles DESC;
    """
    player_performance = query_data(player_performance_query)

    # Player Performance Heatmap
    st.subheader("Player Performance Heatmap")
    fig_heatmap = px.density_heatmap(
        player_performance,
        x="Tackles",
        y="MissedTackles",
        hover_name="PlayerName",
        title="Player Tackles vs. Missed Tackles Heatmap"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("-------")

        # Load game trends data
    game_trends_query = """
    SELECT 
        gameDatetime,
        COUNT(t.tackle) AS TotalTackles,
        AVG(g.homeFinalScore) AS AvgHomeScore,
        AVG(g.visitorFinalScore) AS AvgVisitorScore
    FROM lake."games_fixed.parq" g
    LEFT JOIN lake."tackles.parq" t ON g.gameId = t.gameId
    GROUP BY gameDatetime
    ORDER BY gameDatetime;
    """
    game_trends = query_data(game_trends_query)

    # Game Trends Over Time
    st.subheader("Game Trends Over Time")
    fig_trends = px.line(
        game_trends,
        x="gameDatetime",
        y=["TotalTackles", "AvgHomeScore", "AvgVisitorScore"],
        labels={"value": "Counts", "variable": "Metric"},
        title="Trends in Tackles and Scores Over Time"
    )
    st.plotly_chart(fig_trends, use_container_width=True)

    st.markdown("-------")

    # Load tackles by position data
    position_tackles_query = """
        SELECT 
        p."position",
        COUNT(t.tackle) AS TotalTackles
    FROM lake."tackles.parq" t
    JOIN lake."players.parq"  p ON t.nflId = p.nflId
    GROUP BY p."position"
    ORDER BY TotalTackles DESC
    """
    position_tackles = query_data(position_tackles_query)

    # Tackles by Position
    st.subheader("Tackles by Position")
    fig_position_tackles = px.bar(
        position_tackles,
        x="position",
        y="TotalTackles",
        title="Tackles by Player Position",
        color="position"
    )
    st.plotly_chart(fig_position_tackles, use_container_width=True)

    st.markdown("-------")

    st.subheader("National, American and Overall  Champions")
    team_names = {
    'TEN': 'Tennessee Titans',
    'NO': 'New Orleans Saints',
    'IND': 'Indianapolis Colts',
    'WAS': 'Washington Commanders',
    'CLE': 'Cleveland Browns',
    'JAX': 'Jacksonville Jaguars',
    'PIT': 'Pittsburgh Steelers',
    'LAC': 'Los Angeles Chargers',
    'DAL': 'Dallas Cowboys',
    'BAL': 'Baltimore Ravens',
    'NYG': 'New York Giants',
    'SF': 'San Francisco 49ers',
    'LA': 'Los Angeles Rams',
    'CIN': 'Cincinnati Bengals',
    'MIN': 'Minnesota Vikings',
    'GB': 'Green Bay Packers',
    'DET': 'Detroit Lions',
    'BUF': 'Buffalo Bills',
    'PHI': 'Philadelphia Eagles',
    'TB': 'Tampa Bay Buccaneers',
    'MIA': 'Miami Dolphins',
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons',
    'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears',
    'KC': 'Kansas City Chiefs',
    'LV': 'Las Vegas Raiders',
    'NE': 'New England Patriots',
    'HOU': 'Houston Texans',
    'NYJ': 'New York Jets',
    'SEA': 'Seattle Seahawks',
    'DEN': 'Denver Broncos'
    }


        # Queries to find champions
    nfc_query = """
    SELECT homeTeamAbbr, COUNT(*) AS wins
    FROM lake."games_fixed.parq" 
    WHERE homeTeamAbbr IN ('NO', 'SF', 'LA', 'MIN', 'GB', 'DET', 'PHI', 'TB', 'ARI', 'ATL', 'CAR', 'CHI', 'SEA')
    AND homeFinalScore > visitorFinalScore
    GROUP BY homeTeamAbbr
    ORDER BY wins DESC
    LIMIT 1
    """

    afc_query = """
    SELECT homeTeamAbbr, COUNT(*) AS wins
    FROM lake."games_fixed.parq" 
    WHERE homeTeamAbbr IN ('TEN', 'IND', 'WAS', 'CLE', 'JAX', 'PIT', 'LAC', 'DAL', 'BAL', 'NYG', 'CIN', 'BUF', 'MIA', 'KC', 'LV', 'NE', 'HOU', 'NYJ', 'DEN')
    AND homeFinalScore > visitorFinalScore
    GROUP BY homeTeamAbbr
    ORDER BY wins DESC
    LIMIT 1
    """

    overall_query = """
    SELECT homeTeamAbbr, COUNT(*) AS wins
    FROM lake."games_fixed.parq" 
    WHERE homeFinalScore > visitorFinalScore
    GROUP BY homeTeamAbbr
    ORDER BY wins DESC
    LIMIT 1
    """

    # Fetch Results
    nfc_champion = query_data(nfc_query)
    afc_champion = query_data(afc_query)
    overall_champion = query_data(overall_query)




        
    # Query Results handling
    if not nfc_champion.empty:
        nfc_team = nfc_champion.iloc[0]['homeTeamAbbr']
        nfc_wins = nfc_champion.iloc[0]['wins']
        nfc_team_full_name = team_names.get(nfc_team, nfc_team)
        st.write(f"**National Champion Pick (NFC) 🏆**: {nfc_team_full_name} with {nfc_wins} wins")

    if not afc_champion.empty:
        afc_team = afc_champion.iloc[0]['homeTeamAbbr']
        afc_wins = afc_champion.iloc[0]['wins']
        afc_team_full_name = team_names.get(afc_team, afc_team)
        st.write(f"**American Champion Pick (AFC) 🏆**: {afc_team_full_name} with {afc_wins} wins")

    if not overall_champion.empty:
        overall_team = overall_champion.iloc[0]['homeTeamAbbr']
        overall_wins = overall_champion.iloc[0]['wins']
        overall_team_full_name = team_names.get(overall_team, overall_team)
        st.write(f"**Overall Champion Pick 🌍**: {overall_team_full_name} with {overall_wins} wins")

 

elif selected_option == "Top Performing Players":
    st.subheader("Top Performing Players")
    query = """
        SELECT player_name, nested_0."position" AS "position", total_tackles, total_assists
    FROM (
    SELECT 
        p.displayName AS player_name,
        p."position",
        SUM(t.tackle) AS total_tackles,
        SUM(t.assist) AS total_assists
    FROM 
        lake."players_fixed.parq" p
    JOIN 
        lake."tackles.parq" t
    ON 
        p.nflId = t.nflId
    GROUP BY 
        p.displayName, p."position"
    ORDER BY 
        total_tackles DESC, total_assists DESC
    LIMIT 10
    ) nested_0
    ORDER BY total_tackles ASC

    """
    player_data = query_data(query)
    if not player_data.empty:
        st.dataframe(player_data)

        # Bar plot
        fig, ax = plt.subplots()
        sns.barplot(data=player_data, x="total_tackles", y="player_name", ax=ax, palette="Blues_d")
        ax.set_title("Top Players by Tackles")
        ax.set_xlabel("Total Tackles")
        ax.set_ylabel("Player Name")
        st.pyplot(fig)


# Team Performance Visualization
elif selected_option == "Team Performance":
    st.subheader("Team Performance")
    query = """
    SELECT 
        possessionTeam AS team,
        SUM(playResult) AS total_yards,
        SUM(expectedPoints) AS total_expected_points
    FROM lake."plays.parq"
    GROUP BY possessionTeam
    ORDER BY total_yards DESC
    LIMIT 10
    """
    team_data = query_data(query)
    if not team_data.empty:
        st.dataframe(team_data)

        # Combined bar and line plot
        fig, ax1 = plt.subplots()
        sns.barplot(data=team_data, x="team", y="total_yards", ax=ax1, color="lightblue", label="Total Yards")
        ax2 = ax1.twinx()
        sns.lineplot(data=team_data, x="team", y="total_expected_points", ax=ax2, color="red", label="Total Expected Points")

        ax1.set_title("Team Performance")
        ax1.set_xlabel("Team")
        ax1.set_ylabel("Total Yards")
        ax2.set_ylabel("Total Expected Points")
        st.pyplot(fig)

# Play Formation Analysis Visualization
elif selected_option == "Play Formation Analysis":
    st.subheader("Play Formation Analysis")
    query = """
    SELECT 
        offenseFormation,
        COUNT(*) AS play_count,
        AVG(playResult) AS avg_play_Result,
        AVG(expectedPoints) AS avg_expected_points
    FROM lake."plays.parq"
    GROUP BY offenseFormation
    ORDER BY avg_play_Result DESC
    LIMIT 10
    """
    formation_data = query_data(query)
    if not formation_data.empty:
        st.dataframe(formation_data)

        # Bar chart
        fig, ax = plt.subplots()
        sns.barplot(data=formation_data, x="offenseFormation", y="avg_play_Result", ax=ax, palette="viridis")
        ax.set_title("Play Formation Efficiency")
        ax.set_xlabel("Offense Formation")
        ax.set_ylabel("Average Play Result")
        st.pyplot(fig)
elif selected_option == "2024-25 NFL Analysis":
    st.subheader("2024-25 NFL Analysis and Champion Prediction")
    st.subheader("Data taken from https://fixturedownload.com/Results/nfl-2024")
    query = """select * from lake."NF_DATA_2024.csv" """
    nfl_data = query_data(query)
    
    if not nfl_data.empty:
        # Display the raw data
        st.dataframe(nfl_data)
        
        