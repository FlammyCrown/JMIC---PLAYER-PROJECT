from tkinter import*
from tkinter import ttk, filedialog, messagebox
from pygame import mixer
import customtkinter
from PIL import Image, ImageTk
import os
import requests, time, random, io, pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

main_screen = Tk()
main_screen.title("JMIC Player")

# Get the screen width and height
screen_width = main_screen.winfo_screenwidth()
screen_height = main_screen.winfo_screenheight()

# Calculate the window size relative to the screen
window_width = int(screen_width * 0.5)  # 80% of screen width
window_height = int(screen_height * 0.65)  # 60% of screen height

# Calculate the window position relative to the screen
x_pos = int((screen_width - window_width) / 2)  # Center horizontally
y_pos = int((screen_height - window_height) / 2)  # Center vertically

# Set window size and position
main_screen.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

main_screen.configure(bg="white")
main_screen.resizable(False, False)


"""Quincy"""
# Initialize pygame Mixer
mixer.init()

# Define the directory path
music_directory = os.path.join(os.path.expanduser('~'), 'Music')
stopped = False
repeat_enabled = False

# Grab Song Length Time Info
def update_progress_bar_with_time():
    global stopped
    if stopped:
        return 

    current_time = mixer.music.get_pos() / 1000 
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

    song = playlist_box.get(ACTIVE)
    song_path = os.path.join(music_directory, f"{song}.mp3")
    song_mut = MP3(song_path)
    global song_length
    song_length = song_mut.info.length
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

    current_time += 1
    
    if int(my_slider.get()) == int(song_length):
        time_status_bar.config(text=f'{converted_song_length}  of  {converted_song_length}  ')
    elif paused:
        pass
    elif int(my_slider.get()) == int(current_time):
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(current_time))
    else:
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(my_slider.get()))
        converted_current_time = time.strftime('%M:%S', time.gmtime(int(my_slider.get())))
        time_status_bar1.config(text=f'{converted_current_time}')
        time_status_bar.config(text=f'{converted_song_length}')

        next_time = int(my_slider.get()) + 1
        my_slider.config(value=next_time)

    if repeat_enabled and int(my_slider.get()) >= int(song_length):
        # If repeat is enabled and the slider position is greater than or equal to the song length,
        # it means the song has finished playing, so reset the slider to 0
        my_slider.set(0)

    time_status_bar.after(1000, update_progress_bar_with_time)


# Add Song Function
def add_songs_from_folder():
    try:
        folder_path = filedialog.askdirectory(initialdir='audio/', title="Choose A Folder")
        if folder_path:
            # List of supported file extensions
            supported_extensions = (".mp3", ".wav", ".m4a", ".flac", ".wma", ".aac", ".opus", ".raw", ".webm")
            
            # Get all files in the folder with supported extensions
            songs = [file for file in os.listdir(folder_path) if os.path.splitext(file)[1].lower() in supported_extensions]
            
            # Add each song to the playlist
            for song in songs:
                song = os.path.splitext(song)[0]  # Remove the file extension
                playlist_box.insert(END, song)
        update_progress_bar_with_time()
        playallsong()
    except() as e:
        pass


# Add many songs to playlist
def add_selected_songs():
    songs = filedialog.askopenfilenames(initialdir='audio/', title="Choose Songs", filetypes=(
        ("MP3 Files", "*.mp3"),
        ("WAV Files", "*.wav"),
        ("M4A Files", "*.m4a"),
        ("FLAC Files", "*.flac"),
        ("WMA Files", "*.wma"),
        ("AAC Files", "*.aac"),
        ("OPUS Files", "*.opus"),
        ("RAW Files", "*.raw"),
        ("WEBM Files", "*.webm")
    ))
    
    # Add each selected song to the playlist
    for song in songs:
        song = os.path.basename(song)
        song = os.path.splitext(song)[0]  # Remove the file extension
        playlist_box.insert(END, song)


def show_add():
    add_song_menu.post(add_song_button.winfo_rootx(), add_song_button.winfo_rooty() + add_song_button.winfo_height())


