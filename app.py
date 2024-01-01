from helper import helper
from db_operations import db_operations
import os

#create connection path to playlist database, create clean data from songs.csv
db_ops = db_operations("playlist.db")
data = helper.data_cleaner("songs.csv")

#start screen of code
def startScreen():
    print("Welcome to your playlist!")

#returns if songs table has any records
def is_empty():
    query = '''
    SELECT COUNT(*)
    FROM songs;
    '''
    result = db_ops.single_record(query)
    return result == 0

#fills table from songs.csv if it's empty
def pre_process():
    if is_empty():
        attribute_count = len(data[0])
        placeholders = ("?,"*attribute_count)[:-1]
        query = "INSERT INTO songs VALUES("+placeholders+")"
        db_ops.bulk_insert(query, data)

#show user menu options
def options():
    print('''Select from the following menu options: 
    1. Find songs by artist
    2. Find songs by genre
    3. Find songs by feature
    4. Upload More Songs
    5. Edit Song Attribute
    6. Delete Song
    7. Exit''')
    return helper.get_choice([1,2,3,4,5,6,7])

#search the songs table by artist
def search_by_artist():
    #get list of all artists in table
    query = '''
    SELECT DISTINCT Artist
    FROM songs;
    '''
    print("Artists in playlist: ")
    artists = db_ops.single_attribute(query)

    #show all artists, create dictionary of options, and let user choose
    choices = {}
    for i in range(len(artists)):
        print(i, artists[i])
        choices[i] = artists[i]
    index = helper.get_choice(choices.keys())

    #user can ask to see 1, 5, or all songs
    print("How many songs do you want returned for", choices[index]+"?")
    print("Enter 1, 5, or 0 for all songs")
    num = helper.get_choice([1,5,0])

    #print results
    query = '''SELECT DISTINCT name
    FROM songs
    WHERE Artist =:artist ORDER BY RANDOM()
    '''
    dictionary = {"artist":choices[index]}
    if num != 0:
        query +="LIMIT:lim"
        dictionary["lim"] = num
    results = db_ops.name_placeholder_query(query, dictionary)
    helper.pretty_print(results)

#search songs by genre
def search_by_genre():
    #get list of genres
    query = '''
    SELECT DISTINCT Genre
    FROM songs;
    '''
    print("Genres in playlist:")
    genres = db_ops.single_attribute(query)

    #show genres in table and create dictionary
    choices = {}
    for i in range(len(genres)):
        print(i, genres[i])
        choices[i] = genres[i]
    index = helper.get_choice(choices.keys())

    #user can ask to see 1, 5, or all songs
    print("How many songs do you want returned for", choices[index]+"?")
    print("Enter 1, 5, or 0 for all songs")
    num = helper.get_choice([1,5,0])

    #print results
    query = '''SELECT DISTINCT name
    FROM songs
    WHERE Genre =:genre ORDER BY RANDOM()
    '''
    dictionary = {"genre":choices[index]}
    if num != 0:
        query +="LIMIT:lim"
        dictionary["lim"] = num
    results = db_ops.name_placeholder_query(query, dictionary)
    helper.pretty_print(results)

#search songs table by features
def search_by_feature():
    #features we want to search by
    features = ['Danceability', 'Liveness', 'Loudness']
    choices = {}

    #show features in table and create dictionary
    choices = {}
    for i in range(len(features)):
        print(i, features[i])
        choices[i] = features[i]
    index = helper.get_choice(choices.keys())

    #user can ask to see 1, 5, or all songs
    print("How many songs do you want returned for", choices[index]+"?")
    print("Enter 1, 5, or 0 for all songs")
    num = helper.get_choice([1,5,0])

    #what order does the user want this returned in?
    print("Do you want results sorted in asc or desc order?")
    order = input("ASC or DESC: ")

    #print results
    query = "SELECT DISTINCT name FROM songs ORDER BY "+choices[index]+" "+order
    dictionary = {}
    if num != 0:
        query +=" LIMIT:lim"
        dictionary["lim"] = num
    results = db_ops.name_placeholder_query(query, dictionary)
    helper.pretty_print(results)

def song_exists(song_id):
    query = "SELECT COUNT(*) FROM songs WHERE songID = ?"
    result = db_ops.single_param_attribute(query, (song_id,))
    return result == 1

