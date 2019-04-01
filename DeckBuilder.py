from arena_database import arena_db
from output_log_mtga import personal_collection
import pandas as pd
import random, re
import numpy as np
import matplotlib.pyplot as plt

'''
https://towardsdatascience.com/evolution-of-a-salesman-a-complete-genetic-algorithm-tutorial-for-python-6fe5d2b3ca35
^repurposed this to implement genetic algorithm in python for mtg arena deckbuilder
'''


class Deck:
    def __init__(self, collection, n=36, make_deck=True):
        self._decklist = None
        if make_deck:
            self._decklist = self.create_newdeck(n, collection)



    def create_newdeck(self, n, collection):
        decklist = None
        #Check for duplicates which exceed collection quantity or 4.
        sentinal = True
        while sentinal:
            decklist = collection.sample(n=n, replace=True, weights=collection['quantity'], axis=0)

            #get cards which are used more than once in the deck
            duplicates = decklist[decklist[['card_name','quantity']].duplicated()]
            names = set(duplicates['card_name'].values.tolist())
            if len(names) == 0:
                sentinal=False
                continue

            for name in names:
                sentinal=False
                card = decklist[decklist['card_name'] == name]
                numberused = card.shape[0]
                if numberused > min(card.quantity.iloc[0], 4):
                    sentinal=True
        return decklist.reset_index(drop=True)

    def get_colors(self, decklist):
        colors = {'colorless': 0, 'B': 0, 'R': 0, 'W': 0, 'U': 0, 'G': 0}
        for card in decklist['color_identity'].items():
            #card is tuple (index, color list)
            card = card[1]
            for c in card:
                colors[c] += 1
            if len(card) == 0:
                colors['colorless'] += 1
        return colors



    def get_decklist(self):
        return self._decklist

    def set_decklist(self, decklist):
        self._decklist = decklist


class Fitness:
    def __init__(self, collection):
        self._collection = collection
        training_decks = self.import_decks(collection)
        self._cardtable = self.build_card_table(training_decks)

    def score_deck(self, deck):
        neightbor_score = self.neighbor_score(deck)
        color_score = self.color_score(deck)
        return neightbor_score + color_score


    def neighbor_score(self, deck):

        decklist = deck.get_decklist()
        card_list=set(decklist['card_name'].values.tolist())
        deck_score = []

        relevant_table = self._cardtable[self._cardtable.index.isin(list(card_list))]

        if relevant_table.empty:
            return 0

        for card in card_list:
            ind_card = decklist[decklist['card_name']==card]
            indcard_quantity = ind_card.shape[0]
            ind_card_maxquantity = ind_card.iloc[0]['quantity']
            if indcard_quantity > ind_card_maxquantity:
                return 0



        for card in card_list:
            try:
                neighbor_table = relevant_table.loc[card]
            except KeyError:
                continue
            neighbor_table = neighbor_table[neighbor_table.index.isin(card_list)]
            duplicate_score = decklist[decklist['card_name'] == card].shape[0]
            deck_score.append(neighbor_table.sum()**duplicate_score)

        return(sum(deck_score))

    def color_score(self, deck):
        decklist = deck.get_decklist()
        colors = deck.get_colors(decklist)
        color_vector = []
        del colors['colorless']
        for key, value in colors.items():
            color_vector.append(value)
        color_vector = sorted(color_vector, reverse=True)
        colorscore = 0
        for i in range(2,5):
            colorscore+=color_vector[i]
        return -1 * colorscore


    def build_card_table(self, decks):
        cards = set()

        for deck in decks:
            for ind_card in deck['card_name'].values.tolist():
                cards.add(ind_card)
        card_table = pd.DataFrame(columns=cards, index=cards)
        card_table[:] = 0

        for deck in decks:
            card_list = deck['card_name'].values.tolist()
            for card in card_list:
                for index, row in deck.iterrows():
                    neighbor_card = row['card_name']
                    neighbor_quantity = int(row['quantity'])
                    if neighbor_card is card:
                        neighbor_quantity -= 1
                    card_table.at[card, neighbor_card] += neighbor_quantity

        return card_table.div(card_table.max(axis = 0), axis=1)

    def Remove_Duplicates(self, db):
        duplicates = db[db.duplicated(subset='card_name')]
        keep = db[~db.duplicated(subset='card_name')]
        duplicate_data = duplicates[['card_name','quantity']]

        for index, row in duplicate_data.iterrows():
            keep_index = keep[keep.card_name == row.card_name].index.item()
            keep.at[keep_index, 'quantity'] += row['quantity']

        return keep

    def import_decks(self, collection, path=r'test_deck.txt'):
        with open(path, 'r') as f:
            lines = f.readlines()
        f.close()
        decks = []

        deck_quantity = []
        deck_card = []
        deck_set = []
        deck_code = []

        for line in lines:
            quantity = re.search(r"^\d{1,2}", line)
            card_name = re.search(r"\d+ ((.)*) \(", line)
            set_code = re.search(r"\((\w{3})\)", line)
            collector_code = re.search(r"\d{1,4}$", line)

            if [quantity, card_name, set_code, collector_code] == [None] * 4:
                deck = collection[collection['card_name'].isin(deck_card)]
                deck = deck[deck['collector_number'].isin(deck_code)]
                deck = pd.merge(deck, pd.DataFrame(data={'card_name': deck_card, 'quantity': deck_quantity}),
                                on='card_name')


                deck_quantity = []
                deck_card = []
                deck_set = []
                deck_code = []
                self.Remove_Duplicates(deck)
                decks.append(deck)
                continue

            deck_quantity.append(quantity.group(0))
            deck_card.append(card_name.group(1))
            deck_set.append(set_code.group(1))
            deck_code.append(collector_code.group(0))

        return decks

