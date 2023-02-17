"""Memory Royale V1.1 2021-2023
   (C) Steve Shambles.FREEWARE.
   Code Under MIT Licence.

   Credit must go to code that got me started, with thanks.
   https://github.com/zoenberger/Memory-Game-using-Tkinter

   Requirements:
   -------------
   pip3 install Pillow
   pip3 install soundfile
   pip3 install sounddevice

   Tested and working on 64 bit:
   Windows 7, Windows 10, Linux Mint 19.1
"""
import os
import random
import tkinter as tk
from tkinter import messagebox
import webbrowser as web

from PIL import Image, ImageTk
import sounddevice as sd
import soundfile as sf


root = tk.Tk()
root.title('Memory Royale    Level 1')
root.resizable(False, False)
root.geometry('+550+300')


class Mem():
    """This is instead of using globals, use for example:'Mem.new_card'."""
    logo_frame = None
    new_card = ''
    first_card = ''
    click_count = 0
    found_matches = 0
    total_tries = 0
    match_list = []
    blank_cards = []
    card_images = []
    all_clicks = 0
    target_clicks = 30
    stat_bar = None
    card = None
    num_pairs = 8  # Do not reset.
    level = 1  # Do not reset. max level 3, 4 strips, 16 pairs.

    # cheat: start on level 3
    # level = 3
    # num_pairs = 16
    # target_clicks = 90

    # cheat: start on level 2
    # level = 2
    # num_pairs = 12
    # target_clicks = 60


def play_sound(filename):
    """Play WAV file.Supply filename when calling this function."""
    data, fs = sf.read(filename, dtype='float32')
    sd.play(data, fs)


def updt_status_bar(txt):
    """displays current action in the status bar, text to be displayed
       must be supplied when calling this function."""
    Mem.stat_bar.config(text=txt)
    Mem.stat_bar.update()


def logo():
    """Insert logo image into main window."""
    Mem.logo_frame = tk.Frame(root)
    Mem.logo_frame.grid(row=0, columnspan=8)
    logo_image = Image.open('misc/memory_royale_logo.png')
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(Mem.logo_frame, image=logo_photo)
    logo_label.logo_image = logo_photo
    logo_label.grid(padx=0, pady=0, row=0, column=0)


def complete_game_as_winner():
    """Player has completed all 3 levels within max clicks."""
    play_sound('sfx/game_completed.wav')
    messagebox.showinfo('Winner',
                        'Well done you have completed the game!\n\n'
                        'Now do it again in even less clicks!')
    root.destroy()


def play_start_level_sound():
    """Play a different intro jingle for each level."""
    if Mem.level == 1:
        play_sound('sfx/intro.wav')
    if Mem.level == 2:
        play_sound('sfx/level2intro.wav')
    if Mem.level == 3:
        play_sound('sfx/level3intro.wav')


def level_up():
    """Check if player has completed level within max clicks,
       and if so set up next level."""

    if Mem.level == 1 and Mem.all_clicks < 31:
        messagebox.showinfo('Congratulations:',
                            'Well done, level 1 completed\n\n'
                            'Click OK to play level 2.')
        Mem.level = 2
        Mem.num_pairs = 12
        Mem.target_clicks = 60
        return

    if Mem.level == 2 and Mem.all_clicks < 61:
        messagebox.showinfo('Congratulations:',
                            'Well done, level 2 completed\n\n'
                            'Click OK to play level 3.')
        Mem.level = 3
        Mem.num_pairs = 16
        Mem.target_clicks = 90
        return

    if Mem.level == 3 and Mem.all_clicks < 91:
        complete_game_as_winner()
        return

    # Repeat level.
    messagebox.showinfo('Good try:',
                        'Well done, but to progress\n'
                        'you must complete this level\n'
                        'in less clicks next time.\n\n'
                        'Click OK to try again.')
    play_start_level_sound()


