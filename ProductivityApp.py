import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import mysql.connector
from datetime import datetime, date, timedelta
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

window = tk.Tk()
window.minsize(900, 500)
window.title("Productivity App")
window.iconbitmap("icon.ico")
bg_image = Image.open("new_.png").resize((1280, 730))
bg_image = ImageTk.PhotoImage(bg_image)
backdrop = tk.Label(window, image=bg_image)
backdrop.place(relwidth=1, relheight=1)

class App:
    def __init__(self):
        self.create_widgets()

    def create_widgets(self):
        self.todo_list = tk.Listbox(backdrop, background="#bfa9b6",font=("Book Antiqua", 12))
        self.todo_list.place(relx=0.7, rely=0.135, relwidth=0.28, relheight = 0.54)

        tk.Button(
            backdrop, 
            text="Delete Task", 
            background="#e1e1ca",
            font=("Book Antiqua", 12), 
            command=self.delete_task).place(relx=0.85, rely=0.7, relwidth=0.13, relheight=0.08)
       
        tk.Button(
            backdrop, text="Complete Task", 
            background="#e1e1ca",font=("Book Antiqua", 12), 
            command=self.complete_task).place(relx=0.7, rely=0.7, relwidth=0.13, relheight=0.08)

        tk.Button(
            backdrop, 
            text="Get Report", 
            background="#e1e1ca",
            font=("Book Antiqua", 12), 
            command = self.get_report).place(relx=0.75, rely=0.8, relwidth=0.2, relheight=0.08)

        self.time_label = tk.Label(backdrop, font=("Book Antiqua", 16), background="#44443d", foreground="white")
        self.time_label.place(relx=0.86, rely=0.02, relwidth=0.15, relheight=0.1)
        self.get_time()

        self.cal = Calendar(
            backdrop, 
            seletmode="day", 
            date_pattern='yyyy-mm-dd', 
            background="#e1e1ca", 
            othermonthwebackground="#929e96",
            foreground="black", 
            selectbackground="#a47086", 
            normalbackground="#ee9f9e", 
            weekendbackground="#72b0ae", 
            weekendforeground="black", 
            headersbackground="#bfa9b6", 
            font=("Book Antiqua", 10))
        
        self.cal.place(relx=0.3, rely=0.135, relwidth=0.37, relheight=0.54)
        self.cal.bind("<<CalendarSelected>>", self.show_notes)

        self.task_entry = tk.Entry(backdrop, background="#bfa9b6", font=("Book Antiqua", 12))
        self.task_entry.place(relx=0.3, rely=0.7, relwidth = 0.29, relheight= 0.08)

        tk.Button(
            backdrop, 
            text="Add", 
            command = self.add_task, 
            background="#e1e1ca",
            font=("Book Antiqua", 12)).place(relx=0.6, rely=0.7, relheight=0.08, relwidth=0.07)

        self.combo()
    
        self.study_list = tk.Listbox(backdrop, background="#bfa9b6",font=("Book Antiqua", 12))
        self.study_list.place(relx=0.02, rely=0.48, relwidth=0.25, relheight = 0.3)

        tk.Button(
            backdrop, 
            text="Get record for selected date", 
            background="#e1e1ca", 
            font=("Book Antiqua", 12), 
            command=self.show_study).place(relx=0.02, rely=0.8, relwidth=0.25, relheight=0.08)
    
    def get_report(self):
        self.connections()
        self.cursor.execute("SELECT complete from events")
        all = self.cursor.fetchall()

        count_zeros = 0
        count_ones = 0
   
        for row in all:
            if row[0] == 0:
                count_zeros += 1
            else:
                count_ones += 1

        labels = ["Task Completed", 'Task Not completed']
        counts = [count_ones, count_zeros]
        today = date.today()
        one_week_ago = today - timedelta(days=7)

        self.cursor.execute(
            f"SELECT subjects, SUM(TIME_TO_SEC(time_spent)) FROM tasks WHERE date BETWEEN '{one_week_ago}' AND '{today}' GROUP BY subjects")
        study_data = self.cursor.fetchall()

        self.close_connections()

        subjects = []
        durations_hours = []

        for row in study_data:
            subjects.append(row[0])
            duration_seconds = row[1]
            duration_hours = duration_seconds / (3600)
            durations_hours.append(duration_hours)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].bar(labels, counts, color="#bfa9b6", width=0.5)
        axes[0].set_xlabel('Values')
        axes[0].set_ylabel('Counts')
        axes[0].set_title('Total Tasks')

        axes[1].bar(subjects, durations_hours, color="#bfa9b6")
        axes[1].set_xlabel('Subjects')
        axes[1].set_ylabel('Total Hours')
        axes[1].set_title('Total Hours Studied This Week')

        fig.tight_layout()
        plt.show()

    def combo(self):
        try: 
            self.options = self.get_subject()
            self.options.append("Add a new subject")

            self.combo_box = ttk.Combobox(window, values=self.options, state="readonly")
            self.combo_box.bind("<<ComboboxSelected>>", self.on_select)
            self.combo_box.place(relx=0.02, rely=0.135, relheight=0.06, relwidth=0.25)
        except: messagebox.showerror("!", "Try connecting to sql")
 
    def on_select(self, event):
        selected_item = self.combo_box.get()
        if selected_item == self.options[-1]:
            self.new_window = tk.Toplevel(window)
            self.new_window.title("New Window")
            self.new_window.configure(background="#e1e1ca")
            self.new_window.minsize(200, 100)
            self.new_window.maxsize(200, 100)

            tk.Label(self.new_window, text="Add new subject:", background="#e1e1ca").place(relx=0.1, rely=0.1)
            self.entry = tk.Entry(self.new_window, background="#bfa9b6")
            self.entry.place(relx=0.13, rely=0.15)
            button = tk.Button(self.new_window, text="Add Subject", command = self.add_subject, background="#e1e1ca")
            button.place(relx=0.3, rely=0.4)

    def add_subject(self):
        date_ = self.cal.get_date()
        time = "00:00:00"
        entry = self.entry.get().strip()
        if entry != "":
            self.connections()

            add_query = "INSERT INTO tasks(subjects, time_spent, date) VALUES(%s, %s, %s)"
            self.cursor.execute(add_query, (entry, time, date_))
            self.connection.commit()
            self.close_connections()
            self.combo()
            self.new_window.destroy()
        else:
            messagebox.showwarning("!", "Add a name to the new subject!")

    def save_time(self,el):
        date_ = self.cal.get_date()
        hours = int(el // 3600)
        minutes = int((el % 3600) // 60)
        seconds = int(el % 60)

        time_format = f'{hours :02d}:{minutes :02d}:{seconds :02d}'
        gs = self.combo_box.get()

        self.connections()

        insert_query = "INSERT INTO tasks (subjects, time_spent, date) VALUES (%s, %s, %s)"
        data = (gs, time_format, date_)
        self.cursor.execute(insert_query, data)

        self.connection.commit()
        self.close_connections()

    def get_subject(self):
        try:
            self.connections()
            self.cursor.execute("SELECT DISTINCT subjects FROM tasks")
            names = [row[0] for row in self.cursor.fetchall()]
            self.connection.commit()
            self.close_connections()
            return names
        except:
            messagebox.showerror("Error", "Cannot open Application")

    def get_time(self):
        self.time_label.configure(text=f'{datetime.now().strftime("%H:%M:%S")}\n    {datetime.now().strftime("%A")}')
        backdrop.after(1000, self.get_time)

    def add_task(self):
        date_ = self.cal.get_date()
        title_ = self.task_entry.get()

        if not title_:
            messagebox.showerror("Error", "Please enter a task.")
            return

        self.connections()
        insert_query = "INSERT INTO events (date, description) VALUES (%s, %s)"
        data = (date_, title_)
        self.cursor.execute(insert_query, data)
        self.connection.commit()

        messagebox.showinfo("Success", "Task added successfully.")
        self.task_entry.delete(0, tk.END)

        self.show_notes()

        self.close_connections()

    def complete_task(self):
        selected_indices = self.todo_list.curselection()
        
        if selected_indices:
            for index in selected_indices:
                current_text = self.todo_list.get(index)
                if "done!" not in current_text:
                    new_text = current_text + " done!"     
                    self.connections()

                    update_query = "UPDATE events SET description = %s WHERE description = %s"
                    self.cursor.execute(update_query,(new_text, current_text))

                    complete_query = "UPDATE events SET complete = 1 WHERE description = %s"
                    self.cursor.execute(complete_query, (new_text, ))

                    self.connection.commit()
                    self.show_notes()

                    self.close_connections()
                else: messagebox.showinfo("!", "This task is already done!")
        else:
            messagebox.showerror("Error", "Please select a task to mark it complete!")
            return

    def delete_task(self):
        selected_task = self.todo_list.get(tk.ACTIVE)

        if not selected_task:
            messagebox.showerror("Error", "Please select a task to delete.")
            return
        
        self.connections()
        delete_query = "DELETE FROM events WHERE description = %s"
        self.cursor.execute(delete_query, (selected_task,))
        self.connection.commit()

        self.close_connections()

        self.show_notes()

    def show_study(self, *event):
        date_ = self.cal.get_date()
        self.study_list.delete(0, tk.END)
        self.study_list.insert(tk.END, f"Date: {date_}\n")
        self.connections()

        sql = "SELECT subjects, time_spent FROM tasks WHERE date = %s"
 
        self.cursor.execute(sql, (date_,))
        notes = self.cursor.fetchall()
        self.close_connections()

        for note in notes:
            self.study_list.insert(tk.END, note)

    def show_notes(self, *event):
        date_ = self.cal.get_date()
        self.todo_list.delete(0, tk.END)
        self.todo_list.insert(tk.END, f"Date: {date_}\n")
        self.connections()
        sql = "SELECT * FROM events WHERE date = %s"
        self.cursor.execute(sql, (date_,))
        notes = self.cursor.fetchall()
        self.close_connections()

        for note in notes:
            self.todo_list.insert(tk.END, note[1])

    def connections(self):
        try:
            self.connection = mysql.connector.connect(host="localhost",user="root",password="",database="notion_app")
            self.cursor = self.connection.cursor()
        except:
            messagebox.showerror("Error", "Error While connecting to Database!")
    
    def close_connections(self):
        self.cursor.close()
        self.connection.close()

class Stopwatch:
    def __init__(self):
        self.stopwatch_time = App()
        self.running = False
        self.elapsed_time = 0
        self.start_time = None
        self.create_buttons()
    
    def create_buttons(self):

        self.time_label = tk.Label(backdrop, font=("Book Antiqua", 40), text="00:00:00", background="#474642",foreground="white")
        self.time_label.place(relx=0.03, rely=0.2, relwidth=0.24, relheight=0.15)

        tk.Button(
            backdrop, 
            text="Start", 
            font=("Book Antiqua", 12), 
            background="#e1e1ca",
            command=self.start).place(relx=0.02, rely=0.38, relwidth =0.07)

        tk.Button(
            backdrop, 
            text="Pause",
            font=("Book Antiqua", 12),
            background="#e1e1ca", 
            command=self.pause).place(relx=0.11, rely=0.38, relwidth=0.07)

        tk.Button(
            backdrop, 
            text="Stop",
            font=("Book Antiqua", 12),
            background="#e1e1ca", 
            command=self.stop).place(relx=0.198, rely=0.38, relwidth=0.07)

    def start(self):
        if self.stopwatch_time.cal.get_date() == str(date.today()) and self.stopwatch_time.combo_box.get() != "" and self.stopwatch_time.combo_box.get() != "Add a new subject":
            if not self.running:
                self.running = True
                if not self.start_time:
                    self.start_time = datetime.now()
                else:
                    self.start_time = datetime.now() - timedelta(seconds=self.elapsed_time)
                self.update()
        else:
            messagebox.showerror("Error", "Please select Today's date from the Calendar or Select a Subject!")

    def pause(self):
        if self.running:
            self.running = False
            self.elapsed_time = (datetime.now() - self.start_time).total_seconds()

    def stop(self):
        if self.running:
            self.pause()
        if self.elapsed_time > 0:
            self.running = False
            self.stopwatch_time.save_time(self.elapsed_time)
        self.elapsed_time = 0
        self.start_time = None
        self.update()

    def update(self):
        if self.running:
            self.elapsed_time = (datetime.now() - self.start_time).total_seconds()
        time_str = self.format_time(self.elapsed_time)
        self.time_label.config(text=time_str)
        window.after(100, self.update)
   
    @staticmethod
    def format_time(time):
        hours = int(time//3600)
        minutes = int((time % 3600) // 60)
        seconds = int(time % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

App()
Stopwatch()
window.mainloop()