# Define the playallsong function
def playallsong():
    global paused
    global stopped
    global interrupted_index
    
    # Check if there are songs in the playlist
    if playlist_box.size() > 0:
        # Reset the paused and stopped flags
        paused = False
        stopped = False
        # Reset the interrupted index
        interrupted_index = None
        
        # Iterate over the playlist and play each song
        for i in range(playlist_box.size()):
            # Select the current song from the playlist
            playlist_box.selection_clear(0, END)  # Clear current selection
            playlist_box.selection_set(i)  # Set selection to current index
            playlist_box.activate(i)  # Activate (highlight) current index
            playlist_box.see(i)  # Scroll to make the current index visible
            
            time_status_bar.config(text='')
            my_slider.config(value=0)
            # Play the current song
            play()
            
            # Check if music is playing
            while mixer.music.get_busy():
                main_screen.update()
                time.sleep(0.1)
                
            # Check if the play button was clicked to pause playback
            if paused or stopped:
                # If paused or stopped, break the loop
                break

        # Reset interrupted index when all songs have been played
        interrupted_index = None
    else:
        print("No songs in the playlist.")


"""Crown"""
# Play selected song
def play(event=None):
    global stopped
    if playlist_box.size() == 0:
        messagebox.showinfo("Empty Playlist", "The playlist is empty.")
    else:
        if len(playlist_box.curselection()) == 0:
            # If no song is selected, highlight the first song
            playlist_box.selection_set(0)
        # Set Stopped Variable To False So Song Can Play
        stopped = False
        song = playlist_box.get(ACTIVE)
        music.config(text=song)
        song = os.path.join(music_directory, f"{song}.mp3")
        mixer.music.load(song)
        mixer.music.play(loops=0)


        # Set looping behavior
        if repeat_enabled:
            time_status_bar.config(text='')
            my_slider.config(value=0)
            mixer.music.play(loops=-1)  # Loop indefinitely
        else:
            mixer.music.play(loops=0)   # Do not loop
            time_status_bar.config(text='')
            my_slider.config(value=0)
            
        # Call the update_progress_bar_with_time function to get song length
        update_progress_bar_with_time()
        display_album_cover(song)
        show_lyrics()  # Call show_lyrics to display lyrics for the currently playing song


# Create Global Pause Variable
global paused
paused = False
# Pause and Unpause The Current Song
def pause(is_paused):
    global paused
    paused = is_paused
    if paused:
        mixer.music.unpause()
        paused = False
    else:
        mixer.music.pause()
        paused = True


# Stop playing current song
def stop():
    time_status_bar.config(text='')
    my_slider.config(value=0)
    mixer.music.stop()
    playlist_box.selection_clear(ACTIVE)
    global stopped
    stopped = True 


# Play The Next Song in the playlist
def next_song():
    try:
        time_status_bar.config(text='')
        my_slider.config(value=0)
        next_one = playlist_box.curselection() 
        next_one = next_one[0]+1
        song = playlist_box.get(next_one)
        music.config(text=song)
        song_path = os.path.join(music_directory, f"{song}.mp3")
        mixer.music.load(song_path)
        mixer.music.play(loops=0)
        playlist_box.selection_clear(0, END)
        playlist_box.activate(next_one)
        playlist_box.selection_set(next_one, last=None)
        play()  # Call play function to update UI
    except(IndexError):
        pass
    except pygame.error as e:
         if "No such file or directory" in str(e):
              pass

# Play Previous Song In Playlist
def previous_song():
    try:
        time_status_bar.config(text='')
        my_slider.config(value=0)
        next_one = playlist_box.curselection() 
        next_one = next_one[0]-1
        song = playlist_box.get(next_one)
        music.config(text=song)
        song_path = os.path.join(music_directory, f"{song}.mp3")
        mixer.music.load(song_path)
        mixer.music.play(loops=0)
        playlist_box.selection_clear(0, END)
        playlist_box.activate(next_one)
        playlist_box.selection_set(next_one, last=None)
        play()  # Call play function to update UI
    except(IndexError):
        pass
    except pygame.error as e:
         if "No such file or directory" in str(e):
              pass

