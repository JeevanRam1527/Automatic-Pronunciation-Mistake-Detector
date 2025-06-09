from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit
from extensions import socketio # Import the shared socketio instance
import random
import time
from threading import Thread, Event
import difflib # For calculating similarity

# --- Sample Sentences ---
SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "Peter Piper picked a peck of pickled peppers.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
    "The rain in Spain stays mainly in the plain.",
    "A big black bear sat on a big black rug.",
    "I scream, you scream, we all scream for ice cream.",
    "Fred fed Ted bread and Ted fed Fred bread.",
    "Six slippery snails slid slowly seaward.",
    "Red lorry, yellow lorry.",
    "Betty Botter bought some butter.",
    "He threw three free throws.",
    "How can a clam cram in a clean cream can?",
    "Crisp crusts crackle and crunch.",
    "Brisk brave brigadiers brandish broad bright blades.",
    "Fuzzy Wuzzy was a bear. Fuzzy Wuzzy had no hair. Fuzzy Wuzzy wasn’t very fuzzy, was he?",
    "A proper copper coffee pot.",
    "Four fine fresh fish for you.",
    "Truly rural.",
    "Greek grapes, Greek grapes, Greek grapes.",
    "Rolling red wagons."
]

# --- Blueprint Definition ---
sentence_morph_bp = Blueprint('sentence_morph', __name__, url_prefix='/sentence_morph')

# --- SocketIO is imported from extensions ---

# --- Sentence Morphing Logic ---
def get_initial_sentence():
    return random.choice(SENTENCES)

def morph_sentence(sentence):
    words = sentence.split()
    if len(words) > 1:
        index_to_change = random.randint(0, len(words) - 1)
        random_sentence_words = random.choice(SENTENCES).split()
        words[index_to_change] = random.choice(random_sentence_words)
        return " ".join(words)
    return sentence

# --- WebSocket Integration ---
# session_id: {'stop_event': Event, 'shown_sentences': [], 'user_attempts': [], 'current_sentence': str}
sessions = {}

def morphing_thread(session_id, start_sentence):
    session_data = sessions.get(session_id)
    if not session_data:
        return # Session ended prematurely

    sentence = start_sentence
    session_data['current_sentence'] = sentence
    session_data['shown_sentences'].append(sentence)
    session_data['user_attempts'].append(None) # Placeholder for the initial sentence attempt

    while not session_data['stop_event'].is_set():
        time.sleep(5) # Wait before morphing
        if session_data['stop_event'].is_set(): # Check again after sleep
            break
        sentence = morph_sentence(sentence)
        session_data['current_sentence'] = sentence
        session_data['shown_sentences'].append(sentence)
        session_data['user_attempts'].append(None) # Add placeholder for the new sentence attempt
        socketio.emit('new_sentence', {'sentence': sentence}, to=session_id, namespace='/sentence_morph')

@socketio.on('start_morphing', namespace='/sentence_morph')
def handle_start_morphing(data=None):
    session_id = request.sid
    start_sentence = get_initial_sentence()

    stop_event = Event()
    sessions[session_id] = {
        'stop_event': stop_event,
        'shown_sentences': [],
        'user_attempts': [],
        'current_sentence': start_sentence # Store initial sentence
    }

    thread = Thread(target=morphing_thread, args=(session_id, start_sentence))
    thread.daemon = True
    thread.start()
    emit('started', {'message': 'Morphing started', 'initial_sentence': start_sentence})

