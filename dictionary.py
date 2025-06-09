import requests
import json

def get_word_definition(word):
    """
    Fetches the definition of a word using the free DictionaryAPI.
    Args:
        word (str): The word to look up.
    Returns:
        str: The first definition found, or an error message.
    """
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        # Extract the first definition
        if data and isinstance(data, list):
            first_entry = data[0]
            if 'meanings' in first_entry and first_entry['meanings']:
                first_meaning = first_entry['meanings'][0]
                if 'definitions' in first_meaning and first_meaning['definitions']:
                    first_definition = first_meaning['definitions'][0]
                    if 'definition' in first_definition:
                        return first_definition['definition']
        
        return "Definition not found."

    except requests.exceptions.RequestException as e:
        print(f"Error fetching definition for '{word}': {e}")
        # Check if the error is a 404 Not Found
        if response.status_code == 404:
            return f"No definition found for '{word}'."
        return "Error fetching definition."
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for '{word}'. Response text: {response.text}")
        return "Error processing definition response."
    except Exception as e:
        print(f"An unexpected error occurred for '{word}': {e}")
        return "An unexpected error occurred."

# Example usage:
# if __name__ == '__main__':
#     word_to_lookup = "hello"
#     definition = get_word_definition(word_to_lookup)
#     print(f"Definition of '{word_to_lookup}': {definition}")
#
#     word_to_lookup = "nonexistentwordxyz"
#     definition = get_word_definition(word_to_lookup)
#     print(f"Definition of '{word_to_lookup}': {definition}")