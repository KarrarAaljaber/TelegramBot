import tkinter as tk
from TelegramUserInviter import TelegramUserInviter

if __name__ == '__main__':
    root = tk.Tk()
    app = TelegramUserInviter(master=root)
    app.mainloop()
