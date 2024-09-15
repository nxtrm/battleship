import time
import customtkinter
import tkinter
import os
from PIL import Image,ImageTk
import pygame

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # setting up the window
        scale_factor = 0.9
        
        # music player definition
        pygame.mixer.init()

        self.scale_width = int(600 * scale_factor)
        self.scale_height = int(900 * scale_factor)
        self.scale_font = int(15 * scale_factor)

        self.geometry(str(self.scale_width) + "x" + str(self.scale_height))
        self.title("Battleship")

        self.image = customtkinter.CTkImage(Image.open(os.path.join('./media','wp.png')),size=(self.scale_height,self.scale_width))

        self.main = customtkinter.CTkFrame(self)
        self.main.pack(pady=10, padx=10)
        

        # variables, needed for setup()
        self.current_player = "Player 1"
        self.placing_mode = False
        self.ship_data = {
            "Aircraft carrier": {"length": 5, "count": 1},
            "Battleship": {"length": 4, "count": 1},
            "Cruiser": {"length": 3, "count": 1},
            "Destroyer": {"length": 2, "count": 2},
            "Submarine": {"length": 1, "count": 2},
        }
        self.player_data = {
            "Player 1": {"ships": [], "hits": [], "misses": []},
            "Player 2": {"ships": [], "hits": [], "misses": []},
        }

        # bar animation
        self.animation_running = False

    def main_scr(self):
        def play_onClick():
            self.main_fr.forget()
            self.setup()
    
        self.main_fr = customtkinter.CTkFrame(master=self.main)
        self.main_fr.pack(padx=10, pady=12)
        self.main_fr.grid_rowconfigure((0, 1), weight=1)
        self.main_fr.grid_columnconfigure((0, 1, 2), weight=1)

        self.title_l = customtkinter.CTkLabel(master=self.main_fr,image=self.image, text="Battleship",
            font=customtkinter.CTkFont(size=int(self.scale_font * 3), weight="bold") )
        self.title_l.grid(pady=1,padx=11,row=0,column=1, rowspan=3)

        self.play_but = customtkinter.CTkButton(
                master=self.main_fr,
                width=self.scale_width // 3.5,
                height=self.scale_height // 25,
                text="Play",
                font=customtkinter.CTkFont(size=self.scale_font*2,weight="bold"), 
                command=play_onClick
                )
        self.play_but.grid(row=1,column=1,pady=1,padx=11, rowspan=3)

    def setup(self):
        # defining the board
        self.setup_fr = customtkinter.CTkFrame(master=self.main)
        self.setup_fr.pack(padx=10, pady=12)

        self.board_fr = customtkinter.CTkFrame(
            master=self.setup_fr,
            height=self.scale_width * 0.8,
            width=self.scale_width * 0.8,
        )
        self.board_fr.pack(padx=10, pady=12)
        self.board_fr.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        self.board_fr.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)

        # populating the board
        self.cells = [
            [
                {
                    "name": f"{x}-{y}",
                    "cell": customtkinter.CTkButton(
                        master=self.board_fr, 
                        width=self.scale_width // 20,
                        height=self.scale_width // 20,
                        text=" ",
                        command=lambda name=f"{x}-{y}": self.place_ship_cell(name),
                    ),
                }
                for y in range(10)
            ]
            for x in range(10)
        ]

        for row in self.cells:
            for cell in row:
                cell["cell"].grid(
                    row=int((cell["name"][0])),
                    column=int((cell["name"][2])),
                    padx=2,
                    pady=2,
                )

        self.setup_l = customtkinter.CTkLabel(
            master=self.setup_fr, 
            text="Setup: " + self.current_player,
            font=customtkinter.CTkFont(size=int(self.scale_font * 2.5), weight="bold"),
        )
        self.setup_l.pack(padx=10, pady=15)
        # making buttons for ship selection
        self.ship_buttons = []
        for i, ship in enumerate(self.ship_data):
            name, stats = ship, self.ship_data[ship]
            button = customtkinter.CTkButton(
                master=self.setup_fr,
                width=self.scale_width // 4,
                height=self.scale_height // 25,
                text=name,
                font=customtkinter.CTkFont(size=self.scale_font),
                command=lambda s=stats, n=name: self.select_ship(s, n),
            )
            self.ship_buttons.append({"name": name, "button": button})
            button.pack(padx=10, pady=12)
        # adding the "next" and "reset" buttons ( for later)
        # Next button
        self.next_but = customtkinter.CTkButton(
            master=self.setup_fr,
            font=customtkinter.CTkFont(size=self.scale_font + 5),
            text_color="white",
            width=self.scale_width // 5,
            height=self.scale_height // 25,
            command=lambda c="next": self.next(c),
        )
        # Error button
        self.error_l = customtkinter.CTkLabel(
            master=self.setup_fr,
            text="❌ ERROR : Ship position is invalid",
            text_color="red",
            font=customtkinter.CTkFont(size=self.scale_font),
        )
        # Reset button
        self.reset_but = customtkinter.CTkButton(
            master=self.setup_fr,
            font=customtkinter.CTkFont(size=self.scale_font + 5),
            text_color="white",
            width=self.scale_width // 5,
            height=self.scale_height // 25,
            text="↩  Reset",
            command=lambda c="reset": self.next(c),
        )

    def game(self):
        """
        self.player_data = {
            "Player 1": {"ships": ["0-0"], "hits": [], "misses": []},
            "Player 2": {
                "ships": ["0-1"],
                "hits": [],
                "misses": [],
            },
        }
        """
        self.game_fr = customtkinter.CTkFrame(master=self.main)
        self.game_fr.pack(padx=10, pady=12)

        self.board_fr = customtkinter.CTkFrame(
            master=self.game_fr,
            height=self.scale_width * 0.8,
            width=self.scale_width * 0.8,
        )
        self.board_fr.pack(padx=10, pady=12)
        self.board_fr.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        self.board_fr.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)

        self.player_l = customtkinter.CTkLabel(
            master=self.game_fr,
            text=self.current_player,
            font=customtkinter.CTkFont(size=self.scale_font * 2, weight="bold"),
        )
        self.player_l.pack(padx=10, pady=15)

        self.anim_bar = customtkinter.CTkProgressBar(
            master=self.game_fr,
            width=self.scale_width // 2,
            height=self.scale_height // 100,
        )
        self.anim_bar.set(1)
        self.anim_bar.pack(padx=10, pady=12)

        self.cells = [
            [
                {
                    "name": f"{x}-{y}",
                    "cell": customtkinter.CTkButton(
                        master=self.board_fr,
                        width=self.scale_width // 20,
                        height=self.scale_width // 20,
                        text=" ",
                        command=lambda name=f"{x}-{y}": self.shot(name, self.cells),
                    ),
                }
                for y in range(10)
            ]
            for x in range(10)
        ]

        for row in self.cells:
            for cell in row:
                cell["cell"].grid(
                    row=int((cell["name"][0])),
                    column=int((cell["name"][2])),
                    padx=2,
                    pady=2,
                )
        self.recolor_Cells(self.cells, self.player_data)

    def recolor_Cells(self, cells, player_data):
        self.anim_bar.set(1)

        for row in cells:
            for cell in row:
                if cell["name"] in player_data[self.current_player]["hits"]:
                    cell["cell"].configure(fg_color="red", state="disabled")

                elif cell["name"] in player_data[self.current_player]["misses"]:
                    cell["cell"].configure(fg_color="white", state="disabled")

                else:
                    cell["cell"].configure(
                        fg_color="#1f538d",
                        state="enabled",
                    )

        self.player_l.configure(text=self.current_player)
        self.game_fr.update()

    def bar_animation(self):
        self.animation_running = True
        bar = 1
        for i in range(20):
            bar -= 0.05
            self.anim_bar.set(bar)
            self.board_fr.update()
            time.sleep(0.012)
        self.animation_running = False

    def shot(self, name, cells):
        cell = self.findcell(cells, name)

        other_player = "Player 2" if self.current_player == "Player 1" else "Player 1"

        if name in self.player_data[other_player]["ships"]:
            cell.configure(fg_color="red")
            self.board_fr.update()

            self.player_data[self.current_player]["hits"].append(name)
            self.player_data[other_player]["ships"].remove(name)

            if len(self.player_data[other_player]["ships"]) == 0:
                self.gameWinner = self.current_player
                self.player_l.configure(text=self.gameWinner + " won")
                self.anim_bar.configure(progress_color="green")
                self.game_fr.update()

                self.play_again_but = customtkinter.CTkButton(
                    master=self.game_fr,
                    width=self.scale_width // 4,
                    height=self.scale_height // 25,
                    text="⤿   Play again",
                    command=self.play_again,
                    font=customtkinter.CTkFont(size=int(self.scale_font * 1.5)),
                )
                self.play_again_but.pack(padx=10, pady=10)

                self.quit_but = customtkinter.CTkButton(
                    master=self.game_fr,
                    text="Quit",
                    width=self.scale_width // 4,
                    height=self.scale_height // 25,
                    command=self.quit_onClick,
                    font=customtkinter.CTkFont(size=int(self.scale_font * 1.5)),
                )
                self.quit_but.pack(padx=10, pady=10)
        else:
            if not self.animation_running:
                cell.configure(fg_color="white")

                self.board_fr.update()
                self.bar_animation()

                self.player_data[self.current_player]["misses"].append(name)

                if self.current_player == "Player 1":
                    self.current_player = "Player 2"
                else:
                    self.current_player = "Player 1"
                other_player = (
                    "Player 2" if self.current_player == "Player 1" else "Player 1"
                )
                self.recolor_Cells(self.cells, self.player_data)

    def play_again(self):
        self.game_fr.forget()
        self.rtd()
        self.player_data = {
            "Player 1": {"ships": [], "hits": [], "misses": []},
            "Player 2": {"ships": [], "hits": [], "misses": []},
        }
        self.setup()

    def quit_onClick(self):
        self.destroy()

    def select_ship(self, ship_selected, ship_name):
        # retrieving values of the selected ship and changing the buttons so the ship would be highlighted
        if self.placing_mode == False:
            for j in self.ship_buttons:
                if str(j["name"]) == str(ship_name):
                    self.button = j["button"]

            if ship_selected["count"] > 0:
                self.placing_mode = True
                self.temp_ship = []
                ship_selected["count"] = ship_selected["count"] - 1
                self.button.configure(fg_color="green", hover_color="green")
                self.ships_left = ship_selected["count"]
                self.cells_left = ship_selected["length"]
                self.placed_cell_count = 0

    # placing ships
    def place_ship_cell(self, name):
        if self.placing_mode == True and self.cells_left > 0:
            # finding and editing the cell
            cell = self.findcell(self.cells, name)
            cell.configure(fg_color="green", hover_color="green", state="disabled")
            self.cells_left = self.cells_left - 1
            self.placed_cell_count = self.placed_cell_count + 1
            # blocking the diagonals
            self.block_diagonals(name)

            # saving the placed cell
            self.player_data[self.current_player]["ships"].append(name)
            self.temp_ship.append(name)

            if self.cells_left == 0:
                self.placing_mode = False

                # encasing the chip in blocked cells
                self.block_ship(self.temp_ship)

                # checking ship validity
                flag = self.check_ship(self.temp_ship)

                if flag == True:
                    if self.ships_left == 0:
                        self.button.configure(fg_color="grey35", hover_color="grey30")
                    else:
                        self.button.configure(fg_color="#1f538d")

                    if self.no_ships_left():
                        # if True:
                        # removing the ship buttons
                        for i in self.ship_buttons:
                            i["button"].forget()

                        # placing the "next" and "reset" buttons
                        if self.current_player == "Player 1":
                            self.next_but.configure(text="▶  Next")
                        else:
                            self.next_but.configure(text="▶  Play")
                        self.next_but.pack(padx=10, pady=10)

                        self.reset_but.pack(padx=10, pady=10)
                else:
                    # removing the ship buttons
                    for i in self.ship_buttons:
                        i["button"].forget()
                    self.next("error")

    # finding cell by name
    def findcell(self, cells, name):
        for row in cells:
            for cell in row:
                if cell["name"] == name:
                    return cell["cell"]

    # diagonals
    def block_diagonals(self, name):
        diagonals = [
            f"{int(name[0])-1}-{int(name[2])-1}",
            f"{int(name[0])+1}-{int(name[2])-1}",
            f"{int(name[0])-1}-{int(name[2])+1}",
            f"{int(name[0])+1}-{int(name[2])+1}",
        ]
        for i in diagonals:
            try:
                cell = self.findcell(self.cells, i)
                if cell.cget("fg_color") != "green":
                    cell.configure(state="disabled", fg_color="grey")
            except:
                pass

    # cheks, whether each cell is correctly placed
    def check_ship(self, ship):
        flag = False
        for name in ship:
            potentialInvalid = [
                f"{int(name[0])-1}-{int(name[2])}",
                f"{int(name[0])+1}-{int(name[2])}",
                f"{int(name[0])}-{int(name[2])+1}",
                f"{int(name[0])}-{int(name[2])-1}",
            ]
        for e in potentialInvalid:
            try:
                cell = self.findcell(self.cells, e)
                if cell.cget("fg_color") == "green":
                    flag = True
            except:
                pass
        if self.placed_cell_count == 1:
            flag = True
        return flag

    # encase the ship with cells
    def block_ship(self, ship):
        for name in ship:
            potentialInvalid = [
                f"{int(name[0])-1}-{int(name[2])}",
                f"{int(name[0])+1}-{int(name[2])}",
                f"{int(name[0])}-{int(name[2])+1}",
                f"{int(name[0])}-{int(name[2])-1}",
            ]
            for e in potentialInvalid:
                try:
                    cell = self.findcell(self.cells, e)
                    if (
                        cell.cget("fg_color") != "green"
                        and cell.cget("fg_color") != "grey"
                    ):
                        cell.configure(state="disabled", fg_color="grey")
                except:
                    pass

    # check for any other remaining ships
    def no_ships_left(self):
        for ship in self.ship_data:
            if self.ship_data[ship]["count"] > 0:
                return False
        return True

    def rtd(self):
        # cleans the board and returns the dict to default values
        self.ship_data = {
            "Aircraft carrier": {"length": 5, "count": 1},
            "Battleship": {"length": 4, "count": 1},
            "Cruiser": {"length": 3, "count": 1},
            "Destroyer": {"length": 2, "count": 2},
            "Submarine": {"length": 1, "count": 2},
        }

    def next(self, c):
        # cleaning the board
        if c == "next":
            if self.current_player == "Player 1":
                self.current_player = "Player 2"
                self.setup_fr.forget()
                self.rtd()
                self.setup()
            else:
                # the round starts
                self.current_player = "Player 1"
                self.setup_fr.forget()
                self.game()
        elif c == "reset":
            # resets the ships of the current player
            self.player_data[self.current_player] = {
                "ships": [],
                "hits": [],
                "misses": [],
            }
            self.setup_fr.forget()
            self.rtd()
            self.setup()
        elif c == "error":
            # displays the error message
            self.error_l.pack(padx=10, pady=10)
            self.reset_but.pack(padx=10, pady=10)


app = App()
app.main_scr()
#app.setup()
# app.game()
app.mainloop()
