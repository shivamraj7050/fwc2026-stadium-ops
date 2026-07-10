import os
import re
import json
import random
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

import database

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Initialize Gemini Client
ai_enabled = False
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key.strip():
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        ai_enabled = True
        print("Gemini API initialized successfully.")
    else:
        print("No GEMINI_API_KEY found. Running in Simulated AI Mock mode.")
except Exception as e:
    print(f"Failed to initialize Gemini Client: {e}. Running in Simulated AI Mock mode.")

# Ensure database is initialized
database.initialize_database()

# Helper: Clean JSON responses from Gemini
def extract_json(text):
    try:
        # Strip markdown code blocks if present
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text) or re.search(r'```\s*([\s\S]*?)\s*```', text)
        cleaned = json_match.group(1) if json_match else text
        return json.loads(cleaned.strip())
    except Exception as e:
        print(f"Failed to parse AI JSON: {e}. Raw text: {text}")
        # Repair regex attempt
        try:
            title_match = re.search(r'"title"\s*:\s*"([^"]+)"', text)
            cat_match = re.search(r'"category"\s*:\s*"([^"]+)"', text)
            sev_match = re.search(r'"severity"\s*:\s*"([^"]+)"', text)
            team_match = re.search(r'"assigned_team"\s*:\s*"([^"]+)"', text)
            prot_match = re.search(r'"ai_protocol"\s*:\s*"([\s\S]+?)"', text)
            
            if title_match and cat_match and sev_match:
                return {
                    "title": title_match.group(1),
                    "category": cat_match.group(1),
                    "severity": sev_match.group(1),
                    "assigned_team": team_match.group(1) if team_match else "Steward Team",
                    "ai_protocol": prot_match.group(1).replace('\\n', '\n') if prot_match else "1. Standby at location.\n2. Assist spectators."
                }
        except Exception as repair_err:
            print(f"Regex repair failed too: {repair_err}")
        raise ValueError("AI response was not valid JSON")

# ----------------------------------------------------
# SIMULATED AI FALLBACKS
# ----------------------------------------------------
def mock_incident_ai(description, location):
    desc = description.lower()
    category = 'Other'
    severity = 'Medium'
    title = 'Reported incident'
    assigned_team = 'Steward Team'
    ai_protocol = ''

    if any(x in desc for x in ['slip', 'spill', 'water', 'leak', 'trash']):
        category = 'Facilities'
        title = 'Liquid spill or facilities issue'
        assigned_team = 'Facilities Support'
        severity = 'High' if ('dangerous' in desc or 'hurt' in desc) else 'Low'
        ai_protocol = f"1. Dispatch maintenance team to {location} with cleanup equipment.\n2. Secure the area with warning signs to prevent fan slips.\n3. Inform supervisors once the cleaning is completed."
    elif any(x in desc for x in ['medical', 'collapse', 'hurt', 'bleeding', 'heart', 'faint']):
        category = 'Medical'
        title = 'Spectator medical emergency'
        assigned_team = 'Medical Response'
        severity = 'High'
        if 'chest' in desc or 'unconscious' in desc:
            severity = 'Critical'
        ai_protocol = f"1. Deploy nearest first-aid crew with a defibrillator to {location}.\n2. Clear a pathway for emergency stretchers.\n3. Notify stadium medical command and wait for secondary triage."
    elif any(x in desc for x in ['fight', 'theft', 'stolen', 'intrusion', 'weapon', 'smoke', 'flare']):
        category = 'Security'
        title = 'Security alert / Fan alteration'
        assigned_team = 'Security Team'
        severity = 'High'
        ai_protocol = f"1. Send crowd security units to {location} to diffuse situation.\n2. Monitor CCTV footage of the sector.\n3. Escort non-compliant individuals out of the gates."
    elif any(x in desc for x in ['crowd', 'gate', 'congest', 'stuck', 'bottleneck']):
        category = 'Crowd Control'
        title = 'Concourse queue bottleneck'
        assigned_team = 'Crowd Marshals'
        severity = 'Critical' if 'crush' in desc else 'Medium'
        ai_protocol = f"1. Place barrier queue lines at {location}.\n2. Direct fans to adjacent underutilized entry routes.\n3. Announce updates through the public address speaker."
    elif any(x in desc for x in ['wheelchair', 'disabled', 'ramp', 'elevator', 'mobility']):
        category = 'Facilities'
        title = 'Accessibility assistance required'
        assigned_team = 'Volunteer Support'
        severity = 'Medium'
        ai_protocol = f"1. Direct accessibility volunteers to locate the fan at {location}.\n2. Guide them to nearest step-free routes or elevators.\n3. Supply portable ramp if access is blocked."
    else:
        ai_protocol = f"1. Dispatch steward to {location} to assess details.\n2. Update the operations desk with live status.\n3. Resolve when conditions return to normal."

    if len(description) < 35:
        title = description
    else:
        title = description[:35] + "..."

    return {
        "title": title,
        "category": category,
        "severity": severity,
        "assigned_team": assigned_team,
        "ai_protocol": ai_protocol
    }

