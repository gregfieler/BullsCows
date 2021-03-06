import pdb
import copy
import numpy as np
import random
import pandas as pd
import config as cfg
from tabulate import tabulate
import logging
import csv
from datetime import datetime
import os

def setup_dataframe():
  """
  build the guess position matrix with initial probabilities
  positions are represented by cols, guess values (guess_range) by rows
  """
  guess_list = []
  for g in range(guess_range):
    guess_list.append(g)
  position_list = []
  for p in range(game_positions):
    position_list.append(p)
  initial_weight = 1 / guess_range
  guess_position_matrix = pd.DataFrame(columns=position_list, index=guess_list).fillna(initial_weight)
  return guess_position_matrix

def random_answer ():
  """
  generate a random answer (list)
  returns: answer
  """  
  # use np.random.seed(n) for testing
  if cfg.debug:
    np.random.seed(cfg.random_seed) 
    # 999 answer: 5x10 [0, 5, 1, 8, 1] 4x7 [0, 4, 5, 1] 3x15 [0, 12, 5]
    # 123 answer: 5x10 [2, 2, 6, 1, 3] 4x7 [6, 5, 6, 2] 3x15 [14,13,14]
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
  bulls_factor = cfg.all_factor
  cows_factor = cfg.all_factor
  clue_weight = (clue[0] + clue[1]) / game_positions  # eg 1 bull+cow out of 5 is a factor of .2 4of5 = .8
  if clue[0] != game_positions:  
    bulls_factor = (game_positions / (game_positions - clue[0])) * (cfg.bulls_weight * clue_weight)
  if clue[1] != game_positions:   
    cows_factor = (game_positions / (game_positions - clue[1])) * (cfg.cows_weight * clue_weight) 
  clue_factor = 1 + (bulls_factor * cows_factor)
  return (clue_factor, bulls_factor, cows_factor)

def generate_guess():
  """
  use weighted random choice (normal distribution) to find the values with the highest weight
  """
  guess_list = []
  weights = []
  for i in range(game_positions):
      choice_weight = random.choices(guess_position_matrix[i], weights=guess_position_matrix[i])
      weights.append(choice_weight)
      guess = guess_position_matrix[guess_position_matrix[i]==choice_weight[0]].index.values
      guess_list.append(guess)
  logging.debug("{} generate_guess: guess list {} weights {}".format(game_id,guess_list,weights))
  guess = []
  # randomly choose one of the values with the highest weight
  for i in range(game_positions):
      guess.append(random.choice(guess_list[i]))
  logging.debug("{} generate_guess: working guess {}".format(game_id,guess))
  logging.debug("{} generate_guess: matrix {}".format(game_id,guess_position_matrix))

  return guess

def normalize_matrix(normalize_count):
  """
  update guess position matrix to reset weghts for better guesses
  """
  # guess_position_matrix = (guess_position_matrix - guess_position_matrix.mean()) / guess_position_matrix.std()
  #todo   ideas about how to normalize -  reset weights based on clues and reprocess clues - how expensive?
  if normalize_count == 1:
    logging.warning("{} normalize matrix {} first time(rescale) at guess {}".format(game_id,normalize_count,len(guesses_clues)))
    guess_position_matrix[guess_position_matrix !=0] = (guess_position_matrix - guess_position_matrix.min()) + 1/game_positions
  else:
    logging.warning("{} normalize matrix {} equal weight at guess {}".format(game_id,normalize_count,len(guesses_clues)))
    guess_position_matrix[guess_position_matrix !=0] = 1/game_positions
  # for position in range(game_positions):
  #     for value in range(guess_range):
  #         if guess_position_matrix.loc[value,position] > 1:
  #           guess_position_matrix.loc[value,position] = 1 - (1 / game_positions)
  logging.debug("{} matrix after normalize \n{}".format(game_id,guess_position_matrix))