def we_have_a_winner():
    """If level is completed reset routine."""
    updt_status_bar('Completed puzzle in: '
                    + str(Mem.all_clicks) + ' clicks')

    Mem.new_card = ''
    Mem.first_card = ''
    Mem.click_count = 0
    Mem.found_matches = 0
    Mem.total_tries = 0
    Mem.match_list = []
    Mem.blank_cards = []
    Mem.card_images = []
    Mem.stat_bar = None
    Mem.card = None

    level_up()  # Do we up a level or not?

    # Start game.
    Mem.all_clicks = 0
    create_status_bar()
    create_game_board()
    play_start_level_sound()


def level_msg():
    """Alert player as to max clicks to get to next level."""
    if Mem.level == 1:
        updt_status_bar('Complete this level within 30 clicks'
                        ' to advance to level 2.')
    if Mem.level == 2:
        updt_status_bar('Complete this level within 60 clicks'
                        ' to advance to level 3.')
        root.title('Memory Royale    Level 2')

    if Mem.level == 3:
        updt_status_bar('Complete this level within 90 clicks'
                        ' to complete game.')
        root.title('Memory Royale    Level 3')


def get_png_list(loc):
    """Get all images in 'png' dir."""
    pngs = [f for f in os.listdir(loc) if f[-4:] == '.png']
    return [os.path.join(loc, f) for f in pngs]


def check_match():
    """Check for a match. Update match tracker."""
    Mem.total_tries += 1
    Mem.new_card.img = Mem.card
    Mem.new_card.config(image=Mem.new_card.img)
    Mem.first_card.img = Mem.card
    Mem.first_card.config(image=Mem.first_card.img)

    for item in Mem.blank_cards:
        if item.cget('text') not in Mem.match_list:
            item.bind('<Button-1>', on_click)

    Mem.click_count = 0


def on_click(event):
    """When a card is clicked, show image, check for match and game won."""
    play_sound('sfx/click.wav')
    Mem.click_count += 1
    Mem.all_clicks += 1

    Mem.new_card = event.widget
    img = tk.PhotoImage(file=Mem.new_card.cget('text'))
    Mem.new_card.img = img
    Mem.new_card.config(image=img)

    if Mem.click_count == 1:
        Mem.first_card = Mem.new_card  # Put in holding space if 1st click.
        Mem.first_card.unbind('<Button-1>')
        updt_status_bar('Clicks:' + str(Mem.all_clicks) +
                        '-' + str(Mem.target_clicks))

    else:
        for item in Mem.blank_cards:
            item.unbind('<Button-1>')
        # FOUND MATCH: Unbind click events. Update match tracker.
        if Mem.new_card.cget('text') == Mem.first_card.cget('text'):
            play_sound('sfx/matchedpair.wav')
            Mem.match_list.append(Mem.new_card.cget('text'))
            Mem.found_matches += 1
            # print(Mem.found_matches)
            Mem.total_tries += 1
            Mem.click_count = 0
            for item in Mem.blank_cards:
                if item.cget('text') not in Mem.match_list:
                    updt_status_bar('Clicks:' + str(Mem.all_clicks) +
                                    '-' + str(Mem.target_clicks))
                    item.bind('<Button-1>', on_click)
            if Mem.found_matches == Mem.num_pairs:
                we_have_a_winner()
                updt_status_bar('Clicks:' + str(Mem.all_clicks) +
                                '-' + str(Mem.target_clicks))

                # print('Total Tries = ' + str(Mem.total_tries))

        else:
            for item in Mem.blank_cards:
                item.unbind('<Button-1>')
                updt_status_bar('Clicks:' + str(Mem.all_clicks) +
                                '-' + str(Mem.target_clicks))

            Mem.new_card.after(1000, check_match)


