import streamlit as st
import random
import time
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Word Scramble Game",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .word-display {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        background-color: red;
        border-radius: 10px;
        margin: 20px 0;
        letter-spacing: 5px;
    }
    .score-display {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #28a745;
    }
    .hint-text {
        font-size: 18px;
        color: black;
        text-align: center;
        font-style: italic;
    }
    .timer {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #dc3545;
    }
    .category-btn {
        width: 100%;
        padding: 20px;
        margin: 5px;
        border-radius: 10px;
        border: none;
        background-color: #007bff;
        color: white;
        font-size: 18px;
        cursor: pointer;
    }
    .category-btn:hover {
        background-color: #0056b3;
    }
    .stats-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Word categories and their words
WORD_CATEGORIES = {
    "Animals": ["ELEPHANT", "GIRAFFE", "PENGUIN", "KANGAROO", "DOLPHIN", "CHEETAH", "ZEBRA", "LION", "TIGER", "MONKEY"],
    "Countries": ["FRANCE", "JAPAN", "BRAZIL", "CANADA", "INDIA", "AUSTRALIA", "EGYPT", "ITALY", "SPAIN", "MEXICO"],
    "Fruits": ["APPLE", "BANANA", "ORANGE", "MANGO", "GRAPE", "PINEAPPLE", "STRAWBERRY", "KIWI", "PEACH", "PLUM"],
    "Sports": ["FOOTBALL", "BASKETBALL", "TENNIS", "CRICKET", "VOLLEYBALL", "HOCKEY", "BASEBALL", "RUGBY", "GOLF", "BOXING"]
}

# Initialize session state
if 'current_word' not in st.session_state:
    st.session_state.current_word = ""
if 'scrambled_word' not in st.session_state:
    st.session_state.scrambled_word = ""
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'current_category' not in st.session_state:
    st.session_state.current_category = None
if 'hints_remaining' not in st.session_state:
    st.session_state.hints_remaining = 3
if 'game_history' not in st.session_state:
    st.session_state.game_history = []
if 'words_played' not in st.session_state:
    st.session_state.words_played = set()

def scramble_word(word):
    """Scramble the letters of a word"""
    word_list = list(word)
    scrambled = word
    while scrambled == word:  # Ensure the word is actually scrambled
        random.shuffle(word_list)
        scrambled = ''.join(word_list)
    return scrambled

def get_new_word(category):
    """Get a new word from the specified category"""
    available_words = [word for word in WORD_CATEGORIES[category] 
                      if word not in st.session_state.words_played]
    if not available_words:
        st.session_state.words_played.clear()  # Reset if all words are used
        available_words = WORD_CATEGORIES[category]
    
    word = random.choice(available_words)
    st.session_state.words_played.add(word)
    return word

def start_new_game(category):
    """Initialize a new game"""
    st.session_state.current_category = category
    st.session_state.current_word = get_new_word(category)
    st.session_state.scrambled_word = scramble_word(st.session_state.current_word)
    st.session_state.game_active = True
    st.session_state.start_time = time.time()
    st.session_state.hints_remaining = 3
    st.session_state.attempts = 0

def check_answer(user_answer):
    """Check if the user's answer is correct"""
    st.session_state.attempts += 1
    if user_answer.upper() == st.session_state.current_word:
        time_taken = int(time.time() - st.session_state.start_time)
        base_score = 100
        time_penalty = max(0, time_taken - 30) // 5  # Penalty for taking more than 30 seconds
        attempt_penalty = (st.session_state.attempts - 1) * 10
        final_score = max(0, base_score - time_penalty - attempt_penalty)
        
        st.session_state.score += final_score
        
        # Save game history
        game_record = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'category': st.session_state.current_category,
            'word': st.session_state.current_word,
            'attempts': st.session_state.attempts,
            'time_taken': time_taken,
            'score': final_score
        }
        st.session_state.game_history.append(game_record)
        
        return True
    return False

def main():
    st.title("🎯 Word Scramble Game")
    
    if not st.session_state.game_active:
        st.write("### Choose a Category to Start")
        
        # Display categories in a grid
        cols = st.columns(len(WORD_CATEGORIES))
        for idx, category in enumerate(WORD_CATEGORIES.keys()):
            with cols[idx]:
                if st.button(f"Play {category}", key=f"cat_{category}"):
                    start_new_game(category)
                    st.rerun()
        
        # Display game history and stats if available
        if st.session_state.game_history:
            st.write("### Your Game Statistics")
            
            # Convert game history to DataFrame
            history_df = pd.DataFrame(st.session_state.game_history)
            
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = history_df['score'].mean()
                st.markdown(f"""
                    <div class='stats-card'>
                        <h4>Average Score</h4>
                        <div class='score-display'>{avg_score:.1f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                best_score = history_df['score'].max()
                st.markdown(f"""
                    <div class='stats-card'>
                        <h4>Best Score</h4>
                        <div class='score-display'>{best_score}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_games = len(history_df)
                st.markdown(f"""
                    <div class='stats-card'>
                        <h4>Total Games</h4>
                        <div class='score-display'>{total_games}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Performance trend
            fig = px.line(history_df, x=history_df.index, y='score', 
                         title='Your Score History')
            st.plotly_chart(fig)
            
            # Category performance
            category_avg = history_df.groupby('category')['score'].mean()
            fig2 = px.bar(category_avg, title='Average Score by Category')
            st.plotly_chart(fig2)
    
    else:
        # Display game interface
        st.markdown(f"### Category: {st.session_state.current_category}")
        st.markdown(f"<div class='score-display'>Score: {st.session_state.score}</div>", 
                   unsafe_allow_html=True)
        
        # Display scrambled word
        st.markdown(f"<div class='word-display'>{st.session_state.scrambled_word}</div>", 
                   unsafe_allow_html=True)
        
        # Timer
        elapsed_time = int(time.time() - st.session_state.start_time)
        st.markdown(f"<div class='timer'>Time: {elapsed_time} seconds</div>", 
                   unsafe_allow_html=True)
        
        # Input field
        user_answer = st.text_input("Enter your answer:", key="answer").strip()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Submit"):
                if user_answer:
                    if check_answer(user_answer):
                        st.success("Correct! 🎉")
                    else:
                        st.error("Try again!")
        
        with col2:
            if st.button("Get Hint") and st.session_state.hints_remaining > 0:
                st.session_state.hints_remaining -= 1
                hint_index = random.randint(0, len(st.session_state.current_word)-1)
                hint = f"Letter {hint_index+1} is '{st.session_state.current_word[hint_index]}'"
                st.markdown(f"<div class='hint-text'>{hint}</div>", unsafe_allow_html=True)
                st.write(f"Hints remaining: {st.session_state.hints_remaining}")
        
        with col3:
            if st.button("End Game"):
                st.session_state.game_active = False
                st.rerun()

if __name__ == "__main__":
    main()