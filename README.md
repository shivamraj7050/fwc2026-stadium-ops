# ArenaMinds 2026: GenAI Stadium Operations & Fan Experience Hub

An advanced Generative AI-enabled web application designed to streamline stadium operations, incident response, and crowd management, while elevating the fan experience for the **FIFA World Cup 2026**.

## 🌟 Key Features

* **Interactive Stadium Density Blueprint**: Live SVG-based heatmap tracking sector and gate congestion levels in real time.
* **Match Day Telemetry Simulator**: Fluctuate crowd counts and concession queue times live to test operational readiness.
* **GenAI Incident Dispatcher**: Submit raw text on-site incident descriptions, which the AI automatically categorizes, assigns severity, dispatches to the correct squad, and creates a Ground Action checklist.
* **Organizer Command Center CLI**: Run natural-language operations queries directly against database metrics.
* **Multilingual Fan Assistant Chat**: AI-powered conversational support for transit, safety guidelines, and accessibility queries.
* **Smart Transit & Accessibility Routing**: Provides custom route planning for step-free access and parking guides.
* **Eco Hub (Sustainability Tracker)**: A fan loyalty points tracker for recycling actions and public transit utilization, featuring a live leaderboard.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.13 / Flask / Flask-CORS
* **Database**: SQLite3 (persistent local database `stadium_ops.db`)
* **Frontend**: HTML5 / CSS3 (Vanilla Glassmorphism Layout) / JavaScript (ES6 Client-side logic)
* **GenAI Integration**: Google Gemini API (`gemini-1.5-flash`) via the `google-generativeai` SDK

---

## 🚀 How to Run Locally

### Prerequisites
Make sure you have **Python 3.x** installed.

### 1. Install Dependencies
Run the following command in the project directory:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a file named `.env` in the root directory:
```env
PORT=3000
# Enter your Gemini API Key here to enable GenAI intelligence features.
# If left blank, the application will run in simulated demo mode.
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Initialize the Database
Generate and seed the SQLite database:
```bash
python database.py
```

### 4. Start the Server
Run the Flask server:
```bash
python app.py
```
The application will start on **[http://localhost:3000](http://localhost:3000)**.
