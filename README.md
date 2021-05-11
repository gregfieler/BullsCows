# Number Slueth - Bulls and Cows on steriods

building algorhythms for inductive reasoning

So far this is simply a python script that can efficiently guess the 'answer' in the minimum number of guesses.

The game can have as many 'positions' with as many choices as the user chooses.  For example: a 3 position game with 6 choices choosing the values for 3 dice as the answer.  The guesser has to pick the correct value for each dice, in order (duplicates are allowed.)

secret answer [3,5,5]
guess [1,2,3] -> clue O bulls 1 cows
guess [3,4,5] -> clue 2 bulls 0 cows
guess [3,4,6] -> clue 1 bulls 0 cows
guess [3,5,5] -> clue 3 bulls = success!

This project is for practice and learning.  The 'business logic' is mostly about how this program uses an algorhythm for generating guesses.  

---
***brainstorming***

so you're in the pasture and you see a bunch of shit on the ground...

make the guesses into poo shapes

maybe even make the ui have cows with halo's or embarassed looks or something.



guess the number - instead of calling it bulls and cows 

wanna try it in HEX?
i'll need to map 2 digit integers to hex (easiest/right? way simply do it in the UI - integers can represent anything 0,1,2,3,4,5 could be side of dice, 0-15 c/b 0-F)

