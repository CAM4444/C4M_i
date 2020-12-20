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


def fn_clear_tv(e):
    e.delete(*e.get_children())


# PAGE

def view_teacher_page():
    db_conn = sqlite3.connect("database.db")
    global teacher_tv, view_teacher
    view_teacher = Toplevel(review_)
    view_teacher.geometry('1200x800')
    view_teacher.resizable(0,0)
    view_teacher.title("Teacher's information")
    load = Image.open("images\\g-t-b.jpg")
    render = ImageTk.PhotoImage(load)

    def view_teacher_info(e):
        selected = teacher_tv.focus()
        values = teacher_tv.item(selected, 'values')
        fr_lbl_teacher.config(text=f"{values[1]}'s information")
        xxx = pd.read_sql(f"""Select * from invigilator_db where ID = {values[0]}""", db_conn)  # query get selected data
        tv3['column'] = list(xxx.columns)
        tv3['show'] = 'headings'
        for column in tv3['column']:
            tv3.heading(column, text=column)

        teacher_rows_df = xxx.to_numpy().tolist()
        for row in teacher_rows_df:
            tv3.insert("", "end", value=row)
        tv3.pack(fill=BOTH, pady=10, padx=10)

    fr_bg_tview = Frame(view_teacher, width=1200, height=800)
    fr_bg_tview.place(x=0, y=0)  # khung background
    fr_tview = Frame(view_teacher, bg='white', width=1160, height=760)
    fr_tview.pack(padx=20, pady=20)  # khung trắng

    lbl_bg_review = Label(fr_bg_tview, image=render)
    lbl_bg_review.place(x=0, y=0)  # chứa background

    fr_teacher_info = Frame(fr_tview, bg='white')
    fr_teacher_info.place(x=20, y=20)
    fr_lbl_teacher = LabelFrame(fr_tview, bg='white')
    fr_lbl_teacher.place(x=490, y=20)

    # ScrollBar
    y_scroll = Scrollbar(fr_teacher_info)
    # TREE VIEW
    teacher_tv = ttk.Treeview(fr_teacher_info,yscrollcommand=y_scroll, height=33)
    teacher_tv.bind("<ButtonRelease-1>", view_teacher_info)
    tv3 = ttk.Treeview(fr_lbl_teacher)
    # OUTPUT DATA TO teacher_tv
    teacher_info_df = pd.read_sql("""SELECT * FROM invigilator_db ORDER BY ID;""", db_conn)
    y_scroll.pack(side=RIGHT, fill=Y)
    y_scroll.config(command=teacher_tv.yview)
    teacher_tv['column'] = list(teacher_info_df.columns)
    teacher_tv['show'] = 'headings'
    for column in teacher_tv['column']:
        teacher_tv.heading(column, text=column)
    teacher_rows_df = teacher_info_df.to_numpy().tolist()
    for row in teacher_rows_df:
        teacher_tv.insert("", "end", value=row)
    teacher_tv.pack(pady=10, padx=10)

    view_teacher.mainloop()


def review_page():
    global review_
    review_ = Toplevel()
    review_.geometry('1366x768')
    review_.resizable(0, 0)
    review_.title("Review data")
    load = Image.open("images\\Autumn.jpg")
    render = ImageTk.PhotoImage(load)
    img_name = PhotoImage(file='images\\name_database.png')
    img_view_teacher = PhotoImage(file='images\\view_teacher.png')
    img_view_course = PhotoImage(file='images\\view_course.png')
    img_view_exit = PhotoImage(file='images\\view_exit.png')
    # Frames
    fr_bg_review = Frame(review_, width=1368, height=768)
    fr_bg_review.place(x=0, y=0)  # khung background
    fr_review = Frame(review_, bg='white', width=1328, height=728)
    fr_review.pack(padx=20, pady=20)  # khung trắng

    f0 = LabelFrame(fr_review, text='Menu', bg='white', width=450, height=608)
    f0.propagate(0)
    f0.place(x=15, y=100)

    # Labels
    lbl_bg_review = Label(fr_bg_review, image=render)
    lbl_bg_review.place(x=0, y=0)  # chứa background
    lbl_name_db = Label(fr_review, image=img_name, bg='white')
    lbl_name_db.place(x=500, y=15)
    # Buttons
    btn_view_teacher = Button(f0, command=view_teacher_page, bd=0, bg='white', image=img_view_teacher,
                              activebackground='white')
    btn_view_teacher.pack(padx=20, pady=20)
    btn_view_course = Button(f0, command='fn_imp_teacher', bd=0, bg='white', image=img_view_course,
                             activebackground='white')
    btn_view_course.pack(padx=20, pady=20)
    btn_view_exit = Button(f0, command='', bd=0, bg='white', image=img_view_exit,
                           activebackground='white')
    btn_view_exit.place(x=125, y=488)
    review_.mainloop()


def analysis_page(args):
    pass


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

    btn_view = Button(fr_home, command=review_page, image=img_view, bd=0, bg='white', activebackground='white')
    btn_view.place(x=200, y=400)

    btn_run = Button(fr_home, command=analysis_page, image=img_run, bd=0, bg='white', activebackground='white')
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
