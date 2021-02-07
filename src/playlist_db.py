# playlist_db.py
#
# Handles the writing to and reading from deejay.db
import sqlite3

def sanitize(string) -> str:
    """Basic sanitization of a string until I integrate SQLAlchemy"""
    return '"'+string+'"'

async def save(ctx, playlist_name, playlist):
    try:
        # Sanitize the strings for SQL
        uid = sanitize(ctx.author.id)
        playlist_name = sanitize(playlist_name)

        db = sqlite3.connect('deejay.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT u.user_id FROM users u WHERE u.user_id = {uid}")
        user_id = cursor.fetchone()

        if user_id is None:  # user is not in user table...
            val = (ctx.author.id,)
            cursor.execute('INSERT INTO users(user_id) VALUES(?)', val)  # add new user
            db.commit()
            await ctx.send(f"`{ctx.author.name}` has been added to the database.")

        cursor.execute("""
                        SELECT p.pid
                        FROM playlists p, users u
                        WHERE u.user_id = ?
                        AND u.user_id = p.user_id
                        AND p.name = ?""", (uid, playlist_name))
        pid = cursor.fetchone()

        if pid is None:  # user has no playlist of that name...
            val = (playlist_name, uid)
            cursor.execute('INSERT INTO playlists(name, user_id) VALUES(?,?)', val)  # add playlist
            db.commit()

            cursor.execute("""
                            SELECT p.pid
                            FROM playlists p, users u
                            WHERE u.user_id = ?
                            AND u.user_id = p.user_id
                            AND p.name = ?""", (uid, playlist_name))
            pid = cursor.fetchone()
            await ctx.send(f"`{playlist_name}` has been added to the database.")

        for song in playlist:  # Add each song to songs table if not already there...
            val = (song.title, song.uploader)
            cursor.execute('SELECT song_id FROM songs WHERE title = ? AND artist = ?', val)

            song_id = cursor.fetchone()
            if song_id is None:
                val = (song.title, song.uploader)
                cursor.execute('INSERT INTO songs(title, artist) VALUES(?,?)', val)  # add song to songs table
                db.commit()
                cursor.execute('SELECT song_id FROM songs WHERE title = ? AND artist = ?', val)
                song_id = cursor.fetchone()

            val = (pid[0], song_id[0])
            cursor.execute('INSERT OR IGNORE INTO playlists_songs(pid,song_id) VALUES(?,?)', val)
            db.commit()

    finally:
        print('Save Playlist: closing deejay.db connection')
        db.close()


async def load(ctx, playlist_name):
    try:
        # Sanitize the strings for SQL
        uid = sanitize(ctx.author.id)
        playlist_name = sanitize(playlist_name)

        db = sqlite3.connect('deejay.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT u.user_id FROM users u WHERE u.user_id = {uid}")
        user_id = cursor.fetchone()

        if user_id is None:  # user is not in user table...
            await ctx.send(f"`{ctx.author.name}` not in database. You have not saved any playlists.")
            return

        cursor.execute("""
                            SELECT p.pid
                            FROM playlists p, users u
                            WHERE u.user_id = ?
                            AND u.user_id = p.user_id
                            AND p.name = ?""", (uid, playlist_name))
        pid = cursor.fetchone()

        if pid is None:  # user has no playlist of that name...
            await ctx.send(f"`{playlist_name}` is not in the database.")
            return

        cursor.execute("""
                            SELECT s.title, s.artist
                            FROM playlists_songs p, songs s
                            WHERE p.pid = ?
                            AND p.song_id = s.song_id""", pid)
        songs_info = cursor.fetchall()

        return songs_info

    finally:
        print('Load Playlist: closing deejay.db connection')
        db.close()


async def delete_playlist(ctx, playlist_name) -> bool:
    """Returns true if delete is successful. False otherwise."""
    try:
        # Sanitize the strings for SQL
        uid = sanitize(ctx.author.id)
        playlist_name = sanitize(playlist_name)

        db = sqlite3.connect('deejay.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT u.user_id FROM users u WHERE u.user_id = {uid}")
        user_id = cursor.fetchone()

        if user_id is None:  # user is not in user table...
            await ctx.send(f"`{ctx.author.name}` not in database. You have not saved any playlists.")
            return

        cursor.execute("""
                            SELECT p.pid
                            FROM playlists p, users u
                            WHERE u.user_id = ?
                            AND u.user_id = p.user_id
                            AND p.name = ?""", (uid, playlist_name))
        pid = cursor.fetchone()

        if pid is None:  # user has no playlist of that name...
            await ctx.send(f"`{playlist_name}` is not in the database.")
            return False

        cursor.execute("""
                            DELETE FROM playlists
                            WHERE pid = ?""", pid)
        db.commit()

        cursor.execute("""
                            DELETE FROM playlists_songs
                            WHERE pid = ?""", pid)
        db.commit()

        return True

    finally:
        print('Delete Playlist: closing deejay.db connection')
        db.close()


async def delete_song(ctx, playlist_name, song_name) -> bool:
    """Returns true if delete is successful. False otherwise."""
    try:
        # Sanitize the strings for SQL
        uid = sanitize(ctx.author.id)
        playlist_name = sanitize(playlist_name)

        db = sqlite3.connect('deejay.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT u.user_id FROM users u WHERE u.user_id = {uid}")
        user_id = cursor.fetchone()

        if user_id is None:  # user is not in user table...
            await ctx.send(f"`{ctx.author.name}` not in database. You have not saved any playlists.")
            return

        cursor.execute("""
                            SELECT p.pid
                            FROM playlists p, users u
                            WHERE u.user_id = ?
                            AND u.user_id = p.user_id
                            AND p.name = ?""", (uid, playlist_name))
        pid = cursor.fetchone()

        if pid is None:  # user has no playlist of that name...
            await ctx.send(f"`{playlist_name}` is not in the database.")
            return False

        cursor.execute("""
                            SELECT s.song_id
                            FROM playlists_songs p, songs s
                            WHERE p.pid = ?
                            AND p.song_id = s.song_id
                            AND s.title = ?""", (pid[0], song_name))
        song_id = cursor.fetchone()
        if song_id is None:  # user has no playlist of that name...
            await ctx.send(f"`{song_name}` is not in the playlist `{playlist_name}`.")
            return False

        cursor.execute("""
                            DELETE FROM playlists_songs
                            WHERE pid = ?
                            AND song_id = ?""", (pid[0], song_id[0]))
        db.commit()

        return True

    finally:
        print('Delete Song: closing deejay.db connection')
        db.close()


async def edit_playlist(ctx, old_name, new_name) -> bool:
    """Returns true if edit is successful. False otherwise."""
    try:
        # Sanitize the strings for SQL
        uid = sanitize(ctx.author.id)
        old_name = sanitize(old_name)
        new_name = sanitize(new_name)

        db = sqlite3.connect('deejay.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT u.user_id FROM users u WHERE u.user_id = {uid}")
        user_id = cursor.fetchone()

        if user_id is None:  # user is not in user table...
            await ctx.send(f"`{ctx.author.name}` not in database. You have not saved any playlists.")
            return

        cursor.execute("""
                            SELECT p.pid
                            FROM playlists p, users u
                            WHERE u.user_id = ?
                            AND u.user_id = p.user_id
                            AND p.name = ?""", (uid, old_name))
        pid = cursor.fetchone()

        if pid is None:  # user has no playlist of that name...
            await ctx.send(f"`{old_name}` is not in the database.")
            return False

        cursor.execute("""
                            UPDATE playlists
                            SET name = ?
                            WHERE pid = ?""", (new_name, pid[0]))
        db.commit()

        return True

    finally:
        print('Edit Playlist: closing deejay.db connection')
        db.close()


async def list_playlists(ctx):
    try:
        # Sanitize the strings for SQL
        id = sanitize(ctx.author.id)

        db = sqlite3.connect('deejay.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT u.user_id FROM users u WHERE u.user_id = {uid}")
        user_id = cursor.fetchone()

        if user_id is None:  # user is not in user table...
            await ctx.send(f"`{ctx.author.name}` not in database. You have not saved any playlists.")
            return

        cursor.execute("""
                            SELECT p.name
                            FROM playlists p, users u
                            WHERE u.user_id = ?
                            AND u.user_id = p.user_id""", (uid,))
        playlist_names = cursor.fetchall()

        if playlist_names is None:  # user has no playlist of that name...
            await ctx.send(f"There are no playlists in the database.")
            return

        return playlist_names

    finally:
        print('List Playlists: closing deejay.db connection')
        db.close()
