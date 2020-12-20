# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sqlite3
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from PIL import Image, ImageTk


# Functions


def fn_imp_teacher():
    db_con = sqlite3.connect("database.db")
    c = db_con.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS invigilator_db; 
        CREATE TABLE IF NOT EXISTS invigilator_db(
            ID INT,
            Full_Name TEXT,
            PRIMARY KEY(ID)
            ); 
        """)
    teacher_file = filedialog.askopenfilename(initialdir='/',
                                              title='Select Teacher dataset',
                                              filetype=(('xlsx files', '*.xlsx'), ('All files', '*,*')))
    if teacher_file:
        try:
            inviglator_df = pd.read_excel(teacher_file, sheet_name='Sheet1', header=0)
        except ValueError:
            messagebox.showerror("Error!", 'Invalid File')
            return None
        except FileNotFoundError:
            messagebox.showerror("Error!", "File not found!")
            return None
    try:
        inviglator_df.to_sql("invigilator_db", db_con, if_exists="append", index=False)
    except sqlite3.OperationalError:
        messagebox.showerror("Error!",
                             f"Unable to execute file into database.\nFile path: {teacher_file}.\nPlease try again!")
        return None
    db_con.commit()
    db_con.close()


def fn_imp_course():
    db_con = sqlite3.connect("database.db")
    c = db_con.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS schedule_db; 
        CREATE TABLE IF NOT EXISTS schedule_db(
            CourseID INTEGER NOT NULL,
            CourseName TEXT,
            TestDate Date, 
            ShiftOD INTEGER,
            Room TEXT,
            QuantityOfInvigilator INTEGER,
            PRIMARY KEY(CourseID)
        ); 
            """)
    exam_file = filedialog.askopenfilename(initialdir='/',
                                           title='Select Teacher dataset',
                                           filetype=(('xlsx files', '*.xlsx'), ('All files', '*,*')))
    if exam_file:
        try:
            schedule_df = pd.read_excel(exam_file,  # schedule_df = test_schedule
                                        sheet_name='Sheet1',
                                        header=0,
                                        skiprows=7,
                                        usecols=["STT", "Tên MH", "Ngày thi", "Ca Thi", "Phòng Thi", "Số CBCT"],
                                        nrows=612)
        except ValueError:
            messagebox.showerror("Error!",
                                 f"Unable to execute file into database.\nFile path: {exam_file}.\nPlease try again!")
            return None
        except FileNotFoundError:
            messagebox.showerror("Error!", "File note found!")
            return None

    schedule_df = schedule_df.rename(
        columns={'STT': 'CourseID', 'Tên MH': 'CourseName', 'Ngày thi': 'TestDate', 'Ca Thi': 'ShiftOD',
                 'Phòng Thi': 'Room', 'Số CBCT': 'QuantityOfInvigilator', })
    schedule_df.sort_values(by=['TestDate', 'ShiftOD'], inplace=True, ascending=True)
    schedule_df.to_sql('schedule_db', db_con, if_exists='append', index=False)
    db_con.commit()
    db_con.close()


def home_page():
    try:
        root_.destroy()
    except:
        pass
    home_ = Tk()
    home_.geometry("1366x768")
    home_.resizable(0, 0)
    home_.title("Exam invigilator scheduler")
    load = Image.open("images\\Autumn.jpg")
    render = ImageTk.PhotoImage(load)
    img_view = PhotoImage(file="images\\view_data.png")
    img_run = PhotoImage(file="images\\run_algorithm.png")
    # Frames
    fr_home = Frame(home_, width=1368, height=768)
    fr_home.place(x=0, y=0)
    # Labels
    lbl_bg_home = Label(fr_home, image=render)
    lbl_bg_home.place(x=0, y=0)

    btn_view = Button(fr_home,image=img_view, bd=0, bg='white', activebackground='white')
    btn_view.place(x=200, y=400)

    btn_run = Button(fr_home, image=img_run, bd=0, bg='white', activebackground='white')
    btn_run.place(x=780, y=400)
    home_.mainloop()

def welcome_page():
    # Frames
    fr_welcome = Frame(root_, height=800, width=720, bg='#dad299')
    fr_welcome.place(x=0, y=0)

    # Labels
    lbl_name_welcome = Label(fr_welcome, image=img_title, bg='#dad299')
    lbl_name_welcome.place(x=100, y=60)
    # Buttons
    btn_imp_teacher = Button(fr_welcome, command=fn_imp_teacher, bd=0, bg='#dad299', image=img_imp_teacher,
                             activebackground='#dad299')  # nhập file teacher
    btn_imp_teacher.place(x=200, y=250)
    btn_imp_course = Button(fr_welcome, command=fn_imp_course, bd=0, bg='#dad299', image=img_imp_course,
                            activebackground='#dad299')  # nhập file course
    btn_imp_course.place(x=202, y=380)

    btn_GAs = Button(fr_welcome, command=home_page, bd=0, bg='#dad299', image=img_started,
                     activebackground='#dad299')  # gọi home window
    btn_GAs.place(x=202, y=600)


root_ = Tk()
root_.geometry("720x800")  # width x height
root_.resizable(0, 0)
root_.title('Exam invigilator scheduler')
# IMG
img_title = PhotoImage(file='images\\name.png')
img_imp_teacher = PhotoImage(file='images\\imp_teacher.png')
img_imp_course = PhotoImage(file='images\\imp_course.png')
img_started = PhotoImage(file='images\\started.png')

welcome_page()
root_.mainloop()
