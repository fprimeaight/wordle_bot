import discord
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

SQ_SIZE = 70
BORDER_SIZE = 3

KEYBOARD_HEIGHT = 120
BOARD_WIDTH = SQ_SIZE * 5
BOARD_HEIGHT = 580

KEY_WIDTH = BOARD_WIDTH // 10
KEY_HEIGHT = KEYBOARD_HEIGHT // 3 

BG_COLOUR = '#2b2d31'
CORRECT_COLOUR = '#7bba43'
PARTIAL_COLOUR = '#eebf24'
WRONG_COLOUR = '#2e3035'
UNUSED_COLOUR = '#818384'

WORD_FONT_SIZE = 50
KEYBOARD_FONT_SIZE = 30
STATS_FONT_SIZE = 15

MAX_BAR_WIDTH = 250
BAR_HEIGHT = 20
LEFT_BUFFER = 20


def score_graph(score):
    image = Image.new("RGB", (MAX_BAR_WIDTH + LEFT_BUFFER, BAR_HEIGHT * 6), BG_COLOUR)
    draw = ImageDraw.Draw(image)
    stats_font = ImageFont.truetype("./fonts/ARLRDBD.ttf", STATS_FONT_SIZE)
    bar_colour = UNUSED_COLOUR

    for i in range(len(score)):
        length = int(score[i] / sum(score) * MAX_BAR_WIDTH)
        if length > 6:
            draw.rounded_rectangle((LEFT_BUFFER, i * BAR_HEIGHT, 
                                    LEFT_BUFFER + length, (i + 1) * BAR_HEIGHT), 
                                    fill=BG_COLOUR,
                                    radius=3)
        
            draw.rounded_rectangle((LEFT_BUFFER + BORDER_SIZE, i * BAR_HEIGHT + BORDER_SIZE, 
                                    LEFT_BUFFER + length - BORDER_SIZE, (i + 1) * BAR_HEIGHT - BORDER_SIZE), 
                                    fill=bar_colour,
                                    radius=3)
        draw.text(xy=(LEFT_BUFFER // 2, (i + 0.5) * BAR_HEIGHT),
                      text=str(i + 1), 
                      font=stats_font, 
                      fill=(255,255,255), 
                      anchor='mm')

    buf = BytesIO()
    image.save(buf, format='png', subsampling=0, quality=1000)
    buf.seek(0)
    file = discord.File(fp=buf, filename="image.png")
    buf.close()

    return file

def board_image(board, keyboard):
    image = Image.new("RGB", (BOARD_WIDTH, BOARD_HEIGHT), BG_COLOUR)
    draw = ImageDraw.Draw(image)
    word_font = ImageFont.truetype("./fonts/ARLRDBD.ttf", WORD_FONT_SIZE)
    keyboard_font = ImageFont.truetype("./fonts/ARLRDBD.ttf", KEYBOARD_FONT_SIZE)
    keyboard_layout = [['Q','W','E','R','T','Y','U','I','O','P'],
                       ['A','S','D','F','G','H','J','K','L'],
                       ['Z','X','C','V','B','N','M']]

    for row_idx, row in enumerate(board):
        for col_idx, tuple in enumerate(row):
            bool, letter = tuple

            if bool == 1:
                colour = CORRECT_COLOUR
            elif bool == 0:
                colour = PARTIAL_COLOUR
            else:
                colour = WRONG_COLOUR

            draw.rounded_rectangle((col_idx * SQ_SIZE, 
                                    row_idx * SQ_SIZE, 
                                    (col_idx + 1) * SQ_SIZE, 
                                    (row_idx + 1) * SQ_SIZE), 
                                    fill=BG_COLOUR,
                                    radius=3)
            
            draw.rounded_rectangle((col_idx * SQ_SIZE + BORDER_SIZE, 
                                    row_idx * SQ_SIZE + BORDER_SIZE, 
                                    (col_idx + 1) * SQ_SIZE - BORDER_SIZE, 
                                    (row_idx + 1) * SQ_SIZE - BORDER_SIZE), 
                                    fill=colour,
                                    radius=3)
            
            draw.text(xy=((col_idx + 0.5) * SQ_SIZE, (row_idx + 0.5) * SQ_SIZE),
                      text=letter, 
                      font=word_font, 
                      fill=(255,255,255), 
                      anchor='mm')
            
    for row_idx, row in enumerate(keyboard_layout):
        for col_idx, letter in enumerate(row):

            if keyboard[letter] == 1:
                colour = CORRECT_COLOUR
            elif keyboard[letter] == 0:
                colour = PARTIAL_COLOUR
            elif keyboard[letter] == -1:
                colour = WRONG_COLOUR
            else:
                colour = UNUSED_COLOUR
            
            
            draw.rounded_rectangle((col_idx * KEY_WIDTH, 
                                    row_idx * KEY_HEIGHT + BOARD_HEIGHT - KEYBOARD_HEIGHT, 
                                    (col_idx + 1) * KEY_WIDTH, 
                                    (row_idx + 1) * KEY_HEIGHT + BOARD_HEIGHT - KEYBOARD_HEIGHT), 
                                    fill=BG_COLOUR,
                                    radius=3)
            
            draw.rounded_rectangle((col_idx * KEY_WIDTH + BORDER_SIZE, 
                                    row_idx * KEY_HEIGHT + BOARD_HEIGHT - KEYBOARD_HEIGHT + BORDER_SIZE, 
                                    (col_idx + 1) * KEY_WIDTH - BORDER_SIZE, 
                                    (row_idx + 1) * KEY_HEIGHT + BOARD_HEIGHT - KEYBOARD_HEIGHT - BORDER_SIZE), 
                                    fill=colour,
                                    radius=3)

            draw.text(xy=((col_idx + 0.5) * KEY_WIDTH, (row_idx + 0.5) * KEY_HEIGHT + BOARD_HEIGHT - KEYBOARD_HEIGHT),
                      text=letter, 
                      font=keyboard_font, 
                      fill=(255,255,255), 
                      anchor='mm')

    buf = BytesIO()
    image.save(buf, format='png', subsampling=0, quality=1000)
    buf.seek(0)
    file = discord.File(fp=buf, filename="image.png")
    buf.close()

    return file
