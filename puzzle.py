from tkinter import Frame, Label, CENTER
import random
import logic
import constants as c

import time
import board
import digitalio
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.digitalio import DigitalIO
from adafruit_seesaw.pwmout import PWMOut

def gen():
    return random.randint(0, c.GRID_LEN - 1)

class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_down)

        self.commands = {
            c.KEY_UP_ALT1: logic.up,
            c.KEY_DOWN_ALT1: logic.down,
            c.KEY_LEFT_ALT1: logic.left,
            c.KEY_RIGHT_ALT1: logic.right,
            c.KEY_UP_ALT2: logic.up,
            c.KEY_DOWN_ALT2: logic.down,
            c.KEY_LEFT_ALT2: logic.left,
            c.KEY_RIGHT_ALT2: logic.right,
        }

        self.grid_cells = []
        self.init_grid()
        self.matrix = logic.new_game(c.GRID_LEN)
        self.history_matrixs = []
        self.update_grid_cells()
        self.setup_buttons()
        self.run_button()
        self.mainloop()

    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME,width=c.SIZE, height=c.SIZE)
        background.grid()

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(
                    background,
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    width=c.SIZE / c.GRID_LEN,
                    height=c.SIZE / c.GRID_LEN
                )
                cell.grid(
                    row=i,
                    column=j,
                    padx=c.GRID_PADDING,
                    pady=c.GRID_PADDING
                )
                t = Label(
                    master=cell,
                    text="",
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    justify=CENTER,
                    font=c.FONT,
                    width=5,
                    height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def setup_buttons(self):
        self.i2c = board.I2C() 
        self.arcade_qt = Seesaw(self.i2c, addr=0x3A)
        self.button_pins = (18, 19, 20, 2)
        self.buttons = {}
        for button_pin in self.button_pins:
            button = DigitalIO(self.arcade_qt, button_pin)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
            self.buttons[button_pin] = button

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="",bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number]
                    )
        self.update_idletasks()

    def key_down(self, event):
        key = event.keysym
        print(event)
        if key == c.KEY_QUIT: exit()
        if key == c.KEY_BACK and len(self.history_matrixs) > 1:
            self.matrix = self.history_matrixs.pop()
            self.update_grid_cells()
            print('back on step total step:', len(self.history_matrixs))

    def check_buttons(self):
        for key in self.buttons.keys():
            button = self.buttons[key]
            if not button.value:
                print(f'button at pin {key} was pressed') 
                        
                #Map the direction to the button pressed 
                if key == 20:
                    self.matrix, done = logic.up(self.matrix)
                elif key == 2:
                    self.matrix, done = logic.right(self.matrix)
                elif key == 19:
                    self.matrix, done = logic.left(self.matrix) 
                elif key == 18:
                    self.matrix, done = logic.down(self.matrix)
                
                if done:
                    print("adding two tiles to matrix")
                    self.matrix = logic.add_two(self.matrix)
                    # record last move
                    print("recording last move")
                    self.history_matrixs.append(self.matrix)
                    self.update_grid_cells()
                    if logic.game_state(self.matrix) == 'win': 
                        self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                        self.grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    if logic.game_state(self.matrix) == 'lose': #this doesn't work
                        self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                        self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                return

    def generate_next(self):
        index = (gen(), gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (gen(), gen())
        self.matrix[index[0]][index[1]] = 2

    def run_button(self):
        for key in self.buttons.keys():
            button = self.buttons[key]
            button.value = True
        self.check_buttons()
        self.master.after(100, self.run_button)

game_grid = GameGrid()
