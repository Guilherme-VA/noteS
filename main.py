import tkinter as tk
from tkinter import colorchooser, simpledialog
import sqlite3, os, time, customtkinter
from screeninfo import get_monitors
from pathlib import Path
from PIL import Image, ImageDraw

os.system('cls')

start_time = time.time()

monitors = get_monitors()
monitor = monitors[1]

class noteS_auth_app(customtkinter.CTk):
    conn = sqlite3.connect("C:\\Users\\Mushr\\OneDrive\\Documents\\VSCODE\\Python\\noteS+\\database.db")
    cursor = conn.cursor()

    def __init__(self):  #FRONT-END
        super().__init__()

        self.geometry('400x200')
        self.title("noteS+")
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.usernameEntry = customtkinter.CTkEntry(self.main_frame, placeholder_text="username")
        self.usernameEntry.pack(side=tk.TOP, padx=10, pady=10)
        self.usernameEntry.focus_set()

        self.passwordEntry = customtkinter.CTkEntry(self.main_frame, placeholder_text="password", show="*")
        self.passwordEntry.pack(side=tk.TOP, padx=10, pady=10)
        self.passwordEntry.focus_set()

        self.loginButton = customtkinter.CTkButton(self.main_frame, text="login",
                                                   command=lambda: self.login_user())
        self.loginButton.pack(side=tk.LEFT, padx=10, pady=10)

        self.registerButton = customtkinter.CTkButton(self.main_frame, text="register",
                                                      command=lambda: self.register_user())
        self.registerButton.pack(side=tk.RIGHT, padx=10, pady=10)

        self.labelError = customtkinter.CTkLabel(self.main_frame, text = "no user found", bg_color="red")

    def check_user(self):
        session_username = self.usernameEntry.get()
        session_password = self.passwordEntry.get()

        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (session_username, session_password,))
        result = self.cursor.fetchall()

        self.cursor.execute("SELECT id FROM users WHERE username = ?", (session_username,))
        user_id = (str(self.cursor.fetchone())).strip("()").replace(",", "")

        if result:
            print("check_user() > user in DB")
            print(f"check_user() > username: {session_username}")
            print(f"check_user() > password: {session_password}")
            print(f"check_user() > user_id: {user_id}")
            return True
        else:
            print("check_user() < user not in DB")
            return False

    def login_user(self):
        session_username = self.usernameEntry.get()
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (session_username,))
        user_id = (str(self.cursor.fetchone())).strip("()").replace(",", "")

        if self.check_user():
            self.destroy()
            app = noteS_main_app(user_id)
            app.mainloop()
        else:
            self.labelError.place(x=10, y=10)
            self.labelError.tkraise()

    def register_user(self):
        session_username = self.usernameEntry.get()
        session_password = self.passwordEntry.get()

        if not session_password == "":
            try:
                self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (session_username, session_password))
                self.conn.commit()

                self.cursor.execute("SELECT id FROM users WHERE username = ?", (session_username,))
                user_id = (str(self.cursor.fetchone())).strip("()").replace(",", "")

                directory = Path("C:\\Users\\Mushr\\OneDrive\\Documents\\VSCODE\\Python\\noteS+\\user_data\\" + user_id)

                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    print("register_user() > directory created")

                print(f"register_user() > user registered with id {user_id}")

            except sqlite3.Error as error:
                print("register_user() > ", error)
                print(f"register_user() > username {session_username} in use")
        else:
            print("register_user() > input password")

class noteS_main_app(customtkinter.CTk):
    conn = sqlite3.connect("C:\\Users\\Mushr\\OneDrive\\Documents\\VSCODE\\Python\\noteS+\\database.db")
    cursor = conn.cursor()

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.after(100, lambda: self.maximize_and_stay_maximized(monitor))

        self.title(f"noteS+ {user_id}")
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.image = Image.new("RGB", (monitor.width, monitor.height), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.canvas = customtkinter.CTkCanvas(self.main_frame, bg = "white")
        self.canvas.pack(fill =tk.BOTH, expand=True, padx=15, pady=15)

        self.brush_size = 2
        self.brush_color = "#000000"

        self.add_lines()

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<B3-Motion>", self.erase_area)
        self.canvas.bind("<ButtonRelease-3>", self.add_lines_release)

    # MENU BUTTONS

        self.choose_color_Button = customtkinter.CTkButton(self, text="choose color",
                                                           command=lambda: self.choose_color())
        self.choose_color_Button.pack(side=tk.LEFT, padx=10, pady=10)

        self.choose_size_Button = customtkinter.CTkButton(self, text="choose size",
                                                           command=lambda: self.choose_size())
        self.choose_size_Button.pack(side=tk.LEFT, padx=10, pady=10)

        self.clear_button = customtkinter.CTkButton(self, text="clear",
                                                    command=lambda: self.clear())
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_button = customtkinter.CTkButton(self, text="save",
                                                   command=lambda: self.save())
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

    def add_lines_release(self, event):
        self.add_lines()

    def erase_area(self, event):
        user_color =  self.brush_color
        self.brush_color = "#FFFFFF"
        
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.brush_color, outline=self.brush_color)
        self.draw.ellipse([x1,y1,x2,y2], fill=self.brush_color, outline=self.brush_color)

        self.brush_color = user_color
        
    def add_lines(self):
        line_spacing = 50
        for i in range(0, 1920, line_spacing):
            self.canvas.create_line(1, i, 1920, i, fill="lightgray")
            self.draw.line((1, i, 1920, i), fill="lightgray")

    def paint(self, event):
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.brush_color, outline=self.brush_color)
        self.draw.ellipse([x1,y1,x2,y2], fill=self.brush_color, outline=self.brush_color)

    def choose_color(self):
        self.brush_color = colorchooser.askcolor(color=self.brush_color)[1]

    def choose_size(self):
        input_dialog = simpledialog.askinteger("choose size","brush size from 1-30", minvalue=1, maxvalue=30)
        if input_dialog:
            self.brush_size = input_dialog

    def clear(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (1920, 1080), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.add_lines()

    def save(self):
        input_dialog = customtkinter.CTkInputDialog(title="file name", text="input a name for the file")

        file_path = f"C:\\Users\\Mushr\\OneDrive\\Documents\\VSCODE\\Python\\noteS+\\user_data\\{self.user_id}\\{input_dialog.get_input()}.png"

        self.image.save(file_path)
        print(f"save() >image save {file_path}")
    
    def maximize_and_stay_maximized(self, monitor):
        self.geometry(f"{monitor.width}x{monitor.height}")
        self.update_idletasks()
        self.state("zoomed")

#runtime
end_time = time.time()
elapsed = end_time - start_time
print(f"runtime: {elapsed}")
#runtime


if __name__ == "__main__":
    
    app = noteS_auth_app()
    app.mainloop()

print(0)
