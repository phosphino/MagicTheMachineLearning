from arena_database import arena_db
from output_log_mtga import personal_collection
import pandas as pd
import random, re
import numpy as np
import matplotlib.pyplot as plt

class Deck:
    def __init__(self, collection, n=36, make_deck=True):
        self._decklist = None
        if make_deck:
            self._decklist = self.create_newdeck(n, collection)
        print(self.get_colors(self._decklist))




    def create_newdeck(self, n, collection):
        decklist = None
        #Check for duplicates which exceed collection quantity
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
        return decklist

    def get_colors(self, decklist):
        colors = {'colorless': 0, 'B': 0, 'R': 0, 'W': 0, 'U': 0, 'G': 0}
        for card in decklist['color_identity'].items():
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
        training_decks = self.import_decks(collection)
        self._cardtable = self.build_card_table(training_decks)


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

        return card_table

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
