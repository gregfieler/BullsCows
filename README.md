# Number Sleuth - Bulls and Cows on Steriods

building algorhythms for inductive reasoning

So far this is simply a python script that attempts to efficiently guess the 'answer' in the minimum number of guesses.

The game can have as many 'positions' with as many values as the user chooses.  For example: a 3 position game with 6 values would be like playing with choosing 3 dice as the answer.  The guesser has to pick the correct value for each dice in the correct order (duplicates are allowed.)

- secret answer [3,5,5]
- guess [1,2,3] -> clue O bulls 1 cows
- guess [3,4,5] -> clue 2 bulls 0 cows
- guess [3,4,6] -> clue 1 bulls 0 cows
- guess [3,5,5] -> clue 3 bulls = success!

This project is for practice and learning.  The 'business logic' is mostly about how this program uses an algorhythm for generating guesses.  

## changes
- updated process clues to stop review of inconsistent guesses when even one is found
- updated normalize logic to go to equal weights after the first attempt (fixed permuataions calc)

## stuff to work on
- [x] need to figure out what's wrong with permutations calc
- [x] save results to a csv file
  - use it as a dataframe inside scripts that calc averages and analyze factor effectiveness
- [ ] review logging.info's change to debug
- build a UI (Django,react??)
  - restructure project MVC
- make a new module to process results
  - calculate performance (send avg guess by game size to main module, study how configutation factors affect matrix)
- when human player is giving clues need a way to make sure clues are consistent (or risk an ∞ loop)
  - first step should be to check the consistency of the users clue
  - this logic may be expensive so use it when guesses for this size game exceeds 2?3?std deviations?
  - loop thru guesses checking that clue is same, if not mark clue(s) as suspicious
    - msg user clue x is inconsistent with clue y
- [x] figure out how to reduce insonsistent guesses
  

---
***brainstorming***

maybe just make it a dice game - use only 1-6 for values, any number of positions - clues could be dice in different colors (makes it simpler? - does any of the logic change - it shouldn't)

sell this to a game developer who makes puzzles for getting through levels - let them do the UI
"I've got an inductive reasoning game that can be very easy or be made VERY difficult (requireing at least a spreadsheet to beat it)"

use this game as a coding innerview for employers - 
if you can't beat me (my programming) at this game you should hire me.

so you're in the pasture and you see a bunch of shit on the ground...

make the guesses into poo shapes

maybe even make the ui have cows with halo's or embarassed looks or something.

guess the number - instead of calling it bulls and cows 

wanna try it in HEX?
i'll need to map 2 digit integers to hex (easiest/right? way simply do it in the UI - integers can represent anything 0,1,2,3,4,5 could be side of dice, 0-15 c/b 0-F)

### game script

"I'm picking a die to put in each of the numbered boxes.  You place one of your die in front of each box.  If your choices match mine, you win.  If not I'll give you a clue.  You have Y gueses to get the right answer."

"if you think i'm cheating i double dog dare youto try! you pick the number and I guess, then I pick a number and you guess. I'll bet I can beat you 2/3 times, best of 5, best of 6 - you choose"







