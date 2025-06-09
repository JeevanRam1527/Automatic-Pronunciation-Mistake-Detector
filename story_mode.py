from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import pyttsx3
import speech_recognition as sr
import random

story_mode_bp = Blueprint('story_mode', __name__, template_folder='templates')

# List of different stories
all_stories = [

    {
        'title': 'The Sunstone Quest',
        'stages': [
            {"character": "Forest Guardian", "ai_line": "Halt, traveler! This ancient forest is protected. State your purpose.", "user_prompt": "I seek passage through this forest to reach the Sunstone."},
            {"character": "Forest Guardian", "ai_line": "Hmm, seeking the Sunstone, are you? A perilous journey. Many have tried, few have returned. Why should I let you pass?", "user_prompt": "Guardian, I need the Sunstone to save my people. My cause is just."},
            {"character": "Forest Guardian", "ai_line": "Very well. Your words carry conviction. But the path ahead is treacherous. You will encounter others. Seek out Elara, the hermit near the Whispering Falls. She may offer guidance. Proceed with caution.", "user_prompt": "Thank you, Guardian. I will seek out Elara."},
            {"character": "Elara", "ai_line": "(Sound of rustling leaves) Who goes there? Another lost soul drawn by the forest's whispers?", "user_prompt": "My name is [Player Name], the Forest Guardian sent me."},
            {"character": "Elara", "ai_line": "The Guardian sent you? He rarely trusts outsiders. You seek the Sunstone? *Sigh* A fool's errand, perhaps. But I see a flicker of determination in you. The Sunstone lies beyond the Shadow Mire, guarded by illusions. You'll need more than courage.", "user_prompt": "Elara, how can I safely navigate the Shadow Mire?"},
            {"character": "Elara", "ai_line": "The Mire preys on your fears. Trust your instincts, not your eyes. Look for the Lumina Moss; it glows faintly in the presence of truth and reveals the safe path. Take this charm; it may offer some protection. Now go, before the shadows deepen.", "user_prompt": "Thank you for your guidance and the charm, Elara. I will be careful."},
            {"character": "Mysterious Voice", "ai_line": "(In the Mire) Lost, little one? Give in to the darkness... it's so much easier...", "user_prompt": "I will not give in! I must find the Lumina Moss."},
            {"character": "Narrator", "ai_line": "(Sound of finding the path) You've navigated the Mire! The Sunstone's glow is visible ahead. But be warned, its final guardian awaits.", "user_prompt": "I am ready. Let's face the final guardian."},
            {"character": "Final Guardian", "ai_line": "So, you've made it this far. Impressive. But the Sunstone's power is not for the unworthy. Prove your strength!", "user_prompt": "I fight for my people! I will not falter!"},
            {"character": "Narrator", "ai_line": "(Sound of battle, then victory) You have proven your worth. The Sunstone is yours. Use its power wisely.", "user_prompt": "Thank you. I will."}
        ]
    },
    {
        'title': 'The Whispering Caves',
        'stages': [
            {"character": "Old Miner", "ai_line": "Psst! You there! Looking for adventure, or just lost? These caves... they whisper secrets.", "user_prompt": "Secrets? What kind of secrets?"},
            {"character": "Old Miner", "ai_line": "Secrets of forgotten treasures and ancient dangers. Legend says the Heartstone lies deep within, but the path is guarded by riddles.", "user_prompt": "I'm not afraid of riddles. Where do I start?"},
            {"character": "Old Miner", "ai_line": "Heh, brave words. Follow the echo of dripping water. The first guardian speaks in rhymes. Answer true, or be lost forever.", "user_prompt": "Thank you, old miner. I'll heed your warning."},
            {"character": "Echoing Voice", "ai_line": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?", "user_prompt": "You are a map."},
            {"character": "Echoing Voice", "ai_line": "Correct. You may pass the first trial. The next challenge tests your perception. Trust not what you see, but what you hear.", "user_prompt": "I understand. I will listen carefully."},
            {"character": "Narrator", "ai_line": "(Sound of shifting rocks and illusions) Which sound leads to the Heartstone? The rushing water, the howling wind, or the gentle chime?", "user_prompt": "The gentle chime leads the way."},
            {"character": "Narrator", "ai_line": "(Sound of a hidden passage opening) Your ears serve you well. The Heartstone is near. But its final protector values wisdom above all.", "user_prompt": "I am ready to prove my wisdom."},
            {"character": "Ancient Golem", "ai_line": "To claim the Heartstone, tell me: What has an eye, but cannot see?", "user_prompt": "A needle."},
            {"character": "Ancient Golem", "ai_line": "Hmmm. You possess wisdom. The Heartstone is yours. May it illuminate your path.", "user_prompt": "Thank you, guardian."}
        ]
    },
    
    {
        'title': 'The Crystal of Echoes',
        'stages': [
            {"character": "Temple Guard", "ai_line": "Stop! The Crystal of Echoes is not for idle curiosity. Why have you come?", "user_prompt": "I seek the crystal to uncover the truth of my past."},
            {"character": "Temple Guard", "ai_line": "Few dare to confront their past. The crystal amplifies memory—both joy and regret. Do you still wish to continue?", "user_prompt": "Yes. I need to know who I really am."},
            {"character": "Temple Guard", "ai_line": "Then step into the Hall of Whispers. Your memories will confront you there. Be strong.", "user_prompt": "I am ready. I will face them."},
            {"character": "Echo", "ai_line": "(Whispering) Do you remember me? You left me behind in your quest for glory.", "user_prompt": "I regret what I did. I seek redemption."},
            {"character": "Echo", "ai_line": "Acknowledgment is the first step. The crystal awaits beyond the Mirror Chamber. Speak truth to pass.", "user_prompt": "I will speak only truth."},
            {"character": "Crystal Guardian", "ai_line": "What truth do you seek from the Crystal of Echoes?", "user_prompt": "I seek to know who I was, and who I must become."},
            {"character": "Narrator", "ai_line": "(Sound of shimmering energy) The crystal glows, revealing forgotten faces and choices. You understand now.", "user_prompt": "I accept my past and will shape a better future."}
        ]
    },
    {
        'title': 'The Skyforge Prophecy',
        'stages': [
            {"character": "Skyforged Elder", "ai_line": "You were drawn here by the storm. It is the forge's call. Do you know why?", "user_prompt": "I believe I’m part of the prophecy."},
            {"character": "Skyforged Elder", "ai_line": "Many claim that fate, but the forge accepts only the worthy. You must awaken the Ember Spirit.", "user_prompt": "How do I awaken it?"},
            {"character": "Skyforged Elder", "ai_line": "Climb the Thunder Peak. There, shout your truth into the storm.", "user_prompt": "Then I shall climb it and speak boldly."},
            {"character": "Storm Spirit", "ai_line": "(Thunder rumbles) Who dares call me forth?", "user_prompt": "I am the one destined to wield Skyfire!"},
            {"character": "Storm Spirit", "ai_line": "Then face the flame without fear. Only the brave may command the forge.", "user_prompt": "I fear nothing. Test me."},
            {"character": "Narrator", "ai_line": "(Flames roar, then calm) The Ember Spirit accepts you. A blade begins to form from lightning and flame.", "user_prompt": "I will wield this power with honor."}
        ]
    }
    # Add more stories here as dictionaries
]

def get_current_story_part():
    """Gets the current AI line and user prompt based on the story and stage stored in the session."""
    if 'story_index' not in session or 'current_stage' not in session:
        return None # Or handle error appropriately

    story_index = session['story_index']
    stage_index = session['current_stage']
    selected_story = all_stories[story_index]

    if stage_index < len(selected_story['stages']):
        return selected_story['stages'][stage_index]
    else:
        # Story finished
        return {"ai_line": f"You have completed '{selected_story['title']}'.", "user_prompt": "End of story"}

def advance_story():
    """Advances the story to the next stage within the session."""
    if 'story_index' not in session or 'current_stage' not in session:
        return # Or handle error

    story_index = session['story_index']
    selected_story = all_stories[story_index]

    # Allow advancing to the index equal to the length to signify the end
    if session['current_stage'] < len(selected_story['stages']):
        session['current_stage'] += 1
    session.modified = True # Ensure session changes are saved

@story_mode_bp.route('/story')
def story_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Choose a random story and reset stage for a new visit/refresh
    session['story_index'] = random.randrange(len(all_stories))
    session['current_stage'] = 0
    session.modified = True

    story_part = get_current_story_part()
    if story_part:
        return render_template('story_mode.html', ai_line=story_part['ai_line'], user_prompt=story_part['user_prompt'])
    else:
        # Handle case where story part couldn't be retrieved (e.g., session issue)
        return "Error loading story.", 500

@story_mode_bp.route('/story/speak', methods=['POST'])
def story_speak():
    """Handles the AI speaking its line based on session state."""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    story_part = get_current_story_part()
    if not story_part:
        return jsonify({'status': 'error', 'message': 'Could not retrieve story part.'}), 404

    ai_line = story_part.get('ai_line')
    character = story_part.get('character', 'Narrator') # Default to Narrator if no character specified

    if ai_line:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')

            # --- Voice Selection Logic ---
            # Basic mapping - assumes at least 2 voices exist.
            # You might need to adjust indices based on your system's voices.
            # `pip install pyttsx3` and run a small script to list voices:
            # import pyttsx3
            # engine = pyttsx3.init()
            # voices = engine.getProperty('voices')
            # for i, voice in enumerate(voices):
            #     print(f"Voice {i}: ID={voice.id}, Name={voice.name}, Lang={voice.languages}")
            voice_map = {
                "Forest Guardian": voices[0].id if len(voices) > 0 else None,
                "Elara": voices[1].id if len(voices) > 1 else voices[0].id if len(voices) > 0 else None,
                "Mysterious Voice": voices[0].id if len(voices) > 0 else None, # Reuse voice 0
                "Final Guardian": voices[0].id if len(voices) > 0 else None, # Reuse voice 0
                "Old Miner": voices[0].id if len(voices) > 0 else None,
                "Echoing Voice": voices[1].id if len(voices) > 1 else voices[0].id if len(voices) > 0 else None,
                "Ancient Golem": voices[0].id if len(voices) > 0 else None,
                "Narrator": voices[0].id if len(voices) > 0 else None # Default/Narrator voice
            }

            selected_voice_id = voice_map.get(character)

            if selected_voice_id:
                engine.setProperty('voice', selected_voice_id)
            else:
                print(f"Warning: No specific voice found for character '{character}' or no voices available. Using default.")
                if voices: # Use the first available voice as a fallback if mapping fails but voices exist
                    engine.setProperty('voice', voices[0].id)

            # Optional: Adjust rate per character?
            # if character == "Old Miner":
            #     engine.setProperty('rate', 130)
            # else:
            #     engine.setProperty('rate', 160) # Default rate

            engine.say(ai_line)
            engine.runAndWait()
            engine.stop() # Ensure the engine releases resources
            return jsonify({'status': 'success', 'message': 'AI spoke.'})
        except Exception as e:
            print(f"Error in TTS: {e}")
            return jsonify({'status': 'error', 'message': 'TTS failed.'}), 500
    else:
        return jsonify({'status': 'error', 'message': 'No AI line found for this stage.'}), 404

@story_mode_bp.route('/story/listen', methods=['POST'])
def story_listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for user response...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        print("Recognizing...")
        user_text = recognizer.recognize_google(audio)
        print(f"User said: {user_text}")

        return jsonify({
            'status': 'success',
            'text': user_text,
            'next_ai_line': "Interesting... tell me more.",
            'next_user_prompt': "What happened next?"
        })

    except sr.UnknownValueError:
        print("Speech not understood.")
        return jsonify({
            'status': 'error',
            'message': 'Google Speech Recognition could not understand the audio.'
        })

    except sr.RequestError as e:
        print(f"Google API error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Could not request results from Google; {e}'
        })

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        })
