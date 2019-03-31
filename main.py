from output_log_mtga import *
from DeckBuilder import *
from arena_database import *

def initialize_population(n, collection):
    deck_pop = []
    for i in range(n):
        deck = Deck(collection)
        deck_pop.append(deck)

collection = personal_collection()
no_mana = collection.Remove_Lands(collection.get_Collection())
GA_ready_collection = collection.Remove_Duplicates(no_mana)
initialpop = initialize_population(10, GA_ready_collection)
complete_collection = collection.arena_db
complete_collection_noLands = collection.Remove_Lands(complete_collection)
a = Fitness(complete_collection_noLands)
Deck(GA_ready_collection)

#