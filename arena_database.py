import os, pandas as pd

database_path = os.path.join(os.getcwd(),"CompleteArenaCardlist_condensed.csv")

class arena_db:
    def __init__(self, path = database_path):
        self._db = pd.read_csv(path)

    @property
    def arena_db_nobasiclands(self):
        db = self._db[~self._db['type_line'].str.contains('Basic Land')].reset_index()
        return db.drop(columns='index')

    @property
    def arena_db_nolands(self):
        flip_lands = self._db[self._db['layout'].str.contains('transform')]
        db = self._db[~self._db['type_line'].str.contains('Land')].reset_index()

        return pd.concat([db, flip_lands], axis=0, sort=True)
