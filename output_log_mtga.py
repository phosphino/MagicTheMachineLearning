import os, re
import pandas as pd
from arena_database import arena_db
import numpy as np
import ast

#MTG Arena output log path
path = r"C:\Users\breuh\AppData\LocalLow\Wizards Of The Coast\MTGA"

datapath = os.path.join(path, 'output_log.txt')


class personal_collection(arena_db):
    def __init__(self, path = datapath):
        super(personal_collection, self).__init__()
        with open(path, 'r') as f:
            lines = f.readlines()
        f.close()
        self._personaldb = self.load_completecollection(lines)

    def get_Collection(self):
        return self._personaldb

    def Remove_Duplicates(self, db):
        duplicates = db[db.duplicated(subset='card_name')]
        keep = db[~db.duplicated(subset='card_name')]
        duplicate_data = duplicates[['card_name','quantity']]

        for index, row in duplicate_data.iterrows():
            keep_index = keep[keep.card_name == row.card_name].index.item()
            keep.at[keep_index, 'quantity'] += row['quantity']

        return keep

    def load_completecollection(self, lines):
        card_id= []
        quantity = []
        sentinal = True
        count = 0
        for line in lines:
            if "<== PlayerInventory.GetPlayerCardsV3" in line:
                sentinal = False
                count += 1
            if "}" in line and sentinal is False:
                sentinal = True
            if sentinal:
                continue
            id_result = re.search(r"\"(.*)\"", line)
            quantity_result = re.search(r": (\d{1})", line)
            if id_result and quantity_result and count == 1:
                card_id.append(int(id_result.group(1)))
                quantity.append(int(quantity_result.group(1)))
        collectionlog_dict = {'arena_id':card_id, 'quantity':quantity}
        log_collection_db = pd.DataFrame(collectionlog_dict)
        Arena_allcards = self.arena_db

        #Extracts the rows from the arena card database that correspond to cards i have by merging on the arena ids
        personal_collection = pd.merge(log_collection_db, Arena_allcards, how='inner', on=['arena_id'])

        return personal_collection.reset_index(drop=True)




