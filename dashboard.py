import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Set up the web page settings
st.set_page_config(page_title="The Catenaccio Engine", layout="wide")

# 2. Add the UI Headers
st.title("🛡️ The Catenaccio Engine")
st.subheader("Center-Back True Rating Leaderboard")

# 3. Load the raw spreadsheet
@st.cache_data 
def load_data():
    return pd.read_csv('defenders_data(Sheet1).csv')

raw_df = load_data()

# 4. Build the Sidebar Controls
st.sidebar.header("⚙️ Match State Settings")

# NEW: Add the position selector
selected_position = st.sidebar.selectbox("Select Position", ['CB', 'FB'])

match_minute = st.sidebar.slider("Match Minute", min_value=0, max_value=90, value=0)
goal_difference = st.sidebar.number_input("Goal Difference", min_value=-5, max_value=5, value=0)
st.sidebar.caption("Adjust these to see 'Fortress' and other conditional skills activate.")

# 5. The Engine (Your exact math, FIXED)
def calculate_catenaccio_scores(df, match_minute, goal_difference):
    if match_minute > 45 and goal_difference > 0:
      fortress_active_buff = 0.05
    else:
      fortress_active_buff = 0.00
      
    cols_to_clean = [
        'Aerial Forte', 'Shadow Hunt', 'Fortress', 'Long Reach Tackle',
        'Height', 'Jumping', 'Acceleration', 'Balance', 
        'Aggression', 'Defensive Awareness', 'Tackling', 'Physical Contact'
    ]

    for col in cols_to_clean:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Buffers
    df['Nomalized_Height'] = (df['Height'] / 200) * 99
    df['Buffed_Jumping'] = df['Jumping'] * (1.0 + (df['Aerial Forte'] * 0.10))
    df['Buffed_Acceleration'] = df['Acceleration'] * (1.0 + (df['Shadow Hunt'] * 0.10))
    df['Buffed_Balance'] = df['Balance'] * (1.0 + (df['Shadow Hunt'] * 0.10))
    df['Buffed_Aggression'] = df['Aggression'] * (1.0 + (df['Fortress'] * fortress_active_buff))
    df['Buffed_Def_Aware'] = df['Defensive Awareness'] * (1.0 + (df['Fortress'] * fortress_active_buff))
    df['Buffed_Def_Eng'] = df['Defensive Engagement'] * (1.0 + (df['Fortress'] * fortress_active_buff))
    df['Buffed_Speed'] = df['Speed'] * (1.0 + df['Shadow Hunt'] * 0.10)
    df['Buffed_Tackling'] = df['Tackling'] * (1.0 + (df['Long Reach Tackle'] * 0.10) + (df['Fortress'] * fortress_active_buff)) 

    # Shutdown Score (Using your custom tweaks)
    def calculate_shutdown(row):
      if row['Model'] == 'Build Up':
        score = ((row['Buffed_Tackling'] * 0.25) + 
                (row['Buffed_Def_Aware'] * 0.30) + 
                (row['Buffed_Def_Eng'] * 0.30) + 
                (row['Buffed_Speed'] * 0.10) +
                (row['Buffed_Acceleration'] * 0.05)
                )
      elif row['Model'] == 'Destroyer':
        score = ((row['Buffed_Tackling'] * 0.20) + 
                (row['Buffed_Def_Aware'] * 0.35) + 
                (row['Buffed_Def_Eng'] * 0.20) + 
                (row['Buffed_Speed'] * 0.20) +
                (row['Buffed_Acceleration'] * 0.05)
                )
      else:
        score = ((row['Buffed_Tackling'] * 0.20) + 
                (row['Buffed_Def_Aware'] * 0.30) + 
                (row['Buffed_Def_Eng'] * 0.20) + 
                (row['Buffed_Speed'] * 0.20) +
                (row['Buffed_Acceleration'] * 0.10)
                )
      return score

    df['Shutdown_Score'] = df.apply(calculate_shutdown, axis=1)
    df['Shutdown_Score'] = df['Shutdown_Score'].round(2)

    # Defending Score (The REAL Koller Tax from Day 6)
    df['Defending_Score'] = (
      (df['Buffed_Tackling'] * 0.15) +
      (df['Buffed_Def_Aware'] * 0.15) +
      (df['Buffed_Def_Eng'] * 0.10) +          
      (df['Nomalized_Height'] * 0.20) +  
      (df['Physical Contact'] * 0.15) +  
      (df['Buffed_Acceleration'] * 0.10) +
      (df['Buffed_Speed'] * 0.05) +      
      (df['Buffed_Jumping'] * 0.05) +    
      (df['Buffed_Aggression'] * 0.05)
    )

    df['Defending_Score'] = df['Defending_Score'].round(2)

    df['Overall_Score'] = (df['Shutdown_Score'] + df['Defending_Score']) / 2
    df['Overall_Score'] = df['Overall_Score'].round(2)

    # --- FINAL LEADERBOARD RANKING ---
    df = df.sort_values(by='Overall_Score', ascending=False)
    df = df.reset_index(drop=True)
    df.index = df.index + 1

    # --- COLUMN REORGANIZATION ---
    all_columns = df.columns.tolist()
    front_columns = ['Name', 'Overall_Score', 'Shutdown_Score', 'Defending_Score', 'Model']
    
    for col in front_columns:
        if col in all_columns:
            all_columns.remove(col)
            
    df = df[front_columns + all_columns]

    return df