def songName_exists(song_Name):
    query = "SELECT COUNT(*) FROM songs WHERE Name = ?"
    result = db_ops.single_param_attribute(query, (song_Name,))
    return result == 1

def upload_songs(): #Inserts all songs from inputed csv file unless the song already exists
    newDataName = input("What is the name of the file you are trying to load?: ")
    if not os.path.isfile(newDataName):
        print("Error: The file " + newDataName + " does not exist.")
        return
    newdata = helper.data_cleaner(newDataName)
    attribute_count = len(newdata[0])
    placeholders = ("?," * attribute_count)[:-1]
    query = "INSERT INTO songs VALUES(" + placeholders + ")"

    for song_data in newdata:
        song_id = song_data[0]
        if not song_exists(song_id):
            db_ops.bulk_insert(query, [song_data])
        else:
            print("Song with ID",song_id, "already exists and will not be inserted.")

def change_attribute(): # Allows user to choose specific songs they want to change a specific attribute for
    songName = input("What song would you like to edit?: ")
    if not songName_exists(songName):
        print("That song is not in you playist")
        return
    query = '''SELECT *
    FROM songs
    WHERE Name = ?;'''
    result = db_ops.single_param_record(query, (songName,))
    print("Here are the attributes you may edit:")
    print("1: Song Name:", result[1])
    print("2: Artist Name:", result[2])
    print("3: Album Name:", result[3])
    print("4: Release Date:", result[4])
    print("5: Explicit:", result[6])
    edit = input("Which would you like to edit?: ")
    if edit == "1":
        newSongName = input("What would you like your new song name to be?: ")
        query = '''UPDATE songs
        SET Name = ?
        WHERE Name = ?'''
        result2 = db_ops.edit_query(query, (newSongName, songName))
        print(songName, "updated to:", newSongName)
    elif edit == "2":
        newArtistName = input("What would you like your new Artist name to be?: ")
        query = '''UPDATE songs
        SET Artist = ?
        WHERE Name = ?'''
        result2 = db_ops.edit_query(query, (newArtistName, songName))
        print(result[2], "updated to:", newArtistName)
    elif edit == "3":
        newAlbumName = input("What would you like your new Album name to be?: ")
        query = '''UPDATE songs
        SET Album = ?
        WHERE Name = ?'''
        result2 = db_ops.edit_query(query, (newAlbumName, songName))
        print(result[3], "updated to:", newAlbumName)
    elif edit == "4":
        newreleaseYear = input("What year would you like your new release data to have?: ")
        newreleaseMonth = input("What month would you like your new release data to have?: ")
        newreleaseDay = input("What Day would you like your new release data to have?: ")
        newreleaseDate = newreleaseYear + "-" + newreleaseMonth + "-" + newreleaseDay
        query = '''UPDATE songs
        SET releaseDate = ?
        WHERE Name = ?'''
        result2 = db_ops.edit_query(query, (newreleaseDate, songName))
        print(result[4], "updated to:", newreleaseDate)
    elif edit == "5":
        newExplicit = "False"
        if result[6] == "False":
            newExplicit = "True"
        query = '''UPDATE songs
        SET Explicit = ?
        WHERE Name = ?'''
        result2 = db_ops.edit_query(query, (newExplicit, songName))
        print("The Explicit Rating of", songName, "is now", newExplicit)
    else:
        print("You did not choose a valid option")

def delete_song(): # Allows user to delete any song that is currently in the playlist
    songDelete = input("What is the name of the song you would like to delete? ")
    if not songName_exists(songDelete):
        print("That song is not in you playist")
        return
    query = '''DELETE FROM songs
        WHERE Name = ?'''
    db_ops.edit_query(query,(songDelete,))
    print(songDelete, "has been deleted from your playlist")




    


#main program
startScreen()
pre_process()

#main program loop
while True:
    user_choice = options()
    if user_choice == 1:
        search_by_artist()
    if user_choice == 2:
        search_by_genre()
    if user_choice == 3:
        search_by_feature()
    if user_choice == 4:
        upload_songs()
    if user_choice == 5:
        change_attribute()
    if user_choice == 6:
        delete_song()
    if user_choice == 7:
        print("Goodbye!")
        break

db_ops.destructor()



