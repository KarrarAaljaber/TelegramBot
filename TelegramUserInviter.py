import csv
import time
import tkinter as tk
import tkinter.filedialog as fd
import traceback

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

    userAmount = None
    nOfMsgsPerN = None
    sleepTime = None
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
        self.window_width = 600
        self.window_height = 500
        self.receiver = None
        self.x_cordinate = int((self.screen_width / 2) - (self.window_width / 2))
        self.y_cordinate = int((self.screen_height / 2) - (self.window_height / 2))

        self.singleMessage = tk.IntVar()
        self.master.geometry(
            "{}x{}+{}+{}".format(self.window_width, self.window_height, self.x_cordinate, self.y_cordinate))
        self.master.configure(background='orange')

        self.large_font = ('Verdana', 15)
        self.small_font = ('Verdana', 11)

        tk.Label(bg="black", fg="white", width=40, height=2, text="TeleGroup User Adder",
                 font=("Helvetica", 18, "bold")).pack()

        tk.Label(text="", bg="orange", height=1).pack()

        tk.Button(command=self.loadFile, text="Load Accounts From File(.txt)", bg="green", fg="white", width=45,
                  height=1,
                  font=("Helvetica", 11, "bold")).pack()

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

        tk.Label(bg="black", fg="white", width=40, height=2, text="TeleGroup User Adder",
                 font=("Helvetica", 18, "bold")).pack()

        tk.Label(text="", bg="orange", height=1).pack()

        tk.Button(command=self.loadFile, text="Load Accounts From File(.txt)", bg="green", fg="white", width=45,
                  height=1,
                  font=("Helvetica", 11, "bold")).pack()

        tk.Label(bg="black", fg="white", width=20, height=2, text="Accounts loaded: " + str(len(self.phone_numbers)),
                 font=("Helvetica", 12, "bold")).pack()
        tk.Label(text="", bg="orange", height=2).pack()

        tk.Button(text="Connect all accounts", command=self.connectToAllClients, bg="green", fg="white", width=35,
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

        tk.Label(text="Scrape From", font=("Helvetica", 12, "bold"), width=30, bg="lightgreen").pack()
        selector = tk.OptionMenu(self.master, self.selected_group, *groupsTitles, command=self.getUsers)
        selector.config(width=30)
        selector.pack()

        tk.Label(text="Add Users To", font=("Helvetica", 12, "bold"), width=30, bg="lightgreen").pack()
        addTo = tk.OptionMenu(self.master, self.addToGroup, *groupsTitles, command=self.getInviteLink)
        addTo.config(width=30)
        addTo.pack()

        start = tk.Button(text="Continue", command=self.scrap_reader, bg="green", fg="white", width=35, height=1,
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

        tk.Label(bg="black", fg="white", width=40, height=2, text="TeleGroup User Adder",
                 font=("Helvetica", 18, "bold")).pack()

        tk.Label(text="", bg="orange", height=1).pack()
        tk.Label(text="Number of Users loaded: " + str(self.No_of_participants), width=35, height=1, bg="white",
                 fg="black").pack()
        tk.Label(text="", bg="orange", height=1).pack()
        tk.Label(text="How many users do you want to send an invite message to?", font=("Helvetica", 12, "bold"),
                 width=50, bg="lightgreen").pack()
        self.userAmount = tk.Entry(width=20, font=self.large_font)
        self.userAmount.pack()
        tk.Label(text="Enter the number of messages per number?", font=("Helvetica", 12, "bold"),
                 width=50,
                 bg="lightgreen").pack()
        self.nOfMsgsPerN = tk.Entry(width=20, font=self.large_font)
        self.nOfMsgsPerN.pack()

        tk.Label(text="Enter how many seconds to wait after every msg", font=("Helvetica", 12, "bold"),
                 width=50,
                 bg="lightgreen").pack()
        self.sleepTime = tk.Entry(width=20, font=self.large_font)
        self.sleepTime.pack()

        tk.Label(text="Enter a message", font=("Helvetica", 12, "bold"),
                 width=50,
                 bg="lightgreen").pack()
        self.msg = tk.Text(width=20, height=3, font=self.small_font)
        self.msg.pack()

        check = tk.Checkbutton(text="Single message?", onvalue=1, offvalue=0, variable=self.singleMessage)
        check.pack()

        tk.Label(text="", bg="orange", height=2).pack()
        tk.Button(text="START", command=self.messageSender, bg="green", fg="white", width=35, height=1,
                  font=("Helvetica", 11, "bold")).pack()

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
                        if self.singleMessage.get() == 1:
                            self.client.send_message('me', self.msg.get("1.0", "end-1c") + "\n" + self.inviteLink.link)
                        else:
                            self.client.send_message('me', self.msg.get("1.0", "end-1c"))
                            self.client.send_message('me', self.inviteLink.link)

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
