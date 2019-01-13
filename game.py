#!/usr/local/bin/python3

import sys
import os

class InvalidEntriesCorrector:
    def __init__(self):
        self.entries = { '5': [str(x) for x in range(3, 10)] }
    def __str__(self):
        return str(self.entries)

def validate_reading(reading):
    return reading 
class Score:
    def __init__(self, home_score, home_set, guest_set, guest_score):
        self.home_score = home_score
        self.home_set = home_set
        self.guest_set = guest_set
        self.guest_score = guest_score
        self.invalid_entries_correct = InvalidEntriesCorrector()
    def parse_new_reading(self, reading):
        if not is_reading_valid(reading):
            reading = 
class Game:
    def __init__(self):
        self.previous_score = Score(0, 0, 0, 0)

def main():
    e = InvalidEntriesCorrector()
    print(str(e))

if __name__ == "__main__":
    main()
