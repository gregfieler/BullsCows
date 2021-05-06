import pdb
import copy
import numpy as np
import random
import pandas as pd
import config as cfg
from tabulate import tabulate
import logging

def game_log (message):
  if cfg.print_debug_msgs:
    print(message)

def setup_dataframe(game_positions, guess_range):
  """
  build the positions and guess/answer dataframe with initial probabilities
  positions are represented by cols, guess values (guess_range) by rows
  """
  ges_list = []
  for g in range(guess_range):
    ges_list.append(g)
  pos_list = []
  for p in range(game_positions):
    pos_list.append(p)

  initial_probability = 1 / guess_range
  guess_position_matrix = pd.DataFrame(columns=pos_list, index=ges_list).fillna(initial_probability)
  return guess_position_matrix

def random_answer (game_positions, guess_range):
  """
  generate a random answer (list) of the size specified by game_posistions
  using the number of possible values based on guess_range
  returns: answer
  """  
  # use np.random.seed(n) for testing
  #   np.random.seed(999) # answer: 5x10 [0, 5, 1, 8, 1] 
  answer = []
  for i in range(game_positions):
    answer.append(np.random.randint(0,guess_range))
  return answer

def generate_factors():
  """
  these factors are used to update the guess_position_matrix
  weights are in the config.py 
  todo - track results from these configs to train an algorhythm to optimize these weights
  """
  bulls_factor = 1
  cows_factor = 1
  clue_factor = (clue[0] + clue[1]) / game_positions
  if clue[0] != game_positions:
      bulls_factor = (game_positions / (game_positions - clue[0])) + (cfg.bulls_weight * clue_factor)
  if clue[1] != game_positions:
      cows_factor = (game_positions / (game_positions - clue[1])) + (cfg.cows_weight * clue_factor) 
  else:
      cows_factor = cfg.all_cows_factor * clue_factor 

  return (clue_factor, bulls_factor, cows_factor)

def generate_guess():
  guess_list = []
  # use weighted random choice (normal distribution) to find the values with the highest weight
  weights = []
  for i in range(game_positions):
      choice_weight = random.choices(guess_position_matrix[i], weights=guess_position_matrix[i])
      weights.append(choice_weight)
      guess = guess_position_matrix[guess_position_matrix[i]==choice_weight[0]].index.values
      guess_list.append(guess)
  game_log("generate_guess: guess list {} weights {}".format(guess_list,weights))
  guess = []
  # randomly choose one of the values with the highest weight
  for i in range(game_positions):
      guess.append(random.choice(guess_list[i]))
  game_log("generate_guess: working guess {}".format(guess))

  return guess

def generate_best_guess ():
    """
    # need to work on this - danger of infiniate loop
    """
    global getting_close
    good_guess = False
    valid_guess = True
    while not good_guess:
      guess = generate_guess()
      # check to see if all_in_answer is satisfied
      ### answer must include is cccc <-- ooops, this is the wrong way
      if getting_close: # a previous guess had all the correct values
          check_them_off = copy.copy(all_in_answer)
          game_log("generate_best_guess: guess {} all in {}".format(guess,check_them_off))
          # walk thru must include - check them off
          match_count = 0
          valid_guess = True
          for i in range(game_positions): 
              for x in range(game_positions):
                  if guess[i] == check_them_off[x]:
                      check_them_off[x] = 'c'
                      match_count += 1
                      break
          if match_count != game_positions:
              # guess is not correct
              valid_guess = False
      # check to see if guess has been tried - if it has try agin - if not check for consistency
      repeated_guess = False
      inconsistent_guess = False
      for prev_guess in guesses_clues:
        if guess == prev_guess[0]:
          game_log("generate_best_guess: already tried {}, resetting weights".format(guess))
          repeated_guess = True
          #todo a better way - based on now many times the guess/pos has had high bulls scores (dictionary)
          guess_position_matrix[guess_position_matrix != 0] = 1 / game_positions
        else:
          # use the guess as the answer and make sure all of previous guesses give the same answer
          match_clue = generate_clue(guess, prev_guess[0])
          if match_clue != prev_guess[1]:
            game_log("guess {} is not consistent with previous clues {}".format(guess, match_clue))
            inconsistent_guess = True

      if valid_guess and not repeated_guess and not inconsistent_guess:  # valid guess should never be repeated?!
          good_guess = True

    return guess

