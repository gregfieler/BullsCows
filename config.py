# weights are update the guess_position_matrix based on clues
bulls_weight = .3
cows_weight = .7
all_factor = .5  
# use debug true to set seed and initial guess for testing
debug = False  # sets answer and starting guess
random_seed = 999 # only used for debug  123 -> 6562   999 -> 0451
autorun = 25  # if not 0 automatically runs in computer mode
game_posistions = 3 #   !!!idea - base weights on game positions and range
guess_range = 7 # 0 index
# future
answer_setter = 'computer'
guesser = 'computer'  # computer, computer plays itself (for testing and training)
clue_giver = 'computer'          
