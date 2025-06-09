from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash, make_response
from datetime import timedelta # Import timedelta for session duration
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import pyttsx3
import speech_recognition as sr
from database import init_db, add_user, validate_user, get_random_sentence_from_db, save_practice_result, init_sentences_db, get_practice_history

from extensions import socketio # Import socketio from extensions
# from flask_socketio import SocketIO # Removed direct import
from collaborative import collaborative_bp # Import the collaborative blueprint
from story_mode import story_mode_bp
from emotion_practice import emotion_practice_bp # Import the emotion practice blueprint
from sentence_morph import sentence_morph_bp # Import the sentence morph blueprint

from phoneme_analyzer import get_phonemes, get_phonemes_and_stress
from german_sentence import get_random_german_sentence_with_translation # Import German sentence function
from kannada_sentence import get_random_kannada_sentence_with_translation # Import Kannada sentence function
from dictionary import get_word_definition # Import dictionary function

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize SocketIO with the app context from extensions
socketio.init_app(app, cors_allowed_origins="*") # Enable CORS for WebSocket

# Register the collaborative blueprint
app.register_blueprint(collaborative_bp)

# Register the story mode blueprint
app.register_blueprint(story_mode_bp)
app.register_blueprint(emotion_practice_bp)
app.register_blueprint(sentence_morph_bp) # Register the sentence morph blueprint

# Removed manual injection, sentence_morph should import from extensions



# Initialize the user and sentence databases
init_db()
init_sentences_db()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        remember = request.form.get('remember') # Get the remember me checkbox value

        if validate_user(user, pwd):
            session['username'] = user
            if remember:
                # Make the session permanent (e.g., for 30 days)
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                # Make the session non-permanent (browser session)
                session.permanent = False
            flash("Login successful!") # Add a success flash message
            return redirect('/home')
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        confirm = request.form['confirm']
        if pwd != confirm:
            flash("Passwords do not match")
        elif add_user(user, pwd):
            flash("Registration successful. Please log in.") # Ensure flash is imported
            flash("Registration successful. Please log in.")
            return redirect('/login')
        else:
            flash("User already exists") # Ensure flash is imported
    return render_template('register.html')

@app.route('/get_definition/<word>')
def fetch_definition(word):
    """Fetches the definition of a word and returns it as JSON."""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    definition = get_word_definition(word)
    return jsonify({'definition': definition})

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect('/login')

    result = None
    if request.method == 'POST':
        if 'tts' in request.form:
            text = request.form['tts']
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        elif 'stt' in request.form:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(source, timeout=5)
                    result = recognizer.recognize_google(audio)
                except:
                    result = "Error recognizing voice"
    return render_template('home.html', result=result)

@app.route('/practice', methods=['GET', 'POST'])
def practice():
    if 'username' not in session:
        return redirect('/login')

    sentence = None
    ipa_phonemes = None # For display
    arpabet_phonemes = None # For analysis
    stresses = None # For analysis
    selected_difficulty = 'Easy'  # Default difficulty

    if request.method == 'POST':
        selected_difficulty = request.form['difficulty']
        sentence = get_random_sentence_from_db(selected_difficulty)
        if sentence:
            ipa_phonemes = get_phonemes(sentence) # Get IPA phonemes for display
            arpabet_phonemes, stresses = get_phonemes_and_stress(sentence) # Get ARPABET and stress

    return render_template(
        'practice.html',
        sentence=sentence,
        ipa_phonemes=ipa_phonemes, # Pass IPA phonemes
        arpabet_phonemes=arpabet_phonemes, # Pass ARPABET phonemes (optional for frontend)
        stresses=stresses, # Pass stresses
        selected_difficulty=selected_difficulty
    )

