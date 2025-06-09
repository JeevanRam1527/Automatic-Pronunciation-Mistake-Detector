import eng_to_ipa as ipa
import nltk
import re

try:
    # Check if the resource is available
    nltk.data.find('corpora/cmudict')
except LookupError:
    # If not found, download it
    print("NLTK CMU Dictionary resource not found locally or outdated. Downloading/Updating...")
    nltk.download('cmudict')
    print("Download complete.")

from nltk.corpus import cmudict

# Load the CMU dictionary
arpabet = cmudict.dict()

def get_phonemes(text):
    """Converts English text to its IPA phoneme representation using eng_to_ipa."""
    if not text:
        return ""
    try:
        phonemes = ipa.convert(text)
        return phonemes
    except Exception as e:
        print(f"Error converting text to IPA phonemes: {e}")
        return "(Error converting to IPA)"

def get_phonemes_and_stress(text):
    """Converts English text to ARPABET phonemes and extracts stress levels."""
    if not text:
        return [], []

    words = re.findall(r"\b\w+\b", text.lower()) # Tokenize and lowercase
    all_phonemes = []
    all_stresses = []

    for word in words:
        if word in arpabet:
            # Use the first pronunciation found
            pronunciation = arpabet[word][0]
            word_phonemes = []
            word_stresses = []
            for phon in pronunciation:
                stress = re.search(r'(\d)', phon)
                if stress:
                    word_stresses.append(stress.group(1))
                    # Remove stress digit for cleaner phoneme list if desired
                    # word_phonemes.append(re.sub(r'\d', '', phon))
                    word_phonemes.append(phon) # Keep stress in phoneme for now
                else:
                    word_stresses.append('0') # Assume unstressed if no digit
                    word_phonemes.append(phon)
            all_phonemes.extend(word_phonemes)
            all_stresses.extend(word_stresses)
        else:
            # Handle words not in CMUDict (e.g., use IPA as fallback or mark as unknown)
            # For simplicity, we'll skip unknown words for stress analysis for now
            # but you might want a more robust fallback.
            print(f"Warning: Word '{word}' not found in CMUdict. Skipping stress analysis for this word.")
            # Add placeholders or handle appropriately
            # ipa_phonemes = ipa.convert(word).split() # Get IPA as fallback
            # all_phonemes.extend(ipa_phonemes)
            # all_stresses.extend(['?'] * len(ipa_phonemes)) # Mark stress as unknown

    return all_phonemes, all_stresses

# Example usage:
if __name__ == '__main__':
    sentence = "This is a complex sentence with primary and secondary stress."
    ipa_phonemes = get_phonemes(sentence)
    arpabet_phonemes, stresses = get_phonemes_and_stress(sentence)

    print(f"Sentence: {sentence}")
    print(f"IPA Phonemes: {ipa_phonemes}")
    print(f"ARPABET Phonemes: {' '.join(arpabet_phonemes)}")
    print(f"Stress Pattern: {' '.join(stresses)}")

    sentence_2 = "Permit me to present the permit."
    ipa_phonemes_2 = get_phonemes(sentence_2)
    arpabet_phonemes_2, stresses_2 = get_phonemes_and_stress(sentence_2)
    print(f"\nSentence: {sentence_2}")
    print(f"IPA Phonemes: {ipa_phonemes_2}")
    print(f"ARPABET Phonemes: {' '.join(arpabet_phonemes_2)}")
    print(f"Stress Pattern: {' '.join(stresses_2)}")