def process_clue():
    """
    update the guess position matrix based on clue
    """
    # generate_factors
    clue_factor, bulls_factor, cows_factor = generate_factors()
    game_log("process_clue: factors: clue {:.4f} bulls {:.4f} cows {:.4f}".format(clue_factor, bulls_factor, cows_factor))
    
    if clue[0] == 0 and clue[1] == 0:  # none of these values are in the answer
        game_log("process_clue: best clue no bulls or cows: zero out guess in all positions {}".format(guess))
        for position in range(game_positions):
            guess_position_matrix.loc[guess[position]] = 0
    else:
        if clue[0] == 0:  # nothing is in the right spot
            game_log("process_clue: great clue no bulls: zero out guess position {}".format(guess))
            for position in range(game_positions):
                guess_position_matrix.loc[guess[position],position] = 0
                for value in range(guess_range):
                    guess_position_matrix.iloc[value,position] = guess_position_matrix.iloc[value,position] * bulls_factor * cows_factor

    if clue[0] == 0 and clue[1] == game_positions: # all the right values none in correct position
        game_log("process_clue: great clue no cows: zero out guess position, strenghen weight in other positions {}".format(guess))
        for position in range(game_positions):
            guess_position_matrix.loc[guess[position],position] = 0
            for value in range(guess_range):
                guess_position_matrix.iloc[value,position] = guess_position_matrix.iloc[value,position] * bulls_factor * cows_factor

    if clue[0] != 0:
        # adjust prob for bulls multiply current value by factor of bulls/positions (pos/(pos-bulls))
        game_log("process_clue: good clue - adjust weights {} by *  c{:.4f}*b{:.4f}+c{:.4f}".format(guess,clue_factor,bulls_factor,cows_factor))
        for position in range(game_positions):
            guess_position_matrix.loc[guess[position],position] = \
            guess_position_matrix.loc[guess[position],position] * bulls_factor * cows_factor

    all_in_answer = []
    getting_close = False
    if clue[0] + clue[1] == game_positions:
        all_in_answer = guess
        getting_close = True
        # all of these must be in answer, save in global variable
        game_log("process_clue: big clue - all right answers but not in correct position {}".format(all_in_answer))
    
    return all_in_answer, getting_close

def generate_clue (answer, guess):
  """ 
  calculates 'bulls' (correct value in correct spot) and 'cows' (value in answer but not in correct spot)
  the values in the answer do not have to be unique - makes it challenging
  returns: clue
  """
  bulls = 0 # correct guesses in the correct position
  cows = 0  # guesses in answer that are not in the correct position
  answer_copy = copy.copy(answer)  # need to be able to avoid problems with counting cows
  guess_copy = copy.copy(guess)    # once a position is matched  !! assigment = (pointer)
  for i in range(game_positions):
    if guess_copy[i] == answer_copy[i]:
      bulls += 1
      answer_copy[i] = 'not cow'  # remove the answer, it's already a counted as a bull
      guess_copy[i] = 'bull'      # remove from guess to avoid overcounting duplicates
  # if didn't match all positions we need to see if there are cows (in the answer but not in position and NOT double counted)
  if bulls < game_positions:
      for i in range(game_positions):  
        if guess_copy[i] != 'bull': 
            for x in range(game_positions):
                if guess_copy[i] == answer_copy[x]:
                    answer_copy[x] = 'cow'
                    cows +=1
                    break

  clue = [bulls,cows]
  game_log("generate_clue: working guess {} answer {} clue {}".format(guess_copy,answer_copy,clue))
  return clue

if __name__ == "__main__":
  debug = cfg.debug
  if debug:
      game_positions = cfg.game_posistions # big test is 5x10
      guess_range = cfg.guess_range
  else:
      game_positions = int(input("how many positions? "))
      guess_range = int(input("how many choices? "))

  guess_position_matrix = setup_dataframe(game_positions, guess_range)
  guesses_clues = []
  all_in_answer = []
  getting_close = False

# to test matrix weights in 5X10 game
  # prob_bump = 10 # this should force the answer
  # guess_position_matrix.loc[0,0] = prob_bump  # setup answer
  # guess_position_matrix.loc[5,1] = prob_bump
  # guess_position_matrix.loc[1,2] = prob_bump
  # guess_position_matrix.loc[8,3] = prob_bump
  # guess_position_matrix.loc[1,4] = prob_bump
  # guess_position_matrix.loc[6] = 0 # for testing, no 6's

try_again = True
while try_again:
  answer = random_answer(game_positions, guess_range)
  game_log("main: answer: {}".format(answer))
  correct_guess = False
  while not correct_guess:
    guess = generate_best_guess()
    clue = generate_clue(answer, guess)
    all_in_answer, getting_close = process_clue()
    guesses_clues.append([guess,clue])
    game_log("main: guess {}: {} bulls: {}  cows: {}".format(len(guesses_clues),guess, clue[0], clue[1]))
    if clue[0] == game_positions:
      permutations = cfg.guess_range ** cfg.game_posistions
      print("\nyou got it!  it took you {} tries\nthere are {} possible answers\n".format(len(guesses_clues),permutations))
      correct_guess = True
      review_guesses_clues = input("do you want to review the guesses and clues? ").lower()
      if review_guesses_clues == 'y':
        print(tabulate(guesses_clues, headers=["guess", "clue"]))

  try_again = False


 