def generate_best_guess ():
    """
    # need to work on this - danger of infiniate loop

    #todo restructure this  -  make new functions out of big tests here
    """
    global getting_close
    good_guess = False
    valid_guess = True
    normalize_count = 0
    while not good_guess:
      guess = generate_guess()
      guess_counts["guesses_generated"] += 1  
      # check to see if all_in_answer is satisfied
      ### answer must include is cccc <-- ooops, this is the wrong way
      if getting_close: # a previous guess had all the correct values
          check_them_off = copy.copy(all_in_answer)
          logging.debug("{} generate_best_guess: getting close guess {} all in {}".format(game_id,guess,check_them_off))
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
        if prev_guess[0] == guess:
          logging.warning("{} generate_best_guess: already tried {}, resetting weights".format(game_id,guess))
          guess_counts["duplicate_guesses"] += 1 
          repeated_guess = True
          #todo a better way - based on now many times the guess/pos has had high bulls scores (dictionary)
          normalize_count += 1
          normalize_matrix(normalize_count)
        else:
          if not inconsistent_guess: # already know this is not a good guess - no need to check more
            #      may want to reuse this code for validating user clues
            # use the guess as the answer and make sure all of previous guesses give the same answer
            match_clue = generate_clue(guess, prev_guess[0])
            if match_clue != prev_guess[1]:
              logging.warning("{} generate_best_guess: guess {} is not consistent with previous clues {} yeilds {}".format(game_id,guess,prev_guess,match_clue))
              guess_counts["inconsistent_guesses"] +=1
              inconsistent_guess = True
              # inconsistent_guess_list.append(guess) # todo need to save time and potentially improve normalization

      if valid_guess and not repeated_guess and not inconsistent_guess:  # valid guess should never be repeated?!
          good_guess = True
    return guess

def process_clue():
    """
    update the guess position matrix based on clue
    """
    # generate_factors
    clue_factor, bulls_factor, cows_factor = generate_factors() 
    #todo refactor this code
    if clue[0] == 0 and clue[1] == 0:  # none of these values are in the answer
        clue_counts["clue_bulls0cows0"] += 1
        for position in range(game_positions):
            # zero value in all positions
            guess_position_matrix.loc[guess[position]] = 0
    else:
        if clue[0] == 0:  # nothing is in the right spot
            clue_counts["clue_bulls0"] += 1   
            for position in range(game_positions):
                # zero value in bull positions
                guess_position_matrix.loc[guess[position],position] = 0
                # adjust weights for cows
                for value in range(guess_range):
                    guess_position_matrix.iloc[value,position] = guess_position_matrix.iloc[value,position] * clue_factor
    if clue[0] == 0 and clue[1] == game_positions: # all the right values none in correct position
        clue_counts["clue_bulls0cowsA"] += 1
        for position in range(game_positions):
            # zero guess in bull positions
            guess_position_matrix.loc[guess[position],position] = 0
            for value in range(guess_range):
                # todo    does this make sense?   
                guess_position_matrix.iloc[value,position] = guess_position_matrix.iloc[value,position] * clue_factor
    if clue[0] != 0:
        # adjust prob for bulls multiply current value by factor of bulls/positions (pos/(pos-bulls))
        clue_counts["clue_bullsX"] += 1
        for position in range(game_positions):
            guess_position_matrix.loc[guess[position],position] = guess_position_matrix.loc[guess[position],position] * clue_factor
    all_in_answer = []
    getting_close = False
    if clue[0] + clue[1] == game_positions:
        all_in_answer = guess
        getting_close = True
        # all of these must be in answer, save in global variable
        clue_counts["c_bullscowsA"] +=1
        # zero out all guess values not in all in answer
        for position in range(game_positions):
            for value in range(guess_range):
                if value not in all_in_answer:
                    guess_position_matrix.loc[value,position] = 0
    logging.debug("{} process_clue: {} {} {} factors: clue {:.4f} bulls {:.4f} cows {:.4f}".format(game_id,len(guesses_clues),clue,guess,clue_factor, bulls_factor, cows_factor))
    logging.debug("process_clue: matrix\n{}".format(game_id,guess_position_matrix))
    logging.debug("process_clue: guesses_clues {}".format(game_id,guesses_clues))
    return all_in_answer, getting_close

