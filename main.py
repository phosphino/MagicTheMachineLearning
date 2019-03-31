from DeckBuilder import *
from arena_database import *
from output_log_mtga import *




def GA_main(popsize, generations, elitesize, mutationrate):
    collection = personal_collection()
    no_mana = collection.Remove_Lands(collection.get_Collection())
    GA_ready_collection = collection.Remove_Duplicates(no_mana)

    #Initialize population
    currentpop = initialize_population(popsize, GA_ready_collection)

    complete_collection = collection.arena_db
    complete_collection_noLands = collection.Remove_Lands(complete_collection)
    fitness = Fitness(complete_collection_noLands)

    best_deck = RankPop(currentpop, fitness)[0]


    #Each generation is formed in steps.
    for generation in range(generations):
        print("BEGIN GENERATION: {}".format(generation))
        #Rank the current population
        ranked_currentpop = RankPop(currentpop, fitness)
        if ranked_currentpop[0][1] >= best_deck[1]:
            best_deck = ranked_currentpop[0]
        print("--------------")
        print("SCORE:", best_deck[1])

        #Using the ranks, form a mating pool
        matingpool = select_pool(elitesize, ranked_currentpop)

        #Breed the mating pool to create child decks
        new_population = breed_population(matingpool, elitesize, GA_ready_collection)

        #Mutate the child decks to prevent local minima
        currentpop = mutate_population(new_population,GA_ready_collection, mutationrate)

    return best_deck[0]


deck = GA_main(30, 50, 4, 0.05)
decklist = deck.get_decklist()
print(decklist[['card_name','color_identity']])
print(deck.get_colors(deck.get_decklist()))



