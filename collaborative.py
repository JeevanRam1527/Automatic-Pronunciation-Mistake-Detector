from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_socketio import emit, join_room, leave_room
from extensions import socketio # Import socketio from extensions
from database import get_random_sentence_from_db # Use absolute import
import uuid # For generating unique session IDs
import difflib # For calculating text similarity
import random # For shuffling sentences if needed

collaborative_bp = Blueprint('collaborative', __name__)

# Store active collaborative sessions
# Structure: { 'session_id': {
#     'participants': {sid: {'username': username, 'score': 0, 'submitted_this_round': False}},
#     'sentences': ['sentence1', 'sentence2', ...],
#     'total_sentences': N,
#     'current_sentence_index': 0,
#     'status': 'waiting'/'active'/'finished'
#     }
# }
active_sessions = {}


def calculate_similarity(text1, text2):
    """Calculates the similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


@collaborative_bp.route('/collaborative/create', methods=['POST'])
def create_session():
    """Creates a new collaborative session."""
    if 'username' not in session:
        return redirect(url_for('login'))

    session_id = str(uuid.uuid4())[:8] # Generate a short unique ID
    num_sentences = int(request.form.get('num_sentences', 5)) # Get number of sentences from form, default 5
    difficulty = 'Easy' # TODO: Allow difficulty selection

    sentences = []
    try:
        # Fetch multiple unique sentences
        # Note: This assumes get_random_sentence_from_db can be called repeatedly
        # A more robust approach might involve fetching multiple sentences in one DB call if possible
        all_sentences_of_difficulty = [] # Placeholder if we need to fetch all and sample
        # Example: Fetching one by one, ensuring uniqueness (can be inefficient)
        fetched_sentences = set()
        while len(sentences) < num_sentences:
            sentence = get_random_sentence_from_db(difficulty)
            if sentence and sentence not in fetched_sentences:
                sentences.append(sentence)
                fetched_sentences.add(sentence)
            elif not sentence:
                 # Handle case where not enough unique sentences are available
                 flash(f'Could only fetch {len(sentences)} unique sentences for difficulty {difficulty}.', 'warning')
                 if not sentences: # If none could be fetched at all
                     flash('Failed to fetch any sentences for the session.', 'error')
                     return redirect(url_for('home'))
                 break # Proceed with the sentences fetched so far
        num_sentences = len(sentences) # Update actual number of sentences

    except Exception as e:
        print(f"Error fetching sentences: {e}")
        flash('An error occurred while fetching sentences.', 'error')
        return redirect(url_for('home'))

    active_sessions[session_id] = {
        'participants': {},
        'sentences': sentences,
        'total_sentences': num_sentences,
        'current_sentence_index': 0,
        'status': 'waiting' # Initial status
    }
    print(f"Created collaborative session: {session_id} with {num_sentences} sentences.")
    # Redirect user to the join page/route for this new room
    return redirect(url_for('collaborative.join_session_page', session_id=session_id))

@collaborative_bp.route('/collaborative/join', methods=['POST'])
def join_session():
    """Handles joining an existing session via ID from home page."""
    if 'username' not in session:
        return redirect(url_for('login'))

    session_id = request.form.get('session_id')
    if not session_id or session_id not in active_sessions:
        flash('Invalid or non-existent Session ID.', 'error')
        return redirect(url_for('home'))

    # Redirect to the session page
    return redirect(url_for('collaborative.join_session_page', session_id=session_id))


@collaborative_bp.route('/collaborative/session/<session_id>')
def join_session_page(session_id):
    """Renders the page for a specific collaborative session."""
    if 'username' not in session:
        return redirect(url_for('login'))

    if session_id not in active_sessions:
        flash('Collaborative session not found.', 'error')
        return redirect(url_for('home'))

    session_data = active_sessions[session_id]
    username = session['username']

    # Pass the first sentence and total count
    current_sentence = session_data['sentences'][0] if session_data['sentences'] else "No sentence available."
    total_sentences = session_data['total_sentences']

    return render_template('collaborative.html',
                           session_id=session_id,
                           sentence=current_sentence,
                           username=username,
                           status=session_data['status'],
                           current_index=1, # Start with 1-based index for display
                           total_sentences=total_sentences)

# --- SocketIO Event Handlers ---

@socketio.on('join_collaborative')
def handle_join_collaborative(data):
    """Handles a user joining a collaborative room."""
    session_id = data.get('session_id')
    username = session.get('username')
    sid = request.sid

    if not username:
        print(f"User without session tried to join room {session_id}")
        emit('join_error', {'message': 'Authentication required.'}, room=sid)
        return

    if session_id not in active_sessions:
        print(f"User {username} tried to join non-existent room {session_id}")
        emit('join_error', {'message': 'Session not found.'}, room=sid)
        return

    join_room(session_id)
    # Store username, initial score, and submission status for the current round
    active_sessions[session_id]['participants'][sid] = {'username': username, 'score': 0, 'submitted_this_round': False}
    print(f"User {username} (SID: {sid}) joined room {session_id}")

    # Update participant list for everyone
    participants_data = [{'username': p['username'], 'score': p['score']} for p in active_sessions[session_id]['participants'].values()]
    emit('update_participants', {'participants': participants_data}, room=session_id)

    # Send current sentence details to the new user
    current_index = active_sessions[session_id]['current_sentence_index']
    current_sentence = active_sessions[session_id]['sentences'][current_index]
    total_sentences = active_sessions[session_id]['total_sentences']
    emit('session_details', {
        'sentence': current_sentence,
        'status': active_sessions[session_id]['status'],
        'current_index': current_index + 1, # 1-based for display
        'total_sentences': total_sentences
    }, room=sid)

    # TODO: Add logic to start the session if enough players join?
    # For now, assume it starts immediately or manually
    # If session was waiting, maybe change status?
    # if active_sessions[session_id]['status'] == 'waiting' and len(active_sessions[session_id]['participants']) > 1:
    #     active_sessions[session_id]['status'] = 'active'
    #     emit('session_status_update', {'status': 'active'}, room=session_id)

@socketio.on('leave_collaborative')
def handle_leave_collaborative(data):
    """Handles a user leaving a collaborative room."""
    session_id = data.get('session_id')
    username = session.get('username')
    sid = request.sid

    if not username or session_id not in active_sessions or sid not in active_sessions[session_id]['participants']:
        print(f"Invalid leave request: room={session_id}, user={username}, sid={sid}")
        return # Ignore invalid requests

    leave_room(session_id)
    participant_left = active_sessions[session_id]['participants'].pop(sid, None)

    if participant_left:
        print(f"User {username} (SID: {sid}) left room {session_id}")

        # Update participant list for remaining users
        participants_data = [{'username': p['username'], 'score': p['score']} for p in active_sessions[session_id]['participants'].values()]
        emit('update_participants', {'participants': participants_data}, room=session_id)

        # Check if the round should advance now that someone left
        check_all_submitted_and_advance(session_id)

        # Optional: Clean up room if empty
        if not active_sessions[session_id]['participants']:
            print(f"Room {session_id} is empty, removing.")
            del active_sessions[session_id]
    else:
        print(f"Attempted to remove non-existent participant {sid} from room {session_id}")


@socketio.on('submit_speech')
def handle_submit_speech(data):
    """Handles submission of recognized speech from a client."""
    session_id = data.get('session_id')
    recognized_text = data.get('text')
    username = session.get('username')
    sid = request.sid

    if not username or session_id not in active_sessions or sid not in active_sessions[session_id]['participants']:
        print(f"Invalid speech submission: room={session_id}, user={username}, sid={sid}")
        emit('speech_error', {'message': 'Invalid submission.'}, room=sid)
        return

    if not recognized_text:
        emit('speech_error', {'message': 'No text received.'}, room=sid)
        return

    session_data = active_sessions[session_id]
    current_index = session_data['current_sentence_index']

    # Prevent double submission for the same sentence
    if session_data['participants'][sid]['submitted_this_round']:
        print(f"User {username} tried to submit again for sentence {current_index+1}")
        emit('speech_error', {'message': 'You have already submitted for this sentence.'}, room=sid)
        return

    target_sentence = session_data['sentences'][current_index]
    similarity = calculate_similarity(target_sentence, recognized_text)
    score_this_round = round(similarity * 100)

    # Update the user's score (cumulative) and mark as submitted for this round
    session_data['participants'][sid]['score'] += score_this_round # Accumulate score
    session_data['participants'][sid]['submitted_this_round'] = True

    print(f"User {username} in room {session_id} submitted for sentence {current_index+1}: '{recognized_text}', Round Score: {score_this_round}, Total Score: {session_data['participants'][sid]['score']}")

    # Broadcast the updated participant list with the new total score
    participants_data = [{'username': p['username'], 'score': p['score']} for p in session_data['participants'].values()]
    emit('update_participants', {'participants': participants_data}, room=session_id)

    # Optionally send confirmation back to the sender
    emit('speech_result', {'recognized_text': recognized_text, 'score': score_this_round, 'total_score': session_data['participants'][sid]['score']}, room=sid)

    # Check if all participants have submitted for this round
    check_all_submitted_and_advance(session_id)


@socketio.on('disconnect') # Handle browser close/disconnect
def handle_disconnect_collaborative():
    sid = request.sid
    # Find which room the disconnected user was in
    session_to_leave = None
    username_left = None
    for session_id, data in active_sessions.items():
        if sid in data['participants']:
            session_to_leave = session_id
            username_left = data['participants'][sid]['username']
            # Remove the participant
            participant_left = data['participants'].pop(sid, None)
            session_to_leave = session_id # Keep track of the session ID
            break

    if session_to_leave and username_left:
        print(f"User {username_left} (SID: {sid}) disconnected from room {session_to_leave}")
        # Ensure the session still exists before proceeding
        if session_to_leave in active_sessions:
            # Update participant list for remaining users
            participants_data = [{'username': p['username'], 'score': p['score']} for p in active_sessions[session_to_leave]['participants'].values()]
            emit('update_participants', {'participants': participants_data}, room=session_to_leave)

            # Check if the round should advance now that someone left
            check_all_submitted_and_advance(session_to_leave)

            # Optional: Clean up room if empty
            if not active_sessions[session_to_leave]['participants']:
                print(f"Room {session_to_leave} is empty after disconnect, removing.")
                del active_sessions[session_to_leave]
        else:
            print(f"Session {session_to_leave} was already removed.")

# Remove the old score submission logic
# @socketio.on('submit_collaborative_score') ... (deleted)

def check_all_submitted_and_advance(session_id):
    """Checks if all active participants have submitted for the current round and advances if so."""
    if session_id not in active_sessions:
        return # Session already ended or removed

    session_data = active_sessions[session_id]
    participants = session_data['participants']

    if not participants: # No participants left
        print(f"Session {session_id} has no participants, cannot advance.")
        # Optionally clean up the session here if desired
        # del active_sessions[session_id]
        return

    all_submitted = all(p['submitted_this_round'] for p in participants.values())

    if all_submitted:
        print(f"All participants in {session_id} submitted for sentence {session_data['current_sentence_index'] + 1}.")
        session_data['current_sentence_index'] += 1

        # Reset submission status for the next round
        for sid in participants:
            participants[sid]['submitted_this_round'] = False

        if session_data['current_sentence_index'] < session_data['total_sentences']:
            # Advance to the next sentence
            next_index = session_data['current_sentence_index']
            next_sentence = session_data['sentences'][next_index]
            print(f"Advancing {session_id} to sentence {next_index + 1}: {next_sentence}")
            emit('next_sentence', {
                'sentence': next_sentence,
                'current_index': next_index + 1, # 1-based for display
                'total_sentences': session_data['total_sentences']
            }, room=session_id)
            # Update session status if it was waiting
            if session_data['status'] == 'waiting':
                 session_data['status'] = 'active'
                 emit('session_status_update', {'status': 'active'}, room=session_id)

        else:
            # End of session
            print(f"Session {session_id} finished.")
            session_data['status'] = 'finished'
            # Get final scores
            final_scores = [{'username': p['username'], 'score': p['score']} for p in participants.values()]
            emit('session_end', {'final_scores': final_scores}, room=session_id)
            # Optionally remove the session after a delay or keep it for review
            # Consider adding a cleanup mechanism for finished sessions
            # For now, just mark as finished
    else:
        print(f"Waiting for more submissions in {session_id} for sentence {session_data['current_sentence_index'] + 1}.")