# 6. Run the math using the sidebar inputs
# NEW: Filter the dataframe BEFORE we run the math
filtered_df = raw_df[raw_df['Position'] == selected_position]

# NEW: Pass the 'filtered_df' into your engine instead of the raw_df
calculated_df = calculate_catenaccio_scores(filtered_df.copy(), match_minute, goal_difference)
# 7. Display the final ranked leaderboard on the screen
st.dataframe(calculated_df)

# ==========================================
# 8. THE 1V1 PLAYER COMPARISON VISUALIZER
# ==========================================
st.markdown("---") # Draws a clean visual divider line
st.subheader("⚔️ Head-to-Head Comparison")

# Create two columns for the dropdown menus
col1, col2 = st.columns(2)

# Get a list of all player names for the dropdowns
player_names = calculated_df['Name'].tolist()

with col1:
    player1 = st.selectbox("Select Player 1", player_names, index=0)
with col2:
    player2 = st.selectbox("Select Player 2", player_names, index=1 if len(player_names) > 1 else 0)

# Filter the dataframe to just get the two selected players
p1_data = calculated_df[calculated_df['Name'] == player1].iloc[0]
p2_data = calculated_df[calculated_df['Name'] == player2].iloc[0]

# Define the exact stats we want to plot on the radar chart
categories = [
    'Overall_Score', 'Shutdown_Score', 'Defending_Score', 
    'Physical Contact', 'Speed', 'Acceleration', 'Jumping', 'Nomalized_Height'
]

# Extract the values for those categories
p1_values = [p1_data[cat] for cat in categories]
p2_values = [p2_data[cat] for cat in categories]

# We have to close the radar loop by appending the first value to the end of the list
categories.append(categories[0])
p1_values.append(p1_values[0])
p2_values.append(p2_values[0])

# Draw the Plotly Radar Chart
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
      r=p1_values,
      theta=categories,
      fill='toself',
      name=player1,
      line_color='cyan'
))

fig.add_trace(go.Scatterpolar(
      r=p2_values,
      theta=categories,
      fill='toself',
      name=player2,
      line_color='orange'
))

fig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, max(max(p1_values), max(p2_values)) + 5] # Dynamically scale the chart
    )),
  showlegend=True,
  paper_bgcolor="rgba(0,0,0,0)", # Makes the background transparent
  plot_bgcolor="rgba(0,0,0,0)"
)

# Render the chart on the Streamlit dashboard
st.plotly_chart(fig, use_container_width=True)