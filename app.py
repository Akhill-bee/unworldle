import os
from flask import Flask, render_template, request, redirect, url_for, session

# Import logic directly from your backend file
from solver_backend import load_data, filter_candidates, best_guesses, parse_feedback_string

app = Flask(__name__)
# Secret key is required to use Flask sessions securely
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key_wordle_123")

# Load data into memory once when server starts
ALL_WORDS, FREQUENCIES = load_data("frequencies.csv")
OPENER = "crane"

@app.route("/", methods=["GET", "POST"])
def index():
    # 1. Initialize history if missing
    if "history" not in session:
        session["history"] = []

    error = None

    # 2. Handle Form Submissions
    if request.method == "POST":
        action = request.form.get("action")

        if action == "reset":
            session.clear()
            return redirect(url_for("index"))

        if action == "submit":
            guess = request.form.get("guess", "").lower()
            feedback_str = request.form.get("feedback", "bbbbb").lower()

            if len(guess) != 5 or len(feedback_str) != 5:
                error = "Guess and feedback must be 5 characters long."
            else:
                # Store new turn in history
                history = session.get("history", [])
                history.append({
                    "guess": guess,
                    "feedback": feedback_str
                })
                session["history"] = history
                session.modified = True

    # 3. Recompute remaining candidates dynamically from history
    candidates = ALL_WORDS
    history = session.get("history", [])

    for turn in history:
        color_list = parse_feedback_string(turn["feedback"])
        candidates = filter_candidates(candidates, turn["guess"], color_list)
    
    # Check game over conditions
    game_over = False
    if len(history) >= 6 or not candidates:
        game_over = True
    elif history and history[-1]["feedback"] == "ggggg":
        game_over = True

    top_options = []
    possible_words = []

    if not game_over:
        if not history:
            top_options = [OPENER]
        else:
            top_options = best_guesses(candidates, ALL_WORDS, FREQUENCIES, top_n=3)
        
        if len(candidates) <= 10:
            possible_words = sorted(candidates, key=lambda w: FREQUENCIES.get(w, 0), reverse=True)

    # 4. Render template
    return render_template(
        "index.html",
        candidates_count=len(candidates),
        possible_words=possible_words,
        top_options=top_options,
        history=history,
        game_over=game_over,
        error=error
    )

if __name__ == "__main__":
    # Use environment variable or default to False for production
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1"]
    app.run(debug=debug_mode)