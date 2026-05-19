from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the security pass tool
import pandas as pd

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)  # Turn on the security pass for the whole app!

@app.route('/api/defenders', methods=['GET'])
def get_defenders():
    # 1. Grab the raw spreadsheet
    df = pd.read_csv('defenders_data(Sheet1).csv')

# Grab the parameters from the URL. If they aren't there, default to 0.
    match_minute = int(request.args.get('minute', 0))
    goal_difference = int(request.args.get('goal_diff', 0))

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
                (row['Buffed_Def_Aware'] * 0.35) + 
                (row['Buffed_Def_Eng'] * 0.25) + 
                (row['Buffed_Speed'] * 0.10) +
                (row['Buffed_Acceleration'] * 0.05)
                )
        
      elif row['Model'] == 'Destroyer':
        score = ((row['Buffed_Tackling'] * 0.20) + 
                (row['Buffed_Def_Aware'] * 0.35) + 
                (row['Buffed_Def_Eng'] * 0.20) + 
                (row['Buffed_Speed'] * 0.15) +
                (row['Buffed_Acceleration'] * 0.10)
                )
      
      else:
        score = ((row['Buffed_Tackling'] * 0.20) + 
                (row['Buffed_Def_Aware'] * 0.30) + 
                (row['Buffed_Def_Eng'] * 0.30) + 
                (row['Buffed_Speed'] * 0.10) +
                (row['Buffed_Acceleration'] * 0.05)
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
      (df['Buffed_Aggression'] * 0.15) +
      # (df['Buffed_Speed'] * 0.10) +
      (df['Buffed_Acceleration'] * 0.10) +
      (df['Buffed_Balance'] * 0.05) +
      (df['Buffed_Jumping'] * 0.05) +
      (df['Nomalized_Height'] * 0.25)
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


    # print("___ TOP DEFENDERS STATS___")
    # print(df[['Name', 'Shutdown_Score', 'Defending_Score', 'Overall_Score']])



    
    # 2. Chop the spreadsheet into individual plates
    defenders_list = df.to_dict(orient='records')
    
    # 3. Hand the plates out the window
    return jsonify(defenders_list)

@app.route('/api/compare', methods=['GET'])
def compare_defenders():
    # 1. Grab the raw spreadsheet
    df = pd.read_csv('defenders_data(Sheet1).csv')
    df.columns = df.columns.str.strip()
    
    # 2. Ask the web browser: "Which two players do you want to look at?"
    player1_name = request.args.get('p1')
    player2_name = request.args.get('p2')

    df['Name'] = df['Name'].str.strip()  # <-- ADD THIS LINE HERE
    
    # 3. Use Pandas to filter the spreadsheet and pull out ONLY those two names
    # This says: Find rows where the 'Name' matches player1 OR player2
    compared_df = df[df['Name'].isin([player1_name, player2_name])]
    
    # 4. Convert just those two rows into our clean JSON plate
    result = compared_df.to_dict(orient='records')
    
    # 5. Hand it out the window
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)