"""Ifeanyi"""
def delete_song():
    ...


def delete_all_songs():
    ...


def toggle_repeat():
    ...


def shuffle_playlist():
    ...

def update_volume_and_label(x):
    pass



"""Quincy"""
def display_album_cover(song_name):
    ...


def get_default_image():
    ...


def fetch_lyrics():
    ...


def show_lyrics():
    ...


def slide():
    ...


"""MR CROWN"""
"""
On Blue : Crown
1. Add and Minus(remove) Menu
2. Playlist frame
3. Playlist list box
4. Playlist title "Song playlist"
5. Playlist Menu "Remove Songs" which will contain "Delete song from playlist" and "Delete all songs from playlist"
6. Scroll bar horizontal
"""
#Playlist Frame and title_label
playlist_frame = Frame(main_screen, bd=2, relief=RIDGE)
playlist_frame.place(x=15, y=0, width=250, height=400)

playlist_title = Label(playlist_frame, text="Songs Playlist", font=("Helvetica", 10, "bold"))
playlist_title.pack( anchor="w")

# Create menu
my_menu = Menu(main_screen)
main_screen.config(menu=my_menu)


# Create the Add Songs menu
add_song_menu = Menu(playlist_frame, tearoff=0)
add_song_menu.add_command(label="Add Songs From Folder", command=add_songs_from_folder)
add_song_menu.add_command(label="Pick Out Tracks", command=add_selected_songs)

# Create a Menubutton to display the Remove Songs menu
add_song_button = Menubutton(text="+", font=("ariel", 15, "bold"), fg="black", borderwidth=-5, menu=add_song_menu)
add_song_button.place(x=200, y=3)
add_song_button.bind("<Button-1>", lambda event: show_add())   # Bind the show_remove function to the button click event

# Create the Remove Songs menu
remove_song_menu = Menu(playlist_frame, tearoff=0)
remove_song_menu.add_command(label="Delete Selected Song", command=delete_song)
remove_song_menu.add_command(label="Delete All Songs", command=delete_all_songs)

# Create a Menubutton to display the Remove Songs menu
remove_songs_button = Menubutton(text="~", font=("ariel", 15, "bold"), fg="black", borderwidth=-5, menu=remove_song_menu)
remove_songs_button.place(x=235, y=3)
remove_songs_button.bind("<Button-1>", lambda event: show_remove())   # Bind the show_remove function to the button click event

# Create Playlist Box
#Playlist Scroll Bar
scroll = Scrollbar(playlist_frame)
playlist_box = Listbox(playlist_frame, width=100, font= ("ariel", 10), bg="#D7D4D9", fg="black", selectbackground="lightblue", cursor="hand2", bd=0, yscrollcommand=scroll.set)
scroll.config(command=playlist_box.yview)
scroll.pack(side=RIGHT, fill=Y)
playlist_box.pack(side=LEFT, fill=BOTH)
playlist_box.bind("<Double-1>", lambda event: play()) # Bind double-click event to the playlist

"""MR IFEANYI"""
"""
On Red : Ifeanyi
1. Music frame
2. Music notebook containing "Music_cover" and "Lyrics"
3. Music welcome label
"""
#Notebook Creation for widget
music_diplay = ttk.Notebook(main_screen) #Widgets or Notebooks
music_diplay.place(x=275, y=0, width=400, height=400)


music_img = PhotoImage(file="music_thumbnails/istockphoto-1192064761-612x612.png", width=400, height=400)
music_thumbnail_widget = Label(music_diplay, image=music_img)    #widgets 1  

lyrics_widget = Text(music_diplay, bg="lightblue", fg="black", font=("Arial", 10), wrap="word", width=400, height=400)#widgets 2

music_diplay.add(music_thumbnail_widget, text="Music")
music_diplay.add(lyrics_widget, text="lyrics")

music_display_title = Label(music_diplay, bg="#D7D4D9", text="Welcome to JMIC-Player", font=("Helvetica", 10, "bold"))
music_display_title.pack(pady=0, anchor="e")

lyrics_widget.insert(END, "Lyrics will be displayed here...")
lyrics_widget.config(state=DISABLED)