def write_stats ():
  """
  write stats to csv file
  """
  if not os.path.exists('bullscowsstats.csv'):
    with open('bullscowsstats.csv', 'a') as stats_file:
      headers = ['gametime','player','positions','range','answer','guesses','bull_weight','cow_weight','all_factor',\
        'guesses_generated','duplicate_guesses','inconsistent_guesses',\
        'clue_blulls0','clue_bulls0cows0','clue_bullsX','clue_bulls0cowsA','c_bullscowsA']
      write = csv.writer(stats_file)
      write.writerow(headers)
  stats = [game_id,cfg.guesser,cfg.game_posistions,cfg.guess_range,answer,len(guesses_clues),cfg.bulls_weight,cfg.cows_weight,cfg.all_factor,\
    guess_counts["guesses_generated"],guess_counts["duplicate_guesses"],guess_counts["inconsistent_guesses"],\
    clue_counts["clue_bulls0"],clue_counts["clue_bulls0cows0"],clue_counts["clue_bullsX"],clue_counts["clue_bulls0cowsA"],clue_counts["c_bullscowsA"]]
  with open('bullscowsstats.csv', 'a') as stats_file:
    write = csv.writer(stats_file)
    write.writerow(stats)

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
  logging.debug("{} generate_clue: working guess {} answer {} clue {}".format(game_id,guess_copy,answer_copy,clue))
  return clue

if __name__ == "__main__":
  #todo - change logging to use answer as part of filename
  logging.basicConfig(filename='bullsandcows.log', level=logging.INFO)
  logging.info("main: game: {} x {}, factors: bull {}, cow {}, all {}, seed: {}"\
    .format(cfg.game_posistions,cfg.guess_range,cfg.bulls_weight,cfg.cows_weight,cfg.all_factor,cfg.random_seed))
  if cfg.debug or cfg.autorun > 0:
      game_positions = cfg.game_posistions 
      guess_range = cfg.guess_range
  else:
      print("Let's play numbers!\nIt's a game a lot like 'Bulls and Cows.'\nI've made it so that you can make it easy OR make it extremely difficult.\n\n")
      print("Be warned, I'm really good at this.\n")
      print("how long a number do you want to play with?  (3 is pretty easy, 6 is challenging, 10 is extremely difficult)")
      game_positions = int(input("How many positions? "))
      print("Choices determines which digits to play with.  (6 would be like playing with 6 dice, 16 is like using hex values - very hard")
      guess_range = int(input("How many choices? "))
        
  permutations = (cfg.guess_range - 1) ** cfg.game_posistions
  print("\nthere are {} possible answers\n".format(permutations))

  # add a lookup with how many guesses this program usually takes or you should be able to solve this in x
  # todo   add logging for config info to use in stats  - day time  - maybe game id??

test_runs = cfg.autorun # 0 for normal play
try_again = True
while try_again:
  now = datetime.now()
  game_id = now.strftime('%Y%m%d.%H%M%S') # to make this a unique string - may need adjustment - 
  answer = random_answer()
  logging.info("main: answer: {}".format(answer))
  clue_counts = {"clue_bulls0":0,"clue_bulls0cows0":0,"clue_bullsX":0,"clue_bulls0cowsA":0,"c_bullscowsA":0}
  guess_counts = {"guesses_generated":0,"duplicate_guesses":0,"inconsistent_guesses":0 }
  guess_position_matrix = setup_dataframe()
  guesses_clues = []
  all_in_answer = [] # used to validate guesses when all values are known
  getting_close = False
  correct_guess = False
  guess = []
  seed_first_guess_for_stats = False
  if cfg.debug:
    seed_first_guess_for_stats = True 
  while not correct_guess:
    if seed_first_guess_for_stats:
      seed_first_guess_for_stats = False
      for g in range(game_positions): 
        guess.append(g)
    else:
      guess = generate_best_guess()
    clue = generate_clue(answer, guess)
    guesses_clues.append([guess, clue])
    logging.debug("main: {} guess {}: {} bulls: {}  cows: {}".format(game_id,len(guesses_clues),guess, clue[0], clue[1]))
    if clue[0] == game_positions:
      print("\nyou got it!  it took you {} tries\n".format(len(guesses_clues)))
      print("game review\n {}".format(tabulate(guesses_clues, headers=["guess", "clue"])))
      logging.info("{} final guesses ({}) clues list {}".format(game_id,len(guesses_clues),guesses_clues))
      logging.info("{} final clue counts {}".format(game_id,clue_counts))
      logging.info("{} final guess counts {}".format(game_id,guess_counts))
      logging.info("{} final matrix \n{}".format(game_id,guess_position_matrix))
      write_stats()
      correct_guess = True
    else:
      all_in_answer, getting_close = process_clue()
  
  test_runs -= 1
  if test_runs <= 0:
    try_again = False