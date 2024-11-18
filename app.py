from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secret key

# Example data for alphabet test words (you can update it with real data)
ALPHABET_TESTS = {
    'a': ["abbreviate", "abnormality", "abode", "abrasion", "abundantly", "academic",
    "accessory", "accordion", "acidic", "acne", "acrobat", "adhesive",
    "admirable", "adoption", "adversary", "affected", "affliction", "affordable",
    "agenda", "airport", "alimony", "allergic", "alliance", "alpaca",
    "alphabetical", "amateur", "amplify", "amusing", "animate", "anklebone",
    "annex", "antibacterial", "antibiotic", "anxiety", "apparition", "appease",
    "applause", "aptitude", "aquamarine", "arcade", "arrangement", "assortment",
    "athletic", "attractive", "auditory", "avalanche", "avocado"],
    'b': ["badminton", "balky", "Ballyhoo", "barbarian", "bareback", "bargain", "barrette"],
    'c': ["badminton", "balky", "Ballyhoo", "barbarian", "bareback", "bargain", "barrette"],
    'd': ["badminton", "balky", "Ballyhoo", "barbarian", "bareback", "bargain", "barrette"]
}

# Initialize the session for storing user progress and historical words
@app.before_request
def before_request():
    if 'scoring_board' not in session:
        session['scoring_board'] = {letter: {"correct": 0, "total": len(words)} for letter, words in ALPHABET_TESTS.items()}
        session['incorrect_words'] = []
        session['retest_words'] = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_test')
def select_test():
    return render_template('select_test.html', tests=ALPHABET_TESTS, scoring_board=session['scoring_board'])

@app.route('/start_test/<letter>', methods=['GET', 'POST'])
def start_test(letter):
    if letter not in ALPHABET_TESTS:
        return redirect(url_for('select_test'))
    
    words = ALPHABET_TESTS[letter]
    correct = session['scoring_board'][letter]['correct']
    total = session['scoring_board'][letter]['total']

    # Get the next word (cycle through)
    if 'current_word' not in session:
        session['current_word'] = words[0]

    current_word = session['current_word']

    if request.method == 'POST':
        user_input = request.form['user_input'].lower()
        correct_word = request.form['correct_word'].lower()
        
        if user_input == correct_word:
            session['scoring_board'][letter]['correct'] += 1
        else:
            session['incorrect_words'].append(correct_word)

        # Move to the next word in the test
        current_index = words.index(current_word)
        if current_index + 1 < len(words):
            session['current_word'] = words[current_index + 1]
        else:
            session['current_word'] = None  # Test completed

        # Check if the test is complete
        if session['current_word'] is None:
            if session['scoring_board'][letter]['correct'] == total:
                return render_template('test_complete.html', message="GOOD JOB! All words are correct!", letter=letter)
            else:
                return render_template('test_complete.html', message="Test complete! Some words are incorrect. Please retake.", letter=letter)

    return render_template('test.html', letter=letter, current_word=current_word, scoring_board=session['scoring_board'])

@app.route('/test_complete/<letter>', methods=['GET'])
def test_complete(letter):
    correct_words = session.get(f"{letter}_correct_words", 0)
    total_words = session.get(f"{letter}_total_words", 0)
    message = "GOOD JOB! All words are correct!" if correct_words == total_words else f"GOOD JOB! {correct_words} out of {total_words} words are correct. Please retake the test for the missed words."
    return render_template('test_complete.html', letter=letter, correct_words=correct_words, total_words=total_words, message=message)

@app.route('/retest_incorrect_words', methods=['GET', 'POST'])
def retest_incorrect_words():
    if not session['incorrect_words']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_input = request.form['user_input'].lower()
        correct_word = request.form['correct_word'].lower()

        if user_input == correct_word:
            session['retest_words'].remove(correct_word)
        else:
            session['incorrect_words'].append(correct_word)

        if not session['retest_words']:
            return render_template('retest_complete.html', message="Retest complete! All words are correct.", retest_words=session['retest_words'])

    current_word = session['retest_words'][0] if session['retest_words'] else None
    return render_template('retest.html', current_word=current_word, retest_words=session['retest_words'])

@app.route('/historical_misspelled_word_list')
def historical_misspelled_word_list():
    return render_template('historical_misspelled_word_list.html', words=session['incorrect_words'])

@app.route('/edit_misspelled_word_list', methods=['GET', 'POST'])
def edit_misspelled_word_list():
    if request.method == 'POST':
        word = request.form['word']
        action = request.form['action']
        
        if action == 'add' and word not in session['incorrect_words']:
            session['incorrect_words'].append(word)
        elif action == 'delete' and word in session['incorrect_words']:
            session['incorrect_words'].remove(word)
        
        session.modified = True

    return render_template('edit_misspelled_word_list.html', words=session['incorrect_words'])

@app.route('/pronounce_word/<word>')
def pronounce_word(word):
    # Replace with ResponsiveVoice or another AI TTS API call
    return render_template('play_sound.html', current_word=word)

@app.route('/get_definition/<word>')
def get_definition(word):
    api_key = 'your_wordnik_api_key'  # Replace with your Wordnik API key
    response = requests.get(f"https://api.wordnik.com/v4/word.json/{word}/definitions?api_key={api_key}")
    data = response.json()
    definition = data[0]['text'] if data else "No definition found."
    return definition

@app.route('/get_example_sentence/<word>')
def get_example_sentence(word):
    api_key = 'your_wordnik_api_key'  # Replace with your Wordnik API key
    response = requests.get(f"https://api.wordnik.com/v4/word.json/{word}/exampleSentences?api_key={api_key}")
    data = response.json()
    sentence = data[0]['text'] if data else "No sentence example found."
    return sentence

if __name__ == '__main__':
    app.run(debug=True)
