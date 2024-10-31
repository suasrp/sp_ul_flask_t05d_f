from flask import Flask, render_template, request, redirect, url_for, flash
from gtts import gTTS
from nltk.corpus import wordnet
import os
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

words = [
    # Your list of words goes here
]

# Create 26 tests (A-Z)
def create_tests(words_list):
    tests = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        filtered_words = [word for word in words_list if word.startswith(letter)]
        tests[letter] = filtered_words
    return tests

tests = create_tests(words)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_test')
def select_test():
    return render_template('select_test.html', tests=tests)

@app.route('/start_test/<letter>', methods=['GET', 'POST'])
def start_test(letter):
    if request.method == 'POST':
        # Handle answer submission
        user_input = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']
        if user_input == correct_word:
            flash('Correct!', 'success')
        else:
            flash(f'Incorrect. The correct spelling is: {correct_word}', 'danger')
        return redirect(url_for('start_test', letter=letter))

    words_to_test = tests[letter]
    current_word = random.choice(words_to_test)  # Randomly select a word for the test
    return render_template('test.html', letter=letter, current_word=current_word)

@app.route('/pronounce/<word>')
def pronounce(word):
    tts = gTTS(text=word, lang='en')
    filename = 'static/temp_word.mp3'
    tts.save(filename)
    return redirect(url_for('play_sound', filename='temp_word.mp3'))

@app.route('/play_sound/<filename>')
def play_sound(filename):
    return render_template('play_sound.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
