from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import random

# Placeholder for actual emotion analysis model/library
def analyze_voice_emotion(audio_data):
    """Placeholder function for emotion analysis."""
    # In a real application, you would integrate a machine learning model here.
    # For now, let's simulate some basic logic.
    # This is highly simplified and not accurate.
    print("Analyzing emotion (placeholder)...")
    # Simulate detecting one of the target emotions randomly
    detected_emotions = ['happy', 'sad', 'angry', 'neutral'] # Example possible outputs
    detected_emotion = random.choice(detected_emotions)
    print(f"Simulated detected emotion: {detected_emotion}")
    return detected_emotion

emotion_practice_bp = Blueprint('emotion_practice', __name__, template_folder='templates')

# Sample sentences and emotions
EMOTION_PRACTICE_DATA = {
    'happy': [
        "I just got wonderful news!",
        "This is the best day ever!",
        "I'm so excited about the party!"
    ],
    'sad': [
        "I feel so down today.",
        "That movie ending was heartbreaking.",
        "I miss my friends."
    ],
    'angry': [
        "I can't believe you did that!",
        "This traffic is making me furious!",
        "Get out of my way!"
    ]
}

@emotion_practice_bp.route('/emotion_practice')
def emotion_practice_page():
    """Render the emotion practice page with a random sentence and emotion."""
    if 'username' not in session:
        return redirect(url_for('login'))

    # Select a random emotion and a random sentence for that emotion
    target_emotion = random.choice(list(EMOTION_PRACTICE_DATA.keys()))
    sentence = random.choice(EMOTION_PRACTICE_DATA[target_emotion])

    return render_template('emotion_practice.html', sentence=sentence, target_emotion=target_emotion)

@emotion_practice_bp.route('/analyze_emotion', methods=['POST'])
def analyze_emotion():
    """Receive audio data and return emotion analysis feedback."""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio_data']
    target_emotion = request.form.get('target_emotion')

    if not target_emotion:
        return jsonify({'error': 'Target emotion not specified'}), 400

    try:
        # In a real app, save the file temporarily if needed by the analysis library
        # audio_file.save('temp_recording.wav')
        audio_data = audio_file.read() # Read bytes for analysis

        # --- Emotion Analysis --- (Using placeholder)
        detected_emotion = analyze_voice_emotion(audio_data)

        # --- Feedback Logic --- (Simple comparison)
        is_correct = (detected_emotion == target_emotion)
        if is_correct:
            feedback = f"Correct! You sounded {target_emotion}."
        else:
            feedback = f"Not quite. You sounded more {detected_emotion}, but we were looking for {target_emotion}. Try again!"

        return jsonify({'feedback': feedback, 'detected_emotion': detected_emotion, 'correct': is_correct})

    except Exception as e:
        print(f"Error during emotion analysis: {e}")
        return jsonify({'error': 'Failed to analyze audio'}), 500