#Lyrics Scroll Bar
lyrics_scrollbar = Scrollbar(lyrics_widget, orient="vertical", command=lyrics_widget.yview)
lyrics_widget.config(yscrollcommand=lyrics_scrollbar.set)
lyrics_scrollbar.pack(side="right",fill="y")



"""MR QUINCY"""
"""
On Black : Quincy
1. Music label
2. Progress bar slider
3. Music time status
4. Shuffle button
5. Previous button
6. Pause button
7. Play button
8. Stop button
9. Next Button
10. Repeat button
11. Volume label
12. Volume slider
"""
#icon
image_icon = PhotoImage(file="images/logo.png") #this is for the top logo close to JMIC - Player
main_screen.iconphoto(False, image_icon)

#Button
shuffle = PhotoImage(file="images/40x26/shuffle.png", width=40, height=26)
Button(main_screen, text="", compound=LEFT, image=shuffle, fg= "white", bg="white", bd=0, font=("ariel", 10, "bold"), command=shuffle_playlist).place(x=235, y=465)

previous_button = PhotoImage(file="images/40x40/previous.png", width=20, height=20)
Button(main_screen, text="", compound=LEFT, image=previous_button, bd=0, fg= "white", bg="white", command=previous_song).place(x=260, y=460)

pause_button = PhotoImage(file="images/40x40/pause.png", width=20, height=20)
Button(main_screen, text="", compound=LEFT, image=pause_button, bd=0, fg= "white", bg="white", command=lambda: pause(paused)).place(x=290, y=460)

play_button = PhotoImage(file="images/40x40/play.png", width=40, height=40)
Button(main_screen, text="", compound=LEFT, image=play_button, bd=0, fg= "white", bg="white", command=play).place(x=320, y=450)

stop_button = PhotoImage(file="images/40x40/stop.png", width=20, height=20)
Button(main_screen, text="", compound=LEFT, image=stop_button, bd=0, fg= "white", bg="white", command=stop).place(x=370, y=460)

next_button = PhotoImage(file="images/40x40/next.png", width=20, height=20)
Button(main_screen, text="", compound=LEFT, image=next_button, bd=0, fg= "white", bg="white", command=next_song).place(x=400, y=460)

repeat_img = PhotoImage(file="images/40x26/repeat.png", width=40, height=23)
repeat = Button(main_screen, text="", bg="white", bd=0, image=repeat_img, compound=LEFT, fg= "white", font=("ariel", 10, "bold"), command=toggle_repeat)
repeat.place(x=430, y=465)

#Label of Music being played
music_frame = Frame(main_screen, width=250, height=15, bd=4, bg="white").place(x=15, y=408)
music = Label(music_frame, text="Current playing song", font=("ariel", 10), fg="Black", bg="white", wraplength=250)
music.place(x=15, y=408)

# Create Time Status Bar
time_status_bar = Label(main_screen, text='00:00', bd=1, relief=GROOVE, anchor=E)
time_status_bar.place(x=660, y=420, anchor="center")

time_status_bar1 = Label(main_screen, text='00:00', bd=1, relief=GROOVE, anchor=E)
time_status_bar1.place(x=290, y=420, anchor="center")

#Volume nub
volume_slider = customtkinter.CTkSlider(master=main_screen, from_=0, to=100, command=lambda value: [update_volume_and_label(value)], width=100, number_of_steps=100)
volume_slider.place(x=582, y=460)

volume_label = Label(main_screen, text="Volume: 100", font=("Helvetica", 7, "bold"), fg="black", bg="white")
volume_label.place(x=602, y=475)


# Create Music Position Slider
my_slider = ttk.Scale(main_screen, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length=320, style="TScale")
my_slider.place(x=315, y=413)
# Create a style object
style = ttk.Style()
style.theme_use("clam")

# Set the background color (left side) of the scale widget
style.configure("TScale", troughcolor="light blue", background="blue", 
                highlightcolor="sea green", slidercolor=[("active", "light green")], 
                gripcount=0, bordercolor="light blue", relief="flat", sliderthickness = 15)



main_screen.mainloop()