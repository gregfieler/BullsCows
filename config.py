# weights are update the guess_position_matrix based on clues
bulls_weight = .7
cows_weight = .3
# changed cows weight from .3 to .5  to test if weights should be different
all_factor = .5  
# use debug true to set seed and initial guess for testing
debug = True  
random_seed = 123 # only used for debug  
# 999 answer: 5x10 [0, 5, 1, 8, 1] 4x7 [0, 4, 5, 1] 3x15 [0, 12, 5]
#  6x7 [0, 4, 5, 1, 0, 1]
# 123 answer: 5x10 [2, 2, 6, 1, 3] 4x7 [6, 5, 6, 2] 3x15 [14,13,14]
#     6x7
game_posistions = 5 #   !!!idea - base weights on game positions and range
guess_range = 7 # 0 index
# future
answer_setter = 'computer'
guesser = 'computer'  # computer, computer plays itself (for testing and training)
clue_giver = 'computer'          
