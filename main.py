from fastapi import FastAPI, HTTPException
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

def dict_factory_list (cursor, row):
    my_string = row [0]
    return my_string
    

@app.get ('/tracks')
async def get_tracks (page:int = 0, per_page:int = 10):
    app.db_connection.row_factory = dict_factory
    cursor = app.db_connection.cursor ()
    data = cursor.execute ('''
    SELECT * FROM tracks LIMIT ? OFFSET ?''', [per_page, page]).fetchall ()
    return data

@app.get ('/tracks/album')
async def get_names_of_album (album_id:int):
    app.db_connection.row_factory = dict_factory
    cursor = app.db_connection.cursor ()
    data = cursor.execute ('''SELECT Name FROM tracks WHERE AlbumId = ?''', [album_id]).fetchall ()
    return data

@app.get ('/tracks/composers')
async def get_titles_of_composer (composer_name):
    app.db_connection.row_factory = dict_factory_list
    cursor = app.db_connection.cursor ()
    data = cursor.execute ('''SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name''', [composer_name]).fetchall ()

    if len (data) == 0:
        raise HTTPException (status_code = 404)

    return data
