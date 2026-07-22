import csv
from collections import Counter

def load_data(filepath: str) -> tuple[list[str], dict[str, int]]:
    words = []
    freqs = {}
    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                word = row[0].strip().lower()
                if word == "word" or len(word) != 5:  
                    continue
                try:
                    count = int(row[1].strip())
                except ValueError:
                    continue

                words.append(word)
                freqs[word] = count
    except FileNotFoundError:
        print(f"⚠️ Warning: '{filepath}' not found.")
    return words, freqs

def score_guess(guess: str, answer: str) -> list[str]:
    result = ["gray"] * 5
    answer_chars = list(answer)
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = "green"
            answer_chars[i] = None
    for i, g in enumerate(guess):
        if result[i] == "green":
            continue
        if g in answer_chars:
            result[i] = "yellow"
            answer_chars[answer_chars.index(g)] = None
    return result

# NEW: Translates "bbgyy" from the web form into ["gray", "gray", "green", "yellow", "yellow"]
def parse_feedback_string(feedback_str: str) -> list[str]:
    color_map = {"b": "gray", "y": "yellow", "g": "green"}
    return [color_map.get(char, "gray") for char in feedback_str]

def filter_candidates(candidates: list[str], guess: str, feedback: list[str]) -> list[str]:
    def is_consistent(word: str) -> bool:
        for i, (letter, color) in enumerate(zip(guess, feedback)):
            if color == "green":
                if word[i] != letter:
                    return False
            elif color == "yellow":
                if letter not in word or word[i] == letter:
                    return False
            elif color == "gray":
                green_yellow_count = sum(
                    1 for j, (l, c) in enumerate(zip(guess, feedback))
                    if l == letter and c in ("green", "yellow")
                )
                if word.count(letter) > green_yellow_count:
                    return False
        return True
    return [word for word in candidates if is_consistent(word)]

def best_guesses(candidates: list[str], all_words: list[str], frequencies: dict[str, int], top_n: int = 3) -> list[str]:
    freq = Counter()
    for word in candidates:
        freq.update(set(word))
    def score_word(word: str) -> tuple:
        unique_letters = set(word)
        letter_score = sum(freq[ch] for ch in unique_letters)
        in_candidates = word in candidates
        word_count = frequencies.get(word, 0)
        return (in_candidates, word_count, letter_score)
    return sorted(all_words, key=score_word, reverse=True)[:top_n]