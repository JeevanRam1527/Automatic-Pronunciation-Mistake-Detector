import random

german_sentences_with_translations = {
    'Easy': [
        ("Hallo Welt", "Hello World"),
        ("Ich bin ein Student", "I am a student"),
        ("Das ist ein Apfel", "That is an apple"),
        ("Er liest ein Buch", "He reads a book"),
        ("Sie trinkt Wasser", "She drinks water"),
        ("Wir lernen Deutsch", "We are learning German"),
        ("Der Himmel ist blau", "The sky is blue"),
        ("Die Sonne scheint", "The sun is shining"),
        ("Ich habe Hunger", "I am hungry"),
        ("Wo ist die Toilette?", "Where is the toilet?")
    ],
    'Medium': [
        ("Guten Tag, wie geht es Ihnen?", "Good day, how are you?"),
        ("Ich möchte einen Kaffee bestellen", "I would like to order a coffee"),
        ("Können Sie mir bitte helfen?", "Can you please help me?"),
        ("Wann fährt der nächste Zug nach Berlin?", "When does the next train to Berlin leave?"),
        ("Ich verstehe das nicht ganz", "I don't quite understand that"),
        ("Das Wetter ist heute sehr schön", "The weather is very nice today"),
        ("Meine Hobbys sind Lesen und Reisen", "My hobbies are reading and traveling"),
        ("Ich arbeite als Ingenieur bei einer großen Firma", "I work as an engineer at a large company"),
        ("Wir haben gestern einen interessanten Film gesehen", "We watched an interesting movie yesterday"),
        ("Könnten Sie das bitte wiederholen?", "Could you please repeat that?")
    ],
    'Hard': [
        ("Die Globalisierung beeinflusst die wirtschaftliche Entwicklung vieler Länder maßgeblich.", "Globalization significantly influences the economic development of many countries."),
        ("Trotz der Fortschritte in der Medizin gibt es immer noch unheilbare Krankheiten.", "Despite advances in medicine, there are still incurable diseases."),
        ("Die philosophische Frage nach dem Sinn des Lebens beschäftigt die Menschheit seit Jahrhunderten.", "The philosophical question about the meaning of life has occupied humanity for centuries."),
        ("Umweltschutzmaßnahmen sind unerlässlich, um die Biodiversität unseres Planeten zu erhalten.", "Environmental protection measures are essential to preserve the biodiversity of our planet."),
        ("Die komplexen Zusammenhänge der Quantenphysik sind selbst für Experten oft schwer nachvollziehbar.", "The complex relationships in quantum physics are often difficult for even experts to comprehend."),
        ("Gesellschaftliche Normen und Werte unterliegen einem ständigen Wandel.", "Societal norms and values are subject to constant change."),
        ("Die Integration von Flüchtlingen stellt viele europäische Staaten vor große Herausforderungen.", "The integration of refugees presents many European countries with major challenges."),
        ("Künstliche Intelligenz birgt sowohl enorme Chancen als auch potenzielle Risiken für die Zukunft.", "Artificial intelligence holds both enormous opportunities and potential risks for the future."),
        ("Die Interpretation moderner Kunstwerke erfordert oft ein tiefgehendes Verständnis des historischen Kontexts.", "The interpretation of modern artworks often requires a deep understanding of the historical context."),
        ("Nachhaltige Energiequellen zu erschließen ist eine der dringendsten Aufgaben unserer Zeit.", "Developing sustainable energy sources is one of the most urgent tasks of our time.")
    ]
}

def get_random_german_sentence_with_translation(difficulty):
    """Fetches a random German sentence and its translation based on the difficulty."""
    if difficulty in german_sentences_with_translations:
        sentence, translation = random.choice(german_sentences_with_translations[difficulty])
        return sentence, translation
    else:
        # Default to Easy if difficulty is invalid or not found
        print(f"Warning: Difficulty '{difficulty}' not found. Defaulting to Easy.")
        sentence, translation = random.choice(german_sentences_with_translations['Easy'])
        return sentence, translation