@socketio.on('stop_morphing', namespace='/sentence_morph')
@socketio.on('submit_attempt', namespace='/sentence_morph')
def handle_submit_attempt(data):
    session_id = request.sid
    attempt_text = data.get('text')
    session_data = sessions.get(session_id)

    if session_data and not session_data['stop_event'].is_set() and attempt_text is not None:
        # Store the attempt for the *last shown* sentence
        if session_data['shown_sentences']:
            last_sentence_index = len(session_data['shown_sentences']) - 1
            # Only record if no attempt exists for this index yet
            if last_sentence_index < len(session_data['user_attempts']) and session_data['user_attempts'][last_sentence_index] is None:
                 session_data['user_attempts'][last_sentence_index] = attempt_text
                 print(f"Attempt for '{session_data['shown_sentences'][last_sentence_index]}': {attempt_text}")
            else:
                print(f"Attempt received too late or duplicate for index {last_sentence_index}")


def calculate_score_and_feedback(shown_sentences, user_attempts):
    """Calculates score and generates feedback based on attempts."""
    total_score = 0
    max_score = 0
    feedback_details = []
    suggestions = []

    # Ensure lists are of the same length, padding attempts if necessary
    # This handles cases where the challenge stops before the last attempt is made
    attempt_len = len(user_attempts)
    sentence_len = len(shown_sentences)
    if attempt_len < sentence_len:
        user_attempts.extend([None] * (sentence_len - attempt_len))

    for i, sentence in enumerate(shown_sentences):
        attempt = user_attempts[i]
        max_score += 1 # Each sentence is worth 1 point
        similarity = 0
        if attempt:
            similarity = difflib.SequenceMatcher(None, sentence.lower(), attempt.lower()).ratio()
            total_score += similarity # Score is the similarity ratio
            feedback_details.append(f"Sentence {i+1}: '{sentence}' vs '{attempt}' (Similarity: {similarity:.2f})")
            if similarity < 0.7:
                suggestions.append(f"Practice saying '{sentence}' more clearly.")
        else:
            feedback_details.append(f"Sentence {i+1}: '{sentence}' - No attempt recorded.")
            suggestions.append(f"Try to attempt saying '{sentence}'.")

    overall_percentage = (total_score / max_score * 100) if max_score > 0 else 0
    overall_feedback = f"Overall Score: {total_score:.2f}/{max_score} ({overall_percentage:.1f}%)"

    if overall_percentage > 80:
        overall_feedback += " Excellent work!"
    elif overall_percentage > 60:
        overall_feedback += " Good effort, keep practicing!"
    else:
        overall_feedback += " Needs improvement. Focus on the suggestions."

    # Limit suggestions to avoid overwhelming the user
    if len(suggestions) > 3:
        suggestions = random.sample(suggestions, 3)

    return {
        'score': f"{total_score:.2f}/{max_score}",
        'percentage': f"{overall_percentage:.1f}%",
        'feedback': overall_feedback,
        'details': feedback_details,
        'suggestions': suggestions
    }

@socketio.on('stop_morphing', namespace='/sentence_morph')
def handle_stop_morphing():
    session_id = request.sid
    session_data = sessions.get(session_id)
    if session_data:
        session_data['stop_event'].set() # Signal the thread to stop

        # Calculate results
        results = calculate_score_and_feedback(
            session_data['shown_sentences'],
            session_data['user_attempts']
        )

        # Clean up session
        sessions.pop(session_id, None)

        # Emit results
        emit('stopped', {
            'message': 'Morphing stopped. Results calculated.',
            'results': results
        })
    else:
        # Handle case where session might already be stopped or invalid
        emit('stopped', {'message': 'Morphing already stopped or session invalid.'})

# --- Routes ---
@sentence_morph_bp.route('/')
def index():
    initial_sentence = get_initial_sentence()
    return render_template('sentence_morph.html', initial_sentence=initial_sentence)

@sentence_morph_bp.route('/get_morphed_sentence', methods=['GET', 'POST'])
def get_morphed_sentence_route():
    if request.method == 'POST':
        data = request.get_json()
        current_sentence = data.get('current_sentence', get_initial_sentence())
    else:
        current_sentence = get_initial_sentence()

    morphed = morph_sentence(current_sentence)
    return jsonify({'morphed_sentence': morphed})
