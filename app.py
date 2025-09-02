# -*- coding: utf-8 -*-
import sqlite3
import random
import os
from flask import Flask, g, render_template, request, redirect, url_for

# Check if the database file exists before starting
DATABASE = "planner.db"
if not os.path.exists(DATABASE):
    print(f"ERROR: Database file '{DATABASE}' not found in the current directory.")
    print("Please make sure your database file is in the same folder as this script.")
    exit(1)

app = Flask(__name__)

# ------ Database helpers ------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ------ Activity helper ------
def get_activities(city, interests):
    if not interests:
        return []
        
    db = get_db()
    q_marks = ",".join("?" * len(interests))
    query = f"""
        SELECT id, activity_name, description, category, cost_estimate, city, image_url
        FROM activities
        WHERE city = ? AND category IN ({q_marks})
    """
    try:
        rows = db.execute(query, [city] + interests).fetchall()
        # Convert to dictionaries and return
        return [dict(row) for row in rows]
    
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return []
    # REMOVE THE EXTRA return rows LINE - it was causing the bug!

# ------ Routes ------
@app.route("/")
def index():
    db = get_db()
    activities = db.execute("SELECT id, activity_name, description, category, cost_estimate, city, image_url FROM activities").fetchall()
    
    # Convert to dictionaries and pass to template
    activities_dicts = [dict(activity) for activity in activities]
    
    return render_template("index.html", activities=activities_dicts)  # Fixed: pass activities_dicts

@app.route("/plan", methods=["POST"])
def plan():
    city = request.form.get("city", "").strip()
    try:
        days = int(request.form.get("days", 1))
    except ValueError:
        days = 1
        
    interests = request.form.getlist("interests")

    print(f"DEBUG: City={city}, Days={days}, Interests={interests}")

    if not city or not interests:
        error_msg = "Please select both a city and at least one interest."
        return render_template("plan.html", itinerary=None, city=city, error=error_msg)
    
    activities = get_activities(city, interests)
    print(f"DEBUG: Activities type: {type(activities[0]) if activities else 'No activities'}")
    print(f"DEBUG: Found {len(activities)} activities")
    
    if not activities:
        error_msg = "No activities found matching your criteria. Try different interests!"
        return render_template("plan.html", itinerary=None, city=city, error=error_msg)
    
    random.shuffle(activities)
    itinerary = {}

    # Only create as many days as we have activities for
    actual_days = min(days, len(activities))
    
    per_day = len(activities) // actual_days
    remainder = len(activities) % actual_days
    start = 0
    
    for day in range(1, actual_days + 1):
        end = start + per_day + (1 if day <= remainder else 0)
        itinerary[day] = activities[start:end]
        start = end
        
    print(f"DEBUG: Itinerary created with {len(itinerary)} days")
    return render_template("plan.html", itinerary=itinerary, city=city)

@app.route("/users")
def users():
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    users_dicts = [dict(user) for user in users]  # Convert to dictionaries
    return "<br>".join([f"{u['id']} - {u['name']} ({u['email']})" for u in users_dicts])

@app.route("/add_trip")
def add_trip():
    db = get_db()
    db.execute(
        "INSERT INTO trips (user_id, destination, start_date, end_date) VALUES (?, ?, ?, ?)",
        (1, "Rome", "2025-10-01", "2025-10-07")
    )
    db.commit()
    return "Trip added!"

@app.route("/add_activity", methods=["GET", "POST"])
def add_activity():
    if request.method == "POST":
        activity_name = request.form["activity_name"]
        description = request.form["description"]
        category = request.form["category"]
        cost_estimate = request.form["cost_estimate"]
        city = request.form["city"]
        image_url = request.form.get("image_url", "")
        
        db = get_db()
        db.execute(
            "INSERT INTO activities (activity_name, description, category, cost_estimate, city, image_url) VALUES (?, ?, ?, ?, ?, ?)",
            (activity_name, description, category, cost_estimate, city, image_url)
        )
        db.commit()

        return redirect(url_for("index"))
    return render_template("add_activity.html")

@app.route("/delete_activity", methods=["POST"])
def delete_activity():
    try:
        activity_id = request.form["activity_id"]
        db = get_db()
        db.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        db.commit()
        return redirect(url_for("index"))
    except Exception as e:
        print(f"Error deleting activity: {e}")
        return redirect(url_for("index"))

# ---------- Run ----------
if __name__ == "__main__":
    print(" * Starting Travel Planner server...")
    print(f" * Using database: {DATABASE}")
    app.run(debug=True)