@app.route('/practice/german', methods=['GET', 'POST'])
def german_practice():
    if 'username' not in session:
        return redirect('/login')

    sentence = None
    translation = None
    selected_difficulty = request.args.get('difficulty', 'Easy') # Get difficulty from args for GET

    if request.method == 'POST':
        selected_difficulty = request.form.get('difficulty', 'Easy')
        sentence, translation = get_random_german_sentence_with_translation(selected_difficulty)
        print(f"AJAX Request - Selected German difficulty: {selected_difficulty}, Sentence: {sentence}, Translation: {translation}") # Debugging
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'sentence': sentence, 'translation': translation})
        # Fallback for non-AJAX POST (though unlikely with current JS)
        return render_template(
            'german_practice.html',
            sentence=sentence,
            translation=translation,
            selected_difficulty=selected_difficulty
        )

    # Handle GET request - Fetch initial sentence
    sentence, translation = get_random_german_sentence_with_translation(selected_difficulty)
    print(f"GET Request - Initial German difficulty: {selected_difficulty}, Sentence: {sentence}, Translation: {translation}") # Debugging
    return render_template(
        'german_practice.html',
        sentence=sentence,
        translation=translation,
        selected_difficulty=selected_difficulty
    )

@app.route('/practice/kannada', methods=['GET', 'POST'])
def kannada_practice():
    if 'username' not in session:
        return redirect('/login')

    sentence = None
    translation = None # Add translation variable
    selected_difficulty = 'Easy' # Default difficulty

    if request.method == 'POST':
        # Process difficulty selection if the form submits here
        selected_difficulty = request.form.get('difficulty', 'Easy')
        sentence, translation = get_random_kannada_sentence_with_translation(selected_difficulty)
        print(f"Selected Kannada difficulty: {selected_difficulty}, Sentence: {sentence}, Translation: {translation}") # Debugging

    # Handle GET request - provide a default sentence/translation or none
    # Fetch a default Easy one on GET if no sentence exists yet
    if request.method == 'GET' and not sentence:
         sentence, translation = get_random_kannada_sentence_with_translation(selected_difficulty)

    return render_template(
        'practice_kannada.html', # Point to the new Kannada template
        sentence=sentence,
        translation=translation, # Pass translation to template
        selected_difficulty=selected_difficulty
    )

@app.route('/save_score', methods=['POST'])
def save_score():
    if 'username' not in session:
        return {'error': 'Unauthorized'}, 401

    data = request.get_json()
    sentence = data.get('sentence')
    score = data.get('score')
    user_id = session['username'] # Assuming username is the identifier for now

    if sentence is not None and score is not None:
        try:
            # Ensure score is an integer
            score_int = int(score)
            save_practice_result(user_id, sentence, score_int)
            return {'message': 'Score saved successfully'}, 200
        except ValueError:
            return {'error': 'Invalid score format'}, 400
        except Exception as e:
            print(f"Error saving score: {e}") # Log the error
            return {'error': 'Failed to save score'}, 500
    return {'error': 'Missing sentence or score'}, 400

from flask import jsonify

@app.route('/summary')
def summary():
    if 'username' not in session:
        return redirect('/login')

    user_id = session['username']
    # Fetch only the first 10 history items initially
    initial_history = get_practice_history(user_id, limit=10)
    # Fetch all history for achievement calculation (consider optimizing later if needed)
    full_history = get_practice_history(user_id)

    # Calculate achievements based on full history
    perfect_scores = sum(1 for item in full_history if item[1] == 100)

    achievements = [
        {'name': 'Get 10 Perfect Scores', 'icon': '⚡', 'target': 10, 'current': perfect_scores},
        {'name': 'Get 50 Perfect Scores', 'icon': '🌟', 'target': 50, 'current': perfect_scores},
        {'name': 'Get 100 Perfect Scores', 'icon': '🏆', 'target': 100, 'current': perfect_scores},
        {'name': 'Get 250 Perfect Scores', 'icon': '🚀', 'target': 250, 'current': perfect_scores},
        {'name': 'Get 500 Perfect Scores', 'icon': '🌠', 'target': 500, 'current': perfect_scores},
        {'name': 'Get 750 Perfect Scores', 'icon': '🌌', 'target': 750, 'current': perfect_scores},
        {'name': 'Get 1000 Perfect Scores', 'icon': '👑', 'target': 1000, 'current': perfect_scores},
        {'name': 'Get 2000 Perfect Scores', 'icon': '💎', 'target': 2000, 'current': perfect_scores}
        # Add more achievements here if needed
    ]

    # Calculate progress percentage for each achievement
    for achievement in achievements:
        achievement['progress'] = min(100, (achievement['current'] / achievement['target']) * 100) if achievement['target'] > 0 else 100

    # Pass initial history and achievement data to the template
    return render_template('summary.html', history=initial_history, achievements=achievements)

