from arena_database import arena_db

a = arena_db()
nolands = a.arena_db_nolands
print(nolands.head(5))
print(nolands.columns)

