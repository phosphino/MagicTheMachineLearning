import os, pandas as pd, numpy as np
import re


database_path = os.path.join(os.getcwd(),"CompleteArenaCardlist_condensed.csv")
'''
COLUMNS NAMES OF CompleteArenaCardlist_condensed CSV FILE
['arena_id', 'artist', 'border_color', 'card_faces', 'cmc',
       'collector_number', 'color_identity', 'colors', 'flavor_text', 'layout',
       'loyalty', 'mana_cost', 'card_name', 'object', 'power', 'rarity', 'set',
       'set_name', 'toughness', 'type_line']
'''

class arena_db:
    '''
    Load arena cards. Data from scryfall
    '''
    def __init__(self, path = database_path):
        self._db = pd.read_csv(path)

        #Convert strings back to lists
        self._db['color_identity'] = self._db['color_identity'].apply(self.extract_list)
        self._db['colors'] = self._db['colors'].apply(self.extract_list)
        self._db['mana_cost'] = self._db['mana_cost'].apply(self.extract_list)


    def extract_list(self, stringlist):
        if stringlist is np.NaN:
            return []
        result = re.findall(r"(?<=\')\w", stringlist)
        if result:

            return result

        result = re.findall(r"(?<=\{).", stringlist)
        if result:
            return result
        else:
            return []

    
    def Remove_BasicLands(self, odb):
        return odb[~odb['type_line'].str.contains('Basic Land')].reset_index(drop=True).copy()

    def Remove_Lands(self, odb):
        flip_lands = odb[odb['layout'].str.contains('transform')]
        db = odb[~odb['type_line'].str.contains('Land')]
        db = pd.concat([db, flip_lands], axis=0, sort=True)

        return db.reset_index(drop=True).copy()

    @property
    def arena_db(self):
        return self._db.copy()

