from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import json

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
            SELECT * FROM tracks LIMIT ? OFFSET ?''',
            [per_page, page]).fetchall ()
    return data

@app.get ('/album')
async def get_names_of_album (album_id:int):
    app.db_connection.row_factory = dict_factory
    cursor = app.db_connection.cursor ()
    data = cursor.execute ('''
            SELECT Name FROM tracks WHERE AlbumId = ?''',
            [album_id]).fetchall ()
    return data

@app.get ('/tracks/composers')
async def get_titles_of_composer (composer_name):
    app.db_connection.row_factory = dict_factory_list
    cursor = app.db_connection.cursor ()
    data = cursor.execute ('''
            SELECT Name FROM tracks WHERE
            Composer = ? ORDER BY Name''',
            [composer_name]).fetchall ()

    if len (data) == 0:
        cont = {
            "detail": {
                "error": "there is no such artist"
            }
        }
        return JSONResponse (content = cont, status_code = 404) 

    return data

class Album (BaseModel):
    title: str
    artist_id: int 

@app.post ('/albums')
async def add_album (album: Album):
    my_object = album.dict ()
    cursor = app.db_connection.cursor ()

    if_exists = cursor.execute ('''
            SELECT 1 FROM albums WHERE ArtistId = ?''',
            [my_object ['artist_id']]).fetchall () 

    if len (if_exists) != 0:
        cursor.execute ('''
                INSERT INTO albums (Title, ArtistId) VALUES (?, ?) ''',
                [my_object ['title'], 
                my_object ['artist_id']])
    else:
        cont = {
            "detail": {
                "error": "there is no such artist"
            }
        }
        return JSONResponse (content = cont, status_code = 404) 

    cont = {
            "AlbumId": cursor.lastrowid,
            "Title": my_object ['title'],
            "ArtistId": my_object ['artist_id']
    }
    return JSONResponse (content = cont, status_code = 201) 

@app.get ('/albums/{album_id}')
async def get_album (album_id:int):
    app.db_connection.row_factory = dict_factory
    cursor = app.db_connection.cursor ()
    data = cursor.execute (''' SELECT * FROM albums WHERE AlbumId = ?''',
            [album_id]).fetchall () 

    return data [0]