def mock_chat_ai(message):
    msg = message.lower()
    if any(x in msg for x in ['hello', 'hi', 'welcome']):
        return "👋 Hello! Welcome to the FIFA World Cup 2026 Stadium Operations Assistant. How can I help you today? (English/Español/Français)"
    elif any(x in msg for x in ['recycle', 'sustainability', 'points', 'green']):
        return "🌱 Help us make this the greenest World Cup! Recycle your bottles and beverage cups at our Green Stations to earn **50 points**! Check the Eco Hub tab to see the top eco-fans."
    elif any(x in msg for x in ['gate 1', 'metro', 'transport', 'bus', 'train']):
        return "🚇 **Transport Guide:** Metro Line 1 brings you directly to Gate 1 (Main Entrance). Bus shuttles run every 5 minutes from the central station to Gates 2 and 3. Transit is free with your match ticket!"
    elif any(x in msg for x in ['wheelchair', 'accessible', 'disabled', 'mobility']):
        return "♿️ **Accessibility:** Gate 4 is the dedicated VIP and Step-Free entry. Elevators are situated near Sector A and D lobbies. Wheelchair-accessible toilets are fully signposted on all levels."
    elif any(x in msg for x in ['food', 'tacos', 'beer', 'eat', 'concession']):
        return "🍔 **Concessions:** We have great food stands open! *El Tri Tacos* is in Sector B (current line: 25 mins), *Stadium Bites* in Sector A (15 mins), and *Maple Leaf Grill* in Sector C (only 8 mins!). Grab a bite!"
    else:
        return "⚽️ **FIFA World Cup 2026 Support:** Thanks for your query. Stadium doors open 3 hours before kickoff. Please remember only small clear bags are allowed. Feel free to ask about transport, accessibility, and recycling!"

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Dashboard aggregations
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        zones = database.get_all("SELECT * FROM crowd_zones")
        concessions = database.get_all("SELECT * FROM concessions")
        incidents = database.get_all("SELECT * FROM incidents WHERE status != 'Resolved'")
        sustainability = database.get_one("SELECT SUM(points) as total_points FROM sustainability")
        
        return jsonify({
            "success": True,
            "zones": zones,
            "concessions": concessions,
            "incidents": incidents,
            "total_sustainability_points": sustainability.get("total_points") or 0
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Get crowd zones
@app.route('/api/zones', methods=['GET'])
def get_zones():
    try:
        zones = database.get_all("SELECT * FROM crowd_zones")
        return jsonify({"success": True, "zones": zones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Simulate crowd metrics (Match Day simulation step)
@app.route('/api/zones/simulate', methods=['POST'])
def simulate_zones():
    try:
        zones = database.get_all("SELECT * FROM crowd_zones")
        for zone in zones:
            delta = random.randint(-350, 800)
            new_occupancy = max(100, min(zone["capacity"], zone["occupancy"] + delta))
            ratio = new_occupancy / zone["capacity"]
            
            status = 'Normal'
            if ratio > 0.9:
                status = 'Congested'
            elif ratio > 0.75:
                status = 'Warning'
                
            database.run_query(
                "UPDATE crowd_zones SET occupancy = ?, status = ? WHERE id = ?",
                (new_occupancy, status, zone["id"])
            )
            
        concessions = database.get_all("SELECT * FROM concessions")
        for c in concessions:
            new_time = max(3, c["queue_time"] + random.randint(-2, 5))
            database.run_query(
                "UPDATE concessions SET queue_time = ? WHERE id = ?",
                (new_time, c["id"])
            )
            
        return jsonify({"success": True, "message": "Simulation parameters updated."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Get concessions
@app.route('/api/concessions', methods=['GET'])
def get_concessions():
    try:
        concessions = database.get_all("SELECT * FROM concessions")
        return jsonify({"success": True, "concessions": concessions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Get incidents
@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    try:
        incidents = database.get_all("SELECT * FROM incidents ORDER BY id DESC")
        return jsonify({"success": True, "incidents": incidents})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Update incident status
@app.route('/api/incidents/update', methods=['POST'])
def update_incident():
    data = request.json
    inc_id = data.get("id")
    status = data.get("status")
    
    if not inc_id or not status:
        return jsonify({"success": False, "error": "Incident ID and status are required"}), 400
        
    try:
        database.run_query("UPDATE incidents SET status = ? WHERE id = ?", (status, inc_id))
        return jsonify({"success": True, "message": "Incident updated successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Report incident (GenAI Dispatcher)
@app.route('/api/incidents/report', methods=['POST'])
def report_incident():
    data = request.json
    description = data.get("description")
    location = data.get("location")
    
    if not description or not location:
        return jsonify({"success": False, "error": "Incident description and location are required"}), 400
        
    try:
        ai_response = None
        if ai_enabled:
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""You are a professional incident dispatcher system for the FIFA World Cup 2026 stadium command center.
Analyze the following stadium incident report:
Description: "{description}"
Location: "{location}"

You MUST respond with a raw JSON object and nothing else. Do NOT include markdown code blocks.
Response JSON Schema:
{{
  "title": "A short, professional title summarizing the problem (max 50 chars)",
  "category": "Safety" | "Security" | "Medical" | "Facilities" | "Crowd Control" | "Other",
  "severity": "Low" | "Medium" | "High" | "Critical",
  "assigned_team": "Facilities Support" | "Security Team" | "Medical Response" | "Crowd Marshals" | "Steward Team",
  "ai_protocol": "A step-by-step numbered protocol (in Markdown format) detailing exactly what response staff and volunteers must do on-site."
}}
Analyze this now."""
                response = model.generate_content(prompt)
                ai_response = extract_json(response.text)
            except Exception as gemini_err:
                print(f"Gemini error during incident processing, falling back to mock: {gemini_err}")
                ai_response = mock_incident_ai(description, location)
        else:
            ai_response = mock_incident_ai(description, location)
            
        # Save to database
        inc_id = database.run_query(
            """INSERT INTO incidents (title, description, location, category, severity, status, assigned_team, ai_protocol)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ai_response["title"],
                description,
                location,
                ai_response["category"],
                ai_response["severity"],
                "Open",
                ai_response["assigned_team"],
                ai_response["ai_protocol"]
            )
        )
        
        return jsonify({
            "success": True,
            "incident": {
                "id": inc_id,
                "title": ai_response["title"],
                "description": description,
                "location": location,
                "category": ai_response["category"],
                "severity": ai_response["severity"],
                "status": "Open",
                "assigned_team": ai_response["assigned_team"],
                "ai_protocol": ai_response["ai_protocol"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Log sustainability activity
@app.route('/api/sustainability', methods=['POST'])
def log_sustainability():
    data = request.json
    username = data.get("username")
    action_type = data.get("action_type")
    
    if not username or not action_type:
        return jsonify({"success": False, "error": "Username and action type are required"}), 400
        
    points = 20
    if 'Bottle' in action_type or 'Can' in action_type:
        points = 50
    elif 'Metro' in action_type or 'Train' in action_type:
        points = 100
    elif 'Cup' in action_type or 'Plate' in action_type:
        points = 30
        
    try:
        database.run_query(
            "INSERT INTO sustainability (username, action_type, points) VALUES (?, ?, ?)",
            (username, action_type, points)
        )
        return jsonify({
            "success": True, 
            "message": f"Eco-action logged successfully! You earned {points} points.",
            "points": points
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Get sustainability leaderboard
@app.route('/api/sustainability/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        leaderboard = database.get_all("""
            SELECT username, SUM(points) as total_points, COUNT(*) as action_count
            FROM sustainability
            GROUP BY username
            ORDER BY total_points DESC
            LIMIT 10
        """)
        return jsonify({"success": True, "leaderboard": leaderboard})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Fan Chatbot Assistant
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json
    message = data.get("message")
    
    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400
        
    try:
        if ai_enabled:
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""You are "ArenaBot", the official AI Fan Assistant for the FIFA World Cup 2026 host stadium.
Your goal is to answer fan questions about the stadium, transit, gates, accessibility, sustainability points, and amenities.
Be extremely helpful, friendly, and match the multilingual requests. Keep your answer under 100 words and use emojis for readability.

Relevant Real-time Stadium Info:
- Metro Line 1 is the fastest train to the Main Entrance (Gate 1).
- Free Wi-Fi is available stadium-wide: "FWC2026-FREE" (no password needed).
- Fans earn 50 points on the Eco Leaderboard for recycling plastic bottles.
- Gate 4 is the dedicated step-free entrance for accessibility ticket holders.
- Stadium doors open 3 hours prior to kickoff. Bags must be clear plastic (under 12" x 6" x 12").

User Query: "{message}"
"""
                response = model.generate_content(prompt)
                return jsonify({"success": True, "response": response.text.strip()})
            except Exception as gemini_err:
                print(f"Gemini error during chat, using fallback: {gemini_err}")
                return jsonify({"success": True, "response": mock_chat_ai(message)})
        else:
            return jsonify({"success": True, "response": mock_chat_ai(message)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Organizers Command Center (Command Line)
@app.route('/api/ai/command', methods=['POST'])
def ai_command():
    data = request.json
    command = data.get("command")
    
    if not command:
        return jsonify({"success": False, "error": "Command is required"}), 400
        
    try:
        # Gather DB context
        zones = database.get_all("SELECT name, capacity, occupancy, status FROM crowd_zones")
        concessions = database.get_all("SELECT name, queue_time, status, inventory_status FROM concessions")
        active_incidents = database.get_all("SELECT title, location, category, severity, status, assigned_team FROM incidents WHERE status != 'Resolved'")
        
        zones_str = "\n".join([f"- {z['name']}: {z['occupancy']}/{z['capacity']} fans ({z['status']} congestion)" for z in zones])
        concessions_str = "\n".join([f"- {c['name']}: {c['queue_time']}m queue, Status: {c['status']}, Inventory: {c['inventory_status']}" for c in concessions])
        incidents_str = "\n".join([f"- [{i['severity']}] {i['title']} at {i['location']} (Category: {i['category']}, Status: {i['status']}, Assigned: {i['assigned_team']})" for i in active_incidents])
        
        context_str = f"""
STADIUM STATUS REPORT:
1. Crowd Zones:
{zones_str}

2. Concessions & Amenities:
{concessions_str}

3. Active Incidents:
{incidents_str}
"""
        if ai_enabled:
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""You are the ArenaMinds Operations Director AI for the FIFA World Cup 2026.
You are assisting stadium organizers in the Command Center.
Here is the current real-time database state:
{context_str}

Process the organizer's command or query: "{command}"
Support them with operational summaries, quick statistics, drafting broadcast messages, or offering crowd routing recommendations based on the data.
Format your output in clean Markdown. Keep it direct and professional."""
                response = model.generate_content(prompt)
                return jsonify({"success": True, "response": response.text.strip()})
            except Exception as gemini_err:
                print(f"Gemini error during command execution, using fallback: {gemini_err}")
                return jsonify({"success": True, "response": mock_command_fallback(command, zones, concessions, active_incidents)})
        else:
            return jsonify({"success": True, "response": mock_command_fallback(command, zones, concessions, active_incidents)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def mock_command_fallback(command, zones, concessions, active_incidents):
    cmd = command.lower()
    response = "### 📋 Command Center Assistant (Demo Mode)\n\n"
    
    if any(x in cmd for x in ['incident', 'issue', 'problem']):
        response += "**Active Incidents Summary:**\n"
        if not active_incidents:
            response += "- No active incidents reported at this time.\n"
        else:
            for i in active_incidents:
                response += f"- **[{i['severity']}]** {i['title']} at *{i['location']}* (Team: {i['assigned_team']})\n"
    elif any(x in cmd for x in ['congest', 'crowd', 'capacity', 'zone']):
        response += "**Crowd Densities Report:**\n"
        congested = [z for z in zones if z["status"] != 'Normal']
        if not congested:
            response += "- All sectors are operating within normal limits.\n"
        else:
            for z in congested:
                response += f"- **{z['name']}** is at **{z['status']}** with {z['occupancy']}/{z['capacity']} fans.\n"
    elif any(x in cmd for x in ['broadcast', 'announcement', 'draft']):
        response += "**Draft Broadcast Announcement:**\n\n"
        response += "> *\"Attention World Cup Fans in Sector B: Concession queues are currently busy. For faster service, we recommend visiting Maple Leaf Grill in Sector C where wait times are under 10 minutes. Thank you for your cooperation!\"*\n"
    else:
        response += f"Operational Command parsed your query: *\"{command}\"*.\n\n"
        response += "**Live Highlights:**\n"
        response += f"- Active Incidents: {len(active_incidents)}\n"
        busy_concessions = [c["name"] for c in concessions if c["queue_time"] > 20]
        response += f"- High Wait Concessions: {', '.join(busy_concessions) if busy_concessions else 'None'}\n"
        congested_zones = [z["name"] for z in zones if z["status"] == 'Congested']
        response += f"- Congested Zones: {', '.join(congested_zones) if congested_zones else 'None'}\n"
        
    return response

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 3000))
    print(f"ArenaMinds 2026 Flask Server starting on http://localhost:{port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
