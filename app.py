from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the security pass tool
import pandas as pd

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)  # Turn on the security pass for the whole app!

def calculate_catenaccio_scores(df,match_minute,goal_difference):
    if match_minute > 45 and goal_difference > 0:
      fortress_active_buff = 0.05
    else:
      fortress_active_buff = 0.00
      
    # Force Python to read BOTH skills and base stats as actual numbers instead of text.
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


    # Calculate the Average Tracking Speed and Positioning of defenders with unique models
    def calculate_shutdown(row):
      if row['Model'] == 'Build Up':
        score = ((row['Buffed_Tackling'] * 0.25) + 
                (row['Buffed_Def_Aware'] * 0.30) + 
                (row['Buffed_Def_Eng'] * 0.20) + 
                (row['Buffed_Speed'] * 0.20) +
                (row['Buffed_Acceleration'] * 0.05)
                )
        
      elif row['Model'] == 'Destroyer':
        score = ((row['Buffed_Tackling'] * 0.20) + 
                (row['Buffed_Def_Aware'] * 0.30) + 
                (row['Buffed_Def_Eng'] * 0.20) + 
                (row['Buffed_Speed'] * 0.20) +
                (row['Buffed_Acceleration'] * 0.10)
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

    df = df.sort_values(by = 'Shutdown_Score', ascending = False)


    # Defending Score Calculation
    df['Defending_Score'] = (
      (df['Buffed_Tackling'] * 0.10) +
      (df['Buffed_Def_Aware'] * 0.15) +
      (df['Physical Contact'] * 0.15) +
      (df['Buffed_Aggression'] * 0.10) +
      (df['Buffed_Speed'] * 0.10) +
      (df['Buffed_Acceleration'] * 0.10) +
      (df['Buffed_Balance'] * 0.05) +
      (df['Buffed_Jumping'] * 0.10) +
      (df['Nomalized_Height'] * 0.15)
    )


    df['Defending_Score'] = df['Defending_Score'].round(2)


    if match_minute > 45 and goal_difference > 0:
      fortress_active_buff = 0.05
      print(f"Match State: {match_minute}' Min | Winning. Fortress Skill is ACTIVE.")

    else:
      fortress_active_buff = 0.00
      if match_minute < 45:
        print(f"Match State: {match_minute}' Min | 1st Half. Fortress Skill is INACTIVE.")
      else:
        print(f"Match State: {match_minute}' Min | Not Winning. Fortress Skill is INACTIVE.")

    df['Overall_Score'] = (df['Shutdown_Score'] + df['Defending_Score']) / 2
    df['Overall_Score'] = df['Overall_Score'].round(2)

    # --- FINAL LEADERBOARD RANKING ---
    # Sort by the Overall Score to see who the ultimate complete defenders are
    df = df.sort_values(by='Overall_Score', ascending=False)

    # Clean up the leaderboard numbering (1, 2, 3...)
    df = df.reset_index(drop=True)
    df.index = df.index + 1

    return df


@app.route('/api/defenders', methods=['GET'])
def get_defenders():
    # 1. Grab the raw spreadsheet
    df = pd.read_csv('defenders_data(Sheet1).csv')

    # Grab the parameters from the URL. If they aren't there, default to 0.
    match_minute = int(request.args.get('minute', 0))
    goal_difference = int(request.args.get('goal_diff', 0))


    # 2. Send it to the prep station!
    df = calculate_catenaccio_scores(df, match_minute, goal_difference)
    
    # 3. Sort by overall score for the leaderboard
    df = df.sort_values(by='Overall_Score', ascending=False)
    
    return jsonify(df.to_dict(orient='records'))
    

@app.route('/api/compare', methods=['GET'])
def compare_defenders():
    df = pd.read_csv('defenders_data(Sheet1).csv')
    df['Name'] = df['Name'].str.strip()
    
    # 1. Get the match state AND the two player names from the URL
    minute = int(request.args.get('minute', 0))
    diff = int(request.args.get('goal_diff', 0))
    p1 = request.args.get('p1')
    p2 = request.args.get('p2')
    
    # 2. Send it to the exact same prep station!
    df = calculate_catenaccio_scores(df, minute, diff)
    
    # 3. Filter down to ONLY those two calculated players
    compared_df = df[df['Name'].isin([p1, p2])]
    
    # ... (Your code above stays the same: loading, prep station, filtering) ...

    # Convert the filtered rows into a list of records
    players_found = compared_df.to_dict(orient='records')
    
    # Let's organize the plate explicitly: Player 1 on top, Player 2 under it
    structured_result = {
        "player_1": players_found[0] if len(players_found) > 0 else None,
        "player_2": players_found[1] if len(players_found) > 1 else None
    }
    
    # Hand the structured package out the window
    return jsonify(structured_result)

if __name__ == '__main__':
    app.run(debug=True)