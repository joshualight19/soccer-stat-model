# soccer-stat-model
A data analytics model and optimization engine built to calculate and evaluate tactical defensive synergies using eFootball player statistics.



## How to Run the Backend Server (For Frontend Integration)

1. Open your terminal in this project folder.
2. Install the required backend tools: `pip install -r requirements.txt`
3. Turn the server on: `python app.py`

### The API Endpoints (Menu)
Once the server is running, the frontend can fetch data from these local links:

* **Main Leaderboard:** `http://127.0.0.1:5000/api/defenders`
  * *Optional Parameters:* Add `?minute=X&goal_diff=Y` to simulate live match states.
* **Player Comparison:** `http://127.0.0.1:5000/api/compare?p1=PlayerName&p2=PlayerName`
  * *Note:* Ensure you include the eFootball rating in the name if applicable (e.g., `Baresi(107)`).