def create_game_board():
    """Creats the game board depending on level."""
    image_dir = os.path.join(os.path.dirname(__file__), 'png')
    image_array = get_png_list(image_dir)

    # Create array with how many cards needed and double it.
    image_pairs = image_array[0:Mem.num_pairs]
    image_pairs = image_pairs * 2

    # Because we doubled, we need to re-shuffle order.
    random.shuffle(image_pairs)

    card_dir = os.path.join(os.path.dirname(__file__), 'misc/card.png')
    Mem.card = tk.PhotoImage(file=card_dir)

    # Display card back images in a grid 8 wide.
    ro = 0
    col = 0

    game_board_frame = tk.Frame(root)
    game_board_frame.grid(row=1, column=0)
    game_board_frame.configure(background='darkgreen')

    for i in range(len(image_pairs)):
        Mem.blank_cards.append(tk.Label(game_board_frame))
        Mem.card_images.append(tk.PhotoImage(file=image_pairs[i]))
        Mem.blank_cards[i].img = Mem.card
        Mem.blank_cards[i].config(image=Mem.blank_cards[i].img)
        Mem.blank_cards[i].config(text=image_pairs[i])
        Mem.blank_cards[i].grid(row=ro, column=col, padx=5, pady=5)
        Mem.blank_cards[i].bind('<Button-1>', on_click)
        col += 1
        if col == 8:
            col = 0
            ro += 1
        level_msg()

        # For game testing.
        # cheat = image_pairs[i]
        # print(str(i+1) + ' :' + cheat[-6:])


def create_status_bar():
    """Create the status bar."""
    stat_frame = tk.Frame(root)
    stat_frame.grid(padx=0, pady=4,
                    row=4, columnspan=8,
                    sticky=tk.W + tk.E)

    Mem.stat_bar = tk.Label(stat_frame,
                            bg='yellowgreen',
                            fg='black',
                            font=('ariel, 14'),
                            text='',
                            bd=1,
                            relief=tk.SUNKEN,
                            anchor=tk.W)
    Mem.stat_bar.pack(side=tk.BOTTOM, fill=tk.X)


# Start game.
logo()
play_start_level_sound()
create_status_bar()
create_game_board()


#  -The rest below is all menu related except for last few lines at end.-
def help_me():
    """Opens a help, using systems default text viewer."""
    web.open('help.txt')


def about_menu():
    """About program."""
    messagebox.showinfo('Program info',
                        'Memory Royale V1.1\n'
                        'MIT licence\n'
                        '(c)Steve Shambles. \n'
                        'Freeware 2021-2023.')


def visit_github():
    """View my source codes on GitHub."""
    web.open('https://github.com/steve-shambles?tab=repositories')


def donate_me():
    """User splashes the cash here donating via PayPal."""
    web.open('https:\\paypal.me/photocolourizer')


def exit_app():
    """Don't go.I love you and want to have your children, I'm rich too!."""
    ask_yn = messagebox.askyesno('Question', 'Confirm Quit?')
    if not ask_yn:
        return
    root.destroy()


# Pre-load icons for drop-down menu.
help_icon = ImageTk.PhotoImage(file='icons/help-16x16.ico')
about_icon = ImageTk.PhotoImage(file='icons/about-16x16.ico')
github_icon = ImageTk.PhotoImage(file='icons/github-16x16.ico')
blog_icon = ImageTk.PhotoImage(file='icons/blog-16x16.ico')
contact_icon = ImageTk.PhotoImage(file='icons/contact-16x16.ico')
donation_icon = ImageTk.PhotoImage(file='icons/donation-16x16.ico')
exit_icon = ImageTk.PhotoImage(file='icons/exit-16x16.ico')

# Drop-down menu.
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Menu', menu=file_menu)

file_menu.add_command(label='Help', compound='left',
                      image=help_icon, command=help_me)
file_menu.add_command(label='About', compound='left',
                      image=about_icon, command=about_menu)
file_menu.add_separator()
file_menu.add_command(label='Python source code on GitHub',
                      compound='left',
                      image=github_icon, command=visit_github)
file_menu.add_command(label='Make a small donation via PayPal',
                      compound='left',
                      image=donation_icon, command=donate_me)
file_menu.add_separator()
file_menu.add_command(label='Exit', compound='left',
                      image=exit_icon, command=exit_app)
root.config(menu=menu_bar)

# Capture user trying to exit via x icon on window.
root.protocol('WM_DELETE_WINDOW', exit_app)


root.mainloop()
