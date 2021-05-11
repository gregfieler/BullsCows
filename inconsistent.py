     
     in generate best prev_guess
     
     # check to see if guess has been tried - if it has try agin - if not check for consistency
      repeated_guess = False
      inconsistent_guess = False
      if guess not in list(inconsistent_guess_list):
        for prev_guess in guesses_clues:
          normalized_once = False
          if guess == prev_guess[0]:
            logging.debug("generate_best_guess: already tried {}, resetting weights".format(guess))
            guess_counts["duplicate_guesses"] += 1 
            repeated_guess = True
            #todo a better way - based on now many times the guess/pos has had high bulls scores (dictionary)
            # guess_position_matrix[guess_position_matrix != 0] = 1 / game_positions
            if not normalized_once:
              normalize_matrix()
          else:
            # use the guess as the answer and make sure all of previous guesses give the same answer
            match_clue = generate_clue(guess, prev_guess[0])
            if match_clue != prev_guess[1]:
              logging.debug("guess {} is not consistent with previous clues {}".format(guess, match_clue))
              guess_counts["inconsistent_guesses"] +=1
              inconsistent_guess = True
              inconsistent_guess_list.append(guess)
      if valid_guess and not repeated_guess and not inconsistent_guess:  # valid guess should never be repeated?!
          good_guess = True
    return guess