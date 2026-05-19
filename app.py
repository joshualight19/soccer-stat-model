from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

app.json.sort_keys = False

@app.route('/api/defenders', methods=['GET'])
def get_defenders():
    # 1. Grab the raw spreadsheet
    df = pd.read_csv('defenders_data(Sheet1).csv')
    
    # 2. Chop the spreadsheet into individual plates
    defenders_list = df.to_dict(orient='records')
    
    # 3. Hand the plates out the window
    return jsonify(defenders_list)

if __name__ == '__main__':
    app.run(debug=True)