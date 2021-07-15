import csv
import time
import tkinter as tk
import tkinter.filedialog as fd
import traceback
from tkinter import *

from numpy import random
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError
from telethon.sync import TelegramClient
from telethon.tl import functions
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsSearch


class TelegramUserInviter(tk.Frame):
    api_ids = []
    api_hashes = []
    phone_numbers = []
    client = None
    groups = []
    group_participants = []
    No_of_participants = 0
    users = []

    msg = None

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.resizable(False, False)
        self.master.eval('tk::PlaceWindow . center')
        self.selected_group = tk.StringVar()
        self.addToGroup = tk.StringVar()
        self.inviteLink = None
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.window_width = 800
        self.window_height = 600
        self.receiver = None
        self.x_cordinate = int((self.screen_width / 2) - (self.window_width / 2))
        self.y_cordinate = int((self.screen_height / 2) - (self.window_height / 2))
        self.userAmount = StringVar()
        self.nOfMsgsPerN = StringVar()
        self.sleepTime = StringVar()
        self.singleMessage = tk.IntVar()
        self.master.geometry(
            "{}x{}+{}+{}".format(self.window_width, self.window_height, self.x_cordinate, self.y_cordinate))
        self.master.configure(background='white')

        self.large_font = ('Verdana', 15)
        self.small_font = ('Verdana', 11)
        self.mainColor = "#332767"
        self.bg = PhotoImage(file="bg.png")
        l = Label(self.master, image=self.bg)
        l.place(x=0, y=0, relwidth=1, relheight=1)

        title = Label(self.master, bg=self.mainColor, fg="white", width=80, height=2, text="Message Sender",
                      borderwidth=4,
                      relief="groove",
                      font=("Helvetica", 18, "bold"))
        title.pack(pady=20)

        tk.Button(command=self.loadFile, text="LOAD ACCOUNTS (.txt file)", bg=self.mainColor, borderwidth=4,
                  relief="raised", fg="white", width=45,
                  height=2,
                  font=("Helvetica", 12, "bold")).pack()

    def loadFile(self):
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)

        lines = []
        with open(filename) as f:
            lines = f.read().splitlines()

        # print(lines)

        print(len(lines))
        self.phone_numbers = []
        self.api_ids = []
        self.api_hashes = []
        for x in range(len(lines)):
            self.phone_numbers.append(lines[x].split(":")[0])
            self.api_hashes.append(lines[x].split(":")[1])
            self.api_ids.append(lines[x].split(":")[2])

        # print(self.phone_numbers)
        # print(self.api_hashes)
        # print(self.api_ids)

        for widget in self.master.winfo_children():
            widget.destroy()
        l = Label(self.master, image=self.bg)
        l.place(x=0, y=0, relwidth=1, relheight=1)

        title = tk.Label(bg=self.mainColor, fg="white", width=80, height=2, text="Message Sender",
                         borderwidth=4,
                         relief="groove",
                         font=("Helvetica", 18, "bold"))

        title.pack(pady=20)
        tk.Label(bg="white", borderwidth=4, relief="sunken", fg=self.mainColor, width=45, height=1,
                 text="Accounts loaded: " + str(len(self.phone_numbers)),
                 font=("Helvetica", 12, "bold")).pack()

        tk.Button(command=self.loadFile, text="LOAD ACCOUNTS (.txt file)", bg=self.mainColor, borderwidth=4,
                  relief="raised", fg="white", width=45,
                  height=2,
                  font=("Helvetica", 12, "bold")).pack()

        tk.Label(text="", bg="white", height=2).pack()

        tk.Button(text="Connect To First Account", command=self.connectToAllClients, fg="white", bg=self.mainColor,
                  borderwidth=4,
                  relief="raised", width=35,
                  height=1,
                  font=("Helvetica", 11, "bold")).pack()

    def connectToAllClients(self):
        print("Connecting to first account")
        self.client = TelegramClient(self.phone_numbers[0], int(self.api_ids[0]), self.api_hashes[0])
        self.client.session.report_errors = False
        self.client.connect()

        while not self.client.is_user_authorized():
            self.client.send_code_request(self.phone_numbers[0])
            print('a verification has been sent to {}, please wait for sometime'.format(
                self.phone_numbers[0]))
            print("Enter the code : ")
            otp = input()
            try:
                self.client.sign_in(self.phone_numbers[0], otp)
            except:
                print('code you entered was invalid try again')

        self.firstAccGroups()

    def firstAccGroups(self):
        chats = []
        last_date = None
        chunk_size = 200

        result = self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if chat.megagroup:
                    self.groups.append(chat)
            except:
                continue

        groupsTitles = [None] * len(self.groups)

        for i in range(0, len(self.groups)):
            groupsTitles[i] = self.groups[i].title

        container = tk.Frame(width=385, height=460, relief='raised', borderwidth=5)
        container.pack(pady=20)
        Label(container, fg="black", text="Get Users From: ", relief="sunken", font=("Helvetica", 12, "bold"),
              bg="white").grid(row=0,
                               column=0)
        selector = OptionMenu(container, self.selected_group, *groupsTitles, command=self.getUsers)
        selector.config(bg=self.mainColor, fg="white", width=30, font=("Helvetica", 12, "bold"))
        selector.grid(row=0, column=1)

        start = tk.Button(text="Go Next", command=self.scrap_reader, bg=self.mainColor, fg="white", width=35, height=1,
                          font=("Helvetica", 11, "bold")).pack()

    def getUsers(self, args):

        print('Fetching Members...')

        self.group_participants = self.client.get_participants(self.selected_group.get(), aggressive=True)

        print("All Users......")
        for i in range(0, len(self.group_participants)):
            print(self.group_participants[i].username)

        self.writeUsersToFile()

    def writeUsersToFile(self):
        newstr = self.selected_group.get().split(" ")[0]

        export_file_name = str(newstr) + ".csv"
        with open(export_file_name, "w", encoding='UTF-8') as f:
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            writer.writerow(['username', 'user id', 'access hash', 'name', 'group'])
            for user in self.group_participants:
                if user.username:
                    username = user.username
                else:
                    username = ""
                if user.first_name:
                    first_name = user.first_name
                else:
                    first_name = ""
                if user.last_name:
                    last_name = user.last_name
                else:
                    last_name = ""
                name = (first_name + ' ' + last_name).strip()
                writer.writerow([username, user.id, user.access_hash, name])
        print("saving all users to file " + export_file_name + " ! ")

    def getInviteLink(self, args):
        if self.addToGroup.get() == self.selected_group.get():
            tk.messagebox.showinfo("ERROR", "You cant choose the same groups")

        else:
            channel = self.groups[0]
            for i in range(0, len(self.groups)):
                if self.addToGroup.get() == self.groups[i].title:
                    channel = self.groups[i]

            target_group_entity = InputPeerChannel(channel.id, channel.access_hash)
            self.inviteLink = self.client(functions.messages.ExportChatInviteRequest(channel.id))
            print("Scraped invite link from selected group " + self.inviteLink.link)

    def scrap_reader(self):
        self.client.disconnect()
        newstr = self.selected_group.get().split(" ")[0]

        input_file = str(newstr) + ".csv"
        self.users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {'username': row[0], 'id': int(row[1]), 'access_hash': int(row[2]), 'name': row[3]}
                self.users.append(user)
        self.No_of_participants = len(self.users)
        self.readySender()

    def readySender(self):

        for widget in self.master.winfo_children():
            widget.destroy()

        for widget in self.master.winfo_children():
            widget.destroy()

        l = Label(self.master, image=self.bg)
        l.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(bg=self.mainColor, fg="white", width=80, height=2, text="Message Sender", borderwidth=4,
                 relief="groove",
                 font=("Helvetica", 18, "bold")).pack(pady=20)

        tk.Label(bg="white", borderwidth=4, relief="sunken", fg=self.mainColor, width=45, height=1,
                 text="Number of Users loaded: " + str(self.No_of_participants),
                 font=("Helvetica", 12, "bold")).pack()

        container = tk.Frame(width=600, bg=self.mainColor, height=600, relief='raised', borderwidth=5)
        container.pack(fill=None, expand=False)

        Label(container, text="Amount Of Users To Message", font=("Helvetica", 12, "bold"),
              relief="sunken").grid(row=0, column=0, pady=10)

        Entry(container, textvariable=self.userAmount, width=30, font=self.large_font, relief="raised").grid(row=0,
                                                                                                             column=1,
                                                                                                             pady=10)

        Label(container, text="Messages Per number", font=("Helvetica", 12, "bold"),
              relief="sunken",
              ).grid(row=1, column=0, pady=10)

        Entry(container, textvariable=self.nOfMsgsPerN, width=30, font=self.large_font, relief="raised").grid(row=1,
                                                                                                              column=1,
                                                                                                              pady=10)

        Label(container, text="Seconds To Wait After Every Msg", font=("Helvetica", 12, "bold"),
              relief="sunken",
              ).grid(row=2, column=0, pady=10)

        Entry(container, textvariable=self.sleepTime, width=30, font=self.large_font, relief="raised").grid(row=2,
                                                                                                            column=1,
                                                                                                            pady=10)

        Label(container, text="Enter The Message", font=("Helvetica", 12, "bold"),
              relief="sunken",
              ).grid(row=3, column=0, pady=60)

        self.msg = Text(container, width=40, height=6, font=self.small_font, relief="raised")
        self.msg.grid(row=3, column=1, padx=10,pady=60)

        tk.Button(text="Start Sending", relief="raised", command=self.messageSender, bg=self.mainColor, fg="white",
                  width=35, height=1,
                  font=("Helvetica", 11, "bold")).pack(pady=10)

    def messageSender(self):

        if len(self.sleepTime.get()) == 0 or len(self.nOfMsgsPerN.get()) == 0 or len(self.userAmount.get()) == 0:
            tk.messagebox.showinfo("ERROR", "All fields must be filled!")

        else:
            total_users_contacted = 0
            messages_sent = 0
            phone_selector = 0
            limit = int(self.userAmount.get())
            message_limit_per_number = int(self.nOfMsgsPerN.get())
            SLEEP = int(self.sleepTime.get())
            phoneNumber = 0
            api_id = 0
            api_hash = 0
            while total_users_contacted <= int(limit) and phone_selector < len(self.phone_numbers):

                phoneNumber = str(self.phone_numbers[phone_selector])
                print('Phone Number using : ' + str(phoneNumber))
                api_id = str(self.api_ids[phone_selector])
                api_hash = str(self.api_hashes[phone_selector])
                self.client = TelegramClient(phoneNumber, int(api_id), api_hash)
                self.client.connect()
                while not self.client.is_user_authorized():
                    self.client.send_code_request(phoneNumber)
                    print('a verification has been sent to {}, please wait for sometime'.format(
                        phoneNumber))
                    print("Enter the code : ")
                    otp = input()
                    try:
                        self.client.sign_in(phoneNumber, otp)
                    except:
                        print('code you entered was invalid try again')
                if messages_sent >= int(message_limit_per_number):
                    phone_selector += 1
                    self.client.disconnect()

                    phoneNumber = str(self.phone_numbers[phone_selector])
                    print('changing phone to {} sleeping for 10 seconds'.format(phoneNumber))
                    time.sleep(10)
                    messages_sent = 0

                for user in self.users:
                    mode = random.choice([1, 2])
                    if mode == 2:
                        if user['username'] == "":
                            continue
                        self.receiver = self.client.get_input_entity(user['username'])
                    elif mode == 1:
                        self.receiver = InputPeerUser(user['id'], user['access_hash'])
                    else:
                        print("Invalid Mode. Exiting.")

                    try:
                        if total_users_contacted >= int(limit):
                            print("Total users that have been contacted : " + format(total_users_contacted))
                            print("Done running ")
                            break

                        self.client.send_message("me", self.msg.get("1.0", "end-1c"))

                        print('message sent to {}'.format(user['name'] + " from phone number {}".format(phoneNumber)))
                        messages_sent += 1
                        print("messages sent: " + format(messages_sent))
                        total_users_contacted += 1
                        print("total users contacted: " + format(total_users_contacted))
                        print("userAmount : " + format(limit))
                        print("print nofmsgsperuser: " + format(message_limit_per_number))
                        print("Waiting {} seconds".format(SLEEP))
                        time.sleep(SLEEP)
                    except PeerFloodError:
                        print(
                            "Getting Flood Error from telegram. Script is stopping now. Moving to next number...",
                        )
                        phone_selector += 1
                        break
                    except Exception as e:

                        print("Error: " + format(e))
                        print("Unexpected Error, Trying to continue....")
                        continue

            print("Total users that have been contacted : " + format(total_users_contacted))
            print("Done running ")
