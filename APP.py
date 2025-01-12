# ...existing code...

# Create team stats DataFrame
try:
    # Calculate team statistics
    team_stats = {
        'Home Games': nfl_data.groupby('Home Team').size(),
        'Away Games': nfl_data.groupby('Away Team').size(),
        'Home Wins': nfl_data.groupby('Home Team')['Home Win'].sum(),
        'Away Wins': nfl_data.groupby('Away Team')['Away Win'].sum(),
        'Home Points': nfl_data.groupby('Home Team')['Home Score'].mean(),
        'Away Points': nfl_data.groupby('Away Team')['Away Score'].mean()
    }
    
    team_stats_df = pd.DataFrame(team_stats).fillna(0)
    
    # Initialize scaler and model if not already done
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    
    scaler = StandardScaler()
    X = team_stats_df.values
    X_scaled = scaler.fit_transform(X)
    
    # Train a simple model (you might want to use your own trained model)
    model = RandomForestClassifier(random_state=42)
    # Assuming champion_labels is a binary array indicating champion status
    champion_labels = np.zeros(len(team_stats_df))  # Replace with actual labels
    model.fit(X_scaled, champion_labels)
    
    # Sidebar predictions
    st.sidebar.header("Make Your Predictions")
    new_team = st.sidebar.selectbox("Choose a team:", team_stats_df.index.tolist())
    
    if st.sidebar.button("Predict"):
        try:
            selected_team_stats = team_stats_df.loc[new_team].values.reshape(1, -1)
            selected_team_scaled = scaler.transform(selected_team_stats)
            prediction = model.predict(selected_team_scaled)
            
            if prediction[0] == 1:
                st.sidebar.success(f"{new_team} is predicted to be a champion!")
            else:
                st.sidebar.warning(f"{new_team} is not predicted to be a champion.")
        except Exception as e:
            st.sidebar.error(f"Error making prediction: {str(e)}")
            
except Exception as e:
    st.error(f"Error processing team statistics: {str(e)}")

# ...existing code...