@app.route('/get_history_chunk', methods=['GET'])
def get_history_chunk():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['username']
    offset = request.args.get('offset', default=0, type=int)
    limit = 10 # Fetch 10 items per request

    history_chunk = get_practice_history(user_id, limit=limit, offset=offset)

    # Convert timestamp to string for JSON serialization if needed
    history_serializable = [
        (item[0], item[1], item[2].strftime('%Y-%m-%d %H:%M:%S') if item[2] else None)
        for item in history_chunk
    ]

    return jsonify(history_serializable)

@app.route('/get_phonemes_for_text', methods=['POST'])
def get_phonemes_for_text():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    text = data.get('text')
    if text:
        try:
            phonemes = get_phonemes(text)
            return jsonify({'phonemes': phonemes}), 200
        except Exception as e:
            print(f"Error getting phonemes: {e}") # Log the error
            return jsonify({'error': 'Failed to generate phonemes'}), 500
    return jsonify({'error': 'No text provided'}), 400

@app.route('/speak_practice', methods=['POST'])
def speak_practice():
    if 'username' not in session:
        return redirect('/login')

    data = request.get_json()
    text = data.get('text')
    if text:
        engine = pyttsx3.init()
        # Add error handling for engine initialization if needed
        engine.say(text)
        engine.runAndWait()
        return {'message': 'Speech synthesized successfully'}, 200
    return {'error': 'No text provided'}, 400

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)

@socketio.on('submit_practice')
def handle_submit_practice(data):
    print('Received practice data:', data)
    # You can add further processing here, e.g., saving to DB,
    # providing real-time feedback, etc.
    # For now, we just print it.
    user_id = session.get('username')
    if user_id:
        print(f"Practice submitted by user: {user_id}")
        # Example: Save score via Socket.IO handler instead of separate route
        # try:
        #     save_practice_result(user_id, data['sentence'], int(data['score']))
        #     print("Score saved via Socket.IO")
        # except Exception as e:
        #     print(f"Error saving score via Socket.IO: {e}")
    else:
        print("Practice submitted by unknown user (session missing)")

@app.route('/analyze_stress', methods=['POST'])
def analyze_stress_route():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    spoken_text = data.get('spoken_text')
    expected_stresses = data.get('expected_stresses')

    if not spoken_text or expected_stresses is None:
        return jsonify({'error': 'Missing spoken text or expected stresses'}), 400

    try:
        # Get phonemes and stress for the spoken text
        spoken_phonemes, spoken_stresses = get_phonemes_and_stress(spoken_text)

        # Calculate stress accuracy
        correct_stresses = 0
        comparison_length = min(len(expected_stresses), len(spoken_stresses))
        for i in range(comparison_length):
            # Consider '?' or missing stress as incorrect for simplicity, adjust if needed
            if expected_stresses[i] == spoken_stresses[i] and expected_stresses[i] in ['0', '1', '2']:
                correct_stresses += 1

        # Handle potential division by zero if expected_stresses is empty
        stress_accuracy = (correct_stresses / len(expected_stresses) * 100) if expected_stresses else 0
        stress_accuracy = round(stress_accuracy)

        return jsonify({
            'spoken_stresses': spoken_stresses,
            'stress_accuracy': stress_accuracy
        }), 200

    except Exception as e:
        print(f"Error analyzing stress: {e}") # Log the error
        return jsonify({'error': 'Failed to analyze stress'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Run app
if __name__ == '__main__':
    socketio.run(app, debug=True)  # Use eventlet/gevent in prod
