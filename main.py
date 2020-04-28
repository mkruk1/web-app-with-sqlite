from fastapi import FastAPI
import sqlite3

app = FastAPI ()

@app.on_event ('startup')
async def startup ():
    app.db_connection = sqlite3.connect ("chinook.db")

@app.on_event ('shutdown')
async def shutdown ():
    app.db_connection.close ()

def dict_factory (cursor, row):
    dct = {}
    for idx, col in enumerate (cursor.description):
        dct [col [0]] = row [idx]
    return dct;

@app.get ('/tracks')
async def get_tracks (page:int = 0, per_page:int = 10):
    app.db_connection.row_factory = dict_factory
    cursor = app.db_connection.cursor ()
    data = cursor.execute ('''
    SELECT * FROM tracks LIMIT ? OFFSET ?''', [per_page, page]).fetchall ()
    return data