def initialize_population(n, collection):
    deck_pop = []
    for i in range(n):
        deck = Deck(collection)
        deck_pop.append(deck)

    return deck_pop

#Takes ranked decks (deck, fitness score) and returns decks selected for mating.
#Returns list of Decks()
def select_pool(elitesize,  rankedPop, Best_Deck):
    results = []
    scores = pd.DataFrame(data=rankedPop, columns=['deck','fitness'])
    scores['cum_sum'] = scores['fitness'].cumsum()
    scores['cum_perc'] = 100 * scores['cum_sum'] / scores['fitness'].sum()

    results.append(Best_Deck)

    for i in range(elitesize):
        results.append(rankedPop[i][0])

    for i in range(len(rankedPop)-elitesize-1):
        pick = 100 * random.random()
        for i in range(len(rankedPop)):
            if pick <= scores.iat[i,3]:
                results.append(rankedPop[i][0])
                break

    #Returns only decks
    return results

def breed_population(matingpool, elitesize, collection):
    children = []
    length = len(matingpool) - elitesize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(elitesize):
        children.append(matingpool[i])
    for ii in range(length):
        child = breed(pool[ii], pool[len(matingpool) - ii - 1])
        #Turn the child decklist into a deck
        new_deck = Deck(collection, make_deck=False)
        new_deck.set_decklist(child)
        children.append(new_deck)

    #returns list of Decks
    return children

#Passes in two separate parent Decks, returns a single child decklist
def breed(P1, P2):

    P1decklist = P1.get_decklist()
    P2decklist = P2.get_decklist()

    P1decklist_aslist = P1decklist['card_name'].values.tolist()
    P2decklist_aslist = P2decklist['card_name'].values.tolist()

    geneA = int(random.random() * len(P1decklist_aslist))
    geneB = int(random.random() * len(P2decklist_aslist))

    size = P1decklist.shape[0]

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    return pd.concat([P1decklist.iloc[0 : startGene], P2decklist.iloc[startGene : endGene], P1decklist.iloc[endGene : size]])

def RankPop(population, fit):
    deck_ranks = []
    for deck in population:
        rank = fit.score_deck(deck)
        deck_ranks.append(rank)
    rankedpop = zip(population, deck_ranks)
    rankedpop = sorted(rankedpop, key=lambda x: x[1], reverse=True)

    #[Deck, Rank]
    return rankedpop

#pass in a deck and returns a mutated decklist
def mutate(ind_deck, collection, mutationrate):
    decklist = ind_deck.get_decklist()
    new_decklist = decklist.copy()
    deck_colors = ind_deck.get_colors(decklist)
    del deck_colors['colorless']
    ranked_deck_colors = deck_colors.items()
    deck_colors = list(deck_colors.keys())

    ranked_deck_colors = sorted(ranked_deck_colors, key=lambda x: x[1], reverse=True)
    del ranked_deck_colors[0:2]

    #To speed up convergance towards to the correct color count
    #Figure out which colors are minority. Discard any card mutations in these colors
    minor_colors = [x[0] for x in ranked_deck_colors]

    old_cards = []
    keep_cards = []
    for index, row in decklist.iterrows():
        if random.random() < mutationrate:
            sentinal = True
            while sentinal:
                new_card = collection.sample(n=1, weights=collection['quantity'], axis=0)
                color = new_card['color_identity'].values.tolist()[0]

                if len(color) is None:
                    if random.random() < .5:
                        continue
                    sentinal = False
                    continue

                if all(elem in deck_colors for elem in color):
                    sentinal = False
                    for c in color:
                        if c in minor_colors:
                            sentinal = True

            old_cards.append(index)
            keep_cards.append(new_card)
    new_decklist = new_decklist[~new_decklist.index.isin(old_cards)]
    keep_cards.append(new_decklist)
    new_decklist = pd.concat(keep_cards, ignore_index=True)
    return new_decklist.copy()


#Pass in list of decks. Return list of mutated decks
def mutate_population(population, collection, mutationrate = 0.02):
    mutated_pop = population.copy()
    for deck in mutated_pop:
        mutated_decklist = mutate(deck, collection, mutationrate)
        deck.set_decklist(mutated_decklist)

    return mutated_pop
