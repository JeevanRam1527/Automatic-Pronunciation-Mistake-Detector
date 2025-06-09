import random

kannada_sentences_with_translations = {
    'Easy': [
        ("ನಮಸ್ಕಾರ", "Hello"),
        ("ನಾನು ಒಬ್ಬ ವಿದ್ಯಾರ್ಥಿ", "I am a student"),
        ("ಇದು ಒಂದು ಸೇಬು", "This is an apple"),
        ("ಅವನು ಪುಸ್ತಕ ಓದುತ್ತಾನೆ", "He reads a book"),
        ("ಅವಳು ನೀರು ಕುಡಿಯುತ್ತಾಳೆ", "She drinks water"),
        ("ನಾವು ಕನ್ನಡ ಕಲಿಯುತ್ತಿದ್ದೇವೆ", "We are learning Kannada"),
        ("ಆಕಾಶ ನೀಲಿಯಾಗಿದೆ", "The sky is blue"),
        ("ಸೂರ್ಯ ಬೆಳಗುತ್ತಿದ್ದಾನೆ", "The sun is shining"),
        ("ನನಗೆ ಹಸಿವಾಗಿದೆ", "I am hungry"),
        ("ಶೌಚಾಲಯ ಎಲ್ಲಿದೆ?", "Where is the toilet?")
    ],
    'Medium': [
        ("ಶುಭ ದಿನ, ನೀವು ಹೇಗಿದ್ದೀರಿ?", "Good day, how are you?"),
        ("ನಾನು ಒಂದು ಕಾಫಿ ಆರ್ಡರ್ ಮಾಡಲು ಬಯಸುತ್ತೇನೆ", "I would like to order a coffee"),
        ("ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಬಹುದೇ?", "Can you please help me?"),
        ("ಬೆಂಗಳೂರಿಗೆ ಮುಂದಿನ ರೈಲು ಯಾವಾಗ ಹೊರಡುತ್ತದೆ?", "When does the next train to Bangalore leave?"),
        ("ನನಗೆ ಇದು ಸಂಪೂರ್ಣವಾಗಿ ಅರ್ಥವಾಗುತ್ತಿಲ್ಲ", "I don't quite understand that"),
        ("ಇಂದು ಹವಾಮಾನ ತುಂಬಾ ಚೆನ್ನಾಗಿದೆ", "The weather is very nice today"),
        ("ನನ್ನ ಹವ್ಯಾಸಗಳು ಓದುವುದು ಮತ್ತು ಪ್ರಯಾಣಿಸುವುದು", "My hobbies are reading and traveling"),
        ("ನಾನು ಒಂದು ದೊಡ್ಡ ಕಂಪನಿಯಲ್ಲಿ ಇಂಜಿನಿಯರ್ ಆಗಿ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ", "I work as an engineer at a large company"),
        ("ನಾವು ನಿನ್ನೆ ಒಂದು ಆಸಕ್ತಿದಾಯಕ ಚಲನಚಿತ್ರ ನೋಡಿದೆವು", "We watched an interesting movie yesterday"),
        ("ದಯವಿಟ್ಟು ಅದನ್ನು ಪುನರಾವರ್ತಿಸಬಹುದೇ?", "Could you please repeat that?")
    ],
    'Hard': [
        ("ಜಾಗತೀಕರಣವು ಅನೇಕ ದೇಶಗಳ ಆರ್ಥಿಕ ಅಭಿವೃದ್ಧಿಯ ಮೇಲೆ ಗಮನಾರ್ಹವಾಗಿ ಪ್ರಭಾವ ಬೀರುತ್ತದೆ.", "Globalization significantly influences the economic development of many countries."),
        ("ವೈದ್ಯಕೀಯದಲ್ಲಿನ ಪ್ರಗತಿಗಳ ಹೊರತಾಗಿಯೂ, ಇನ್ನೂ ಗುಣಪಡಿಸಲಾಗದ ರೋಗಗಳಿವೆ.", "Despite advances in medicine, there are still incurable diseases."),
        ("ಜೀವನದ ಅರ್ಥದ ಬಗೆಗಿನ ತಾತ್ವಿಕ ಪ್ರಶ್ನೆಯು ಶತಮಾನಗಳಿಂದ ಮಾನವೀಯತೆಯನ್ನು ಕಾಡುತ್ತಿದೆ.", "The philosophical question about the meaning of life has occupied humanity for centuries."),
        ("ನಮ್ಮ ಗ್ರಹದ ಜೀವವೈವಿಧ್ಯವನ್ನು ಸಂರಕ್ಷಿಸಲು ಪರಿಸರ ಸಂರಕ್ಷಣಾ ಕ್ರಮಗಳು ಅತ್ಯಗತ್ಯ.", "Environmental protection measures are essential to preserve the biodiversity of our planet."),
        ("ಕ್ವಾಂಟಮ್ ಭೌತಶಾಸ್ತ್ರದ ಸಂಕೀರ್ಣ ಸಂಬಂಧಗಳು ತಜ್ಞರಿಗೂ ಸಹ ಗ್ರಹಿಸಲು ಕಷ್ಟಕರವಾಗಿರುತ್ತದೆ.", "The complex relationships in quantum physics are often difficult for even experts to comprehend."),
        ("ಸಾಮಾಜಿಕ ನಿಯಮಗಳು ಮತ್ತು ಮೌಲ್ಯಗಳು ನಿರಂತರ ಬದಲಾವಣೆಗೆ ಒಳಪಟ್ಟಿರುತ್ತವೆ.", "Societal norms and values are subject to constant change."),
        ("ನಿರಾಶ್ರಿತರ ಏಕೀಕರಣವು ಅನೇಕ ಯುರೋಪಿಯನ್ ರಾಷ್ಟ್ರಗಳಿಗೆ ದೊಡ್ಡ ಸವಾಲುಗಳನ್ನು ಒಡ್ಡುತ್ತದೆ.", "The integration of refugees presents many European countries with major challenges."),
        ("ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯು ಭವಿಷ್ಯಕ್ಕಾಗಿ ಅಪಾರ ಅವಕಾಶಗಳನ್ನು ಮತ್ತು ಸಂಭಾವ್ಯ ಅಪಾಯಗಳನ್ನು ಹೊಂದಿದೆ.", "Artificial intelligence holds both enormous opportunities and potential risks for the future."),
        ("ಆಧುನಿಕ ಕಲಾಕೃತಿಗಳ ವ್ಯಾಖ್ಯಾನಕ್ಕೆ ಐತಿಹಾಸಿಕ ಸಂದರ್ಭದ ಆಳವಾದ ತಿಳುವಳಿಕೆ ಅಗತ್ಯ.", "The interpretation of modern artworks often requires a deep understanding of the historical context."),
        ("ಸಮರ್ಥನೀಯ ಇಂಧನ ಮೂಲಗಳನ್ನು ಅಭಿವೃದ್ಧಿಪಡಿಸುವುದು ನಮ್ಮ ಕಾಲದ ಅತ್ಯಂತ ತುರ್ತು ಕಾರ್ಯಗಳಲ್ಲಿ ಒಂದಾಗಿದೆ.", "Developing sustainable energy sources is one of the most urgent tasks of our time.")
    ]
}

def get_random_kannada_sentence_with_translation(difficulty):
    """Fetches a random Kannada sentence and its translation based on the difficulty."""
    if difficulty in kannada_sentences_with_translations:
        sentence, translation = random.choice(kannada_sentences_with_translations[difficulty])
        return sentence, translation
    else:
        # Default to Easy if difficulty is invalid or not found
        print(f"Warning: Difficulty '{difficulty}' not found. Defaulting to Easy.")
        sentence, translation = random.choice(kannada_sentences_with_translations['Easy'])
        return sentence, translation