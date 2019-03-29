from arena_database import arena_db
from output_log_mtga import personal_collection
import pandas as pd
import random
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
                card = collection[collection['card_name'] == name]
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


if __name__ == '__main__':
    collection = personal_collection()
    no_mana = collection.Remove_ManaSources(collection.get_Collection())
    GA_ready_collection = collection.Remove_Duplicates(no_mana)

    Deck(GA_ready_collection)


