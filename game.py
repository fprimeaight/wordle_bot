import random
      
class Wordle():
    def __init__(self):
        self.solution = None
        self.dictionary = {}
        self.board = [[(-1, '') for i in range(5)] for i in range(6)]
        self.curr_row = 0
        self.keyboard = {chr(i): None for i in range(65,91)}

    def generate_solution(self):
        word_list = []

        f = open('wordle_answers.txt','r')
        for line in f:
            word_list.append(line.strip())
        f.close()

        solution = random.choice(word_list).upper()

        for letter in solution:
            if letter not in self.dictionary:
                self.dictionary[letter] = 1
            else:
                self.dictionary[letter] += 1

        self.solution = solution

    def check_word_exists(self, word):
        word = word.strip().upper()
        word_exists = False
      
        f = open('words.txt','r')
        for line in f:
            if word == line.strip().upper():
                word_exists = True
                break

        return word_exists

    def eval_word(self, word):
        word = word.strip().upper()
        output = [None] * 5
        dictionary_copy = self.dictionary.copy()

        for idx, letter in enumerate(word):
            if letter == self.solution[idx]:
                bool, char = 1, letter
                output[idx] = (bool, char)
                dictionary_copy[letter] -= 1
                self.keyboard[char] = 1

        for idx, letter in enumerate(word):
            if (letter in self.solution and letter != self.solution[idx] 
                and dictionary_copy[letter] > 0):
                bool, char = 0, letter
                output[idx] = (bool, char)
                dictionary_copy[letter] -= 1
                if self.keyboard[char] == None:
                    self.keyboard[char] = 0

        for idx, tuple in enumerate(output):
            if tuple == None:
                bool, char = -1, word[idx]
                output[idx] = (bool, char)
                if self.keyboard[char] == None:
                    self.keyboard[char] = -1

        self.board[self.curr_row] = output
        self.curr_row += 1

    def check_win(self, word):
        word = word.strip().upper()
        return word == self.solution
    
    def check_lose(self):
        return self.curr_row > 5
