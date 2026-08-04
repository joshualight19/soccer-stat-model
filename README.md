# 🛡️ The Catenaccio Engine

An advanced analytical engine designed for eFootball to calculate true defender ratings, evaluate tactical compatibility, and visualize head-to-head defensive metrics. 

Instead of relying on base in-game overalls, this engine applies situational coefficients to calculate how players actually perform under specific match conditions.

**🔗 [View the Live App Here] https://soccer-stat-model-mrtb58vq9zerjnvemjd7se.streamlit.app/

---

## ⚙️ Core Features

* **Dynamic Match State Engine:** Adjust the match minute and goal difference to automatically trigger situational player buffs (e.g., activating "Fortress" when leading after the 45th minute or applying "Shadow Hunt" speed boosts).
* **True Rating Calculator:** Computes a unique **Shutdown Score** and **Defending Score** by weighting attributes (Tackling, Defensive Awareness, Physical Contact, etc.) differently depending on the player's intrinsic model (Build Up, Destroyer, etc.).
* **Tactical Compatibility Algorithm:** Evaluates defensive pairings using a custom 60/40 weighted system comparing Playstyle Synergy against Aerial/Physical Balance to grade the duo's effectiveness.
* **1v1 Visualizer:** Generates interactive Plotly radar charts to instantly compare the underlying stats of any two defenders.
* **Data Export:** Allows users to download the fully processed CSV with the recalculated ratings for their own offline analysis.

---

## 🛠️ Tech Stack

* **Language:** Python
* **Frontend/Deployment:** Streamlit
* **Data Manipulation:** Pandas
* **Data Visualization:** Plotly (Graph Objects)

---

## 🚀 How to Run Locally

If you want to run the engine on your own machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/joshualight19/soccer-stat-model.git](https://github.com/joshualight19/soccer-stat-model.git)
   cd soccer-stat-model