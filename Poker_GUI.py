import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import random
from treys import Card, Evaluator

PATH = "pythoncode\class\cards_images"
SIZE = (90+50, 130+60)

class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Game")
        self.root.configure(bg="darkgreen")

        self.img = self.load_images()

      
        #Titles + Frames

        tk.Label(root, text="Opponent Cards", font=("Arial", 14, "bold"),
                 bg="darkgreen", fg="white").grid(row=0, pady=(10,0))
        self.top = tk.Frame(root, bg="blue")
        self.top.grid(row=1, pady=(0,10))

        tk.Label(root, text="Table Cards", font=("Arial", 14, "bold"),
                 bg="darkgreen", fg="white").grid(row=2, pady=(10,0))
        self.mid = tk.Frame(root, bg="darkgreen")
        self.mid.grid(row=3, pady=(0,10))

        tk.Label(root, text="Your Cards", font=("Arial", 14, "bold"),
                 bg="darkgreen", fg="white").grid(row=4, pady=(10,0))
        self.bot = tk.Frame(root, bg="black")
        self.bot.grid(row=5, pady=(0,10))

        #card labels
      
        self.comp  = [tk.Label(self.top, bg="white") for i in range(2)]
        self.table = [tk.Label(self.mid, bg="white") for i in range(5)]
        self.me    = [tk.Label(self.bot, bg="white") for i in range(2)]

        for i,l in enumerate(self.comp):  l.grid(row=0, column=i, padx=10)
        for i,l in enumerate(self.table): l.grid(row=0, column=i, padx=10)
        for i,l in enumerate(self.me):    l.grid(row=0, column=i, padx=10)

        #buttons+info

        self.ctrl = tk.Frame(root, bg="darkgreen")
        self.ctrl.grid(row=6, pady=20)

        tk.Button(self.ctrl, text="Bet / Check", font=("Arial", 14),
                  command=self.action).grid(row=0, column=0, padx=20)

        tk.Button(self.ctrl, text="Quit", font=("Arial", 14),
                  command=root.destroy).grid(row=0, column=1, padx=20)

        self.info = tk.Label(root, bg="darkgreen", fg="white", font=("Arial", 14))
        self.info.grid(row=7, pady=10)

        self.set()

    #image-loading
  
    def load_images(self):
        import os
        imgs = {}
        for f in os.listdir(PATH):
            if f.endswith(".png"):
                card = f[:-4]
                im = Image.open(f"{PATH}/{f}").resize(SIZE)
                imgs[card] = ImageTk.PhotoImage(im)
        return imgs


    #game-setup

    def set(self):
        self.yb = 100
        self.cb = 100
        self.pot = 0

        deck = [r+s for r in "A23456789TJQK" for s in "hdcs"]
        random.shuffle(deck)

        self.you = deck[:2]
        self.cs  = deck[2:4]
        self.flop = deck[4:7]
        self.turn = deck[7]
        self.river = deck[8]

        #blinds
        self.yb -= 1
        self.cb -= 1
        self.pot = 2
        self.stage = "pre"

        #Showing hole cards
        for i,c in enumerate(self.you):
            self.me[i].config(image=self.img[c])
        for i,c in enumerate(self.cs):
            self.comp[i].config(image=self.img[c])

        #Clear table
        for t in self.table:
            t.config(image="")

        self.update("Preflop: Enter bet (0 = check).")

    def update(self, msg=""):
        self.info.config(text=f"You: {self.yb}   Opponent: {self.cb}   Pot: {self.pot}\n{msg}")

    #bet popup

    def ask_bet(self, title):
        while True:
            bet = simpledialog.askinteger("Bet", f"{title}\nEnter bet:", minvalue=0)
            if bet is None: return None
            if 0 <= bet <= self.yb: return bet
            messagebox.showerror("Invalid Bet", "Enter a valid bet not exceeding your balance.") #title,text

    #show cards


    def show_flop(self):
        for i,c in enumerate(self.flop):
            self.table[i].config(image=self.img[c])

    def show_turn(self):
        self.show_flop()
        self.table[3].config(image=self.img[self.turn])

    def show_river(self):
        self.show_turn()
        self.table[4].config(image=self.img[self.river])

    #bet handling

    def handle_bet(self, bet, next_func):
        self.yb -= bet
        self.pot += bet
        self.update()

        if bet > 50:
            self.yb += self.pot
            self.end("Computer folds! You win pot")
            return

        if bet == 0:
            next_func()
        else:
            self.cb -= bet
            self.pot += bet
            self.update()
            next_func()

    #button actions
 

    def action(self):
        if self.stage == "pre":
            b = self.ask_bet("Preflop")
            self.handle_bet(b, self.to_flop)

        elif self.stage == "flop":
            b = self.ask_bet("Flop")
            self.handle_bet(b, self.to_turn)

        elif self.stage == "turn":
            b = self.ask_bet("Turn")
            self.handle_bet(b, self.to_river)

        elif self.stage == "river":
            b = self.ask_bet("River")
            self.handle_bet(b, self.showdown)

    #stage transition
 

    def to_flop(self):
        self.show_flop()
        self.stage = "flop"
        self.update("Flop shown. Enter bet.")

    def to_turn(self):
        self.show_turn()
        self.stage = "turn"
        self.update("Turn shown. Enter bet.")

    def to_river(self):
        self.show_river()
        self.stage = "river"
        self.update("River shown. Enter bet.")

    #showdown

    def showdown(self):
        board = self.flop + [self.turn, self.river]
        eval = Evaluator()

        y = eval.evaluate([Card.new(c) for c in board],
                          [Card.new(c) for c in self.you])
        cs = eval.evaluate([Card.new(c) for c in board],
                           [Card.new(c) for c in self.cs])

        if y < cs:
            msg = f"You WIN a pot of {self.pot}!!!"
            self.yb += self.pot
        elif y > cs:
            msg = f"You LOSE a pot of {self.pot}!!!"
        else:
            self.yb += self.pot/2
            self.cb += self.pot/2
            msg = f"It's a TIE — split pot of {self.pot}."

        self.end(msg)

    def end(self, msg):
        messagebox.showinfo("Result", msg)
        self.update("Round over.")
        self.stage = "done"

        self.play_again_btn=tk.Button(self.ctrl, text="Play Again",font=("Arial",14),command=self.play_again )
        self.play_again_btn.grid(row=0,column=2,padx=10)

    def play_again(self):
        self.play_again_btn.destroy()
        self.set()
        
#run
root = tk.Tk()
PokerGUI(root)
root.mainloop()


