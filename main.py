# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math
import random
import sqlite3
import threading
import time
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
from multiprocessing import Queue

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
                             f"File path: {teacher_file}.\n\nUnable to import selected file into database.\nPlease try again!")
        return None
    except UnboundLocalError:
        messagebox.showerror("Error!", "You just canceling import TEACHER.\nPlease try again!")
    db_con.commit()
    db_con.close()


def fn_imp_course():
    try:
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
                                     f"File path: {exam_file}.\n\nUnable to import selected file into database.\nPlease try again!")
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
    except UnboundLocalError:
        messagebox.showerror("Error!", "You just canceling import COURSE.\nPlease try again!")
    return btn_GAs.config(state='active')

def fn_clear_tv(e):
    e.delete(*e.get_children())


# PAGE
############ UNFINISHED #############
def view_teacher_page():
    db_conn = sqlite3.connect("database.db")
    view_teacher = Toplevel(review_)
    view_teacher.geometry('1200x800')
    view_teacher.resizable(0, 0)
    view_teacher.title("Teacher's information PAGE")
    load = Image.open("images\\g-t-b.jpg")
    render = ImageTk.PhotoImage(load)
    img_name = PhotoImage(file='images\\name_teacher_info.png')

    def view_teacher_info(e):
        try:
            selected = teacher_tv.focus()
            values = teacher_tv.item(selected, 'values')
            fr_lbl_teacher.config(text=f"{values[1]}'s information")
            xxx = pd.read_sql(f"""SELECT CourseID, CourseName, Room, ShiftOD, TestDate
            FROM 
                (SELECT assign_db.CourseID,  schedule_db.CourseName, schedule_db.Room, schedule_db.ShiftOD, schedule_db.TestDate, 
                invigilator_db.ID Invigilator 
                FROM assign_db, invigilator_db, schedule_db
                WHERE assign_db.ID=invigilator_db.ID and schedule_db.CourseID = assign_db.CourseID  
                ORDER BY schedule_db.TestDate) 
            WHERE Invigilator = {values[0]}""", db_conn)  # query get selected data
            fn_clear_tv(tv3)
            tv3['column'] = list(xxx.columns)
            tv3['show'] = 'headings'
            for column in tv3['column']:
                tv3.heading(column, text=column)
            tv3.column('#1', width=70, stretch=0, anchor='n')
            tv3.column('#2', width=200, stretch=0, anchor='w')
            tv3.column('#3', width=70, stretch=0, anchor='n')
            tv3.column('#4', width=70, stretch=0, anchor='n')
            tv3.column('#5', stretch=0, anchor='n')
            teacher_rows_df = xxx.to_numpy().tolist()
            for row in teacher_rows_df:
                tv3.insert("", "end", value=row)
            tv3.pack(fill=BOTH, pady=10, padx=10)
        except sqlite3.OperationalError:
            messagebox.showinfo("Info!", "Nothing to show yet!\nPlease run the algorithm first.")
            review_.destroy()
            return home_
        except pd.io.sql.DatabaseError:
            messagebox.showinfo("Info!", "Nothing to show yet!\nPlease run the algorithm first.")
            review_.destroy()
            return home_
    fr_bg_tview = Frame(view_teacher, width=1200, height=800)
    fr_bg_tview.place(x=0, y=0)  # khung background
    fr_tview = Frame(view_teacher, bg='white', width=1160, height=760)
    fr_tview.pack(padx=20, pady=20)  # khung trắng

    lbl_bg_review = Label(fr_bg_tview, image=render)
    lbl_bg_review.place(x=0, y=0)  # chứa background
    lbl_name_db = Label(fr_tview, image=img_name, bg='white')
    lbl_name_db.place(x=500, y=20)

    fr_teacher_info = Frame(fr_tview, bg='white')
    fr_teacher_info.place(x=20, y=20)
    fr_lbl_teacher = LabelFrame(fr_tview, bg='white', font=20)
    fr_lbl_teacher.place(x=490, y=120)

    # ScrollBar
    y_scroll = Scrollbar(fr_teacher_info)
    # TREE VIEW
    teacher_tv = ttk.Treeview(fr_teacher_info, yscrollcommand=y_scroll, height=33)
    teacher_tv.bind("<ButtonRelease-1>", view_teacher_info)
    tv3 = ttk.Treeview(fr_lbl_teacher,height=15)  # chứa thông tin được click
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


def view_course_page():
    db_conn = sqlite3.connect("database.db")
    view_course = Toplevel(review_)
    view_course.geometry('1200x800')
    view_course.resizable(0, 0)
    view_course.title("Course's information PAGE")
    load = Image.open("images\\Kye-Meh.jpg")
    render = ImageTk.PhotoImage(load)
    img_name = PhotoImage(file='images\\name_database.png')
    # FRAMES
    fr_bg_cview = Frame(view_course, width=1200, height=800)
    fr_bg_cview.place(x=0, y=0)  # khung background
    fr_cview = Frame(view_course, bg='white', width=1160, height=760)
    fr_cview.pack(padx=20, pady=20)  # khung trắng
    fr_course_info = Frame(fr_cview, bg='white')
    fr_course_info.pack(padx=20, pady=120, fill=BOTH)
    # LABELS
    lbl_bg_review = Label(fr_bg_cview, image=render)
    lbl_bg_review.place(x=0, y=0)  # chứa background (render)
    lbl_name_db = Label(fr_cview, image=img_name, bg='white')
    lbl_name_db.place(x=450, y=20)  # chứa tên (img_name)
    # SCROLL BAR
    y_scroll = Scrollbar(fr_course_info)
    # TREE VIEW
    tv2 = ttk.Treeview(fr_course_info, yscrollcommand=y_scroll, height=33)
    # OUTPUT DATA TO TREE VIEW 2
    schedule_info_df = pd.read_sql("""SELECT * FROM schedule_db ORDER BY CourseID""", db_conn)
    y_scroll.pack(side=RIGHT, fill=Y)
    y_scroll.config(command=tv2.yview)
    tv2['column'] = list(schedule_info_df.columns)
    tv2['show'] = 'headings'
    for column in tv2['column']:
        tv2.heading(column, text=column)
    tv2.column('#1', width=70, stretch=0)
    teacher_rows_df = schedule_info_df.to_numpy().tolist()
    for row in teacher_rows_df:
        tv2.insert("", "end", value=row)

    tv2.pack(fill=BOTH, expand=TRUE)

    view_course.mainloop()


def review_page():
    global review_
    review_ = Toplevel(home_)
    review_.geometry('1366x768')
    review_.resizable(0, 0)
    review_.title("Review data PAGE")
    load = Image.open("images\\Autumn.jpg")
    render = ImageTk.PhotoImage(load)
    img_name = PhotoImage(file='images\\name_blue_black.png')
    img_view_teacher = PhotoImage(file='images\\view_teacher.png')
    img_view_course = PhotoImage(file='images\\view_course.png')
    img_view_exit = PhotoImage(file='images\\view_exit.png')
    img_view_schedule = PhotoImage(file='images\\button_schedule.png')
    load1 = Image.open('images\\temp.jpg')
    img_temp =ImageTk.PhotoImage(load1)
    # Frames
    fr_bg_review = Frame(review_, width=1368, height=768)
    fr_bg_review.place(x=0, y=0)  # khung background
    fr_review = Frame(review_, bg='white', width=1328, height=728)
    fr_review.pack(padx=20, pady=20)  # khung trắng

    f0 = LabelFrame(fr_review, text='Menu', bg='white', width=360, height=608,
                    font=("Helvetica", 20))
    f0.propagate(0)
    f0.place(x=15, y=100)
    lbl_tv5 = Label(fr_review,image=img_temp)
    lbl_tv5.place(x=380, y=120)
    #rs = pd.read_excel("output.xlsx")
# THÊM 1 button để hiện treeview5

    # Labels
    lbl_bg_review = Label(fr_bg_review, image=render)
    lbl_bg_review.place(x=0, y=0)  # chứa background
    lbl_name_db = Label(fr_review, image=img_name, bg='white')
    lbl_name_db.place(x=500, y=15)  # chứa tên

    def view_schedule():
        try:
            db_conn=sqlite3.connect("database.db")
            rs = pd.read_sql("""SELECT assign_db.CourseID,  schedule_db.CourseName, schedule_db.Room, schedule_db.ShiftOD, schedule_db.TestDate, schedule_db.QuantityOfInvigilator, GROUP_CONCAT(invigilator_db.Full_Name) Invigilator
        FROM assign_db, invigilator_db, schedule_db
        WHERE assign_db.ID=invigilator_db.ID and schedule_db.CourseID = assign_db.CourseID
        GROUP BY assign_db.CourseID
        ORDER BY assign_db.CourseID;""",db_conn)
            tv5 = ttk.Treeview(lbl_tv5, height=27)
            tv5.delete(*tv5.get_children())

            tv5['column'] = list(rs.columns)
            tv5['show'] = 'headings'
            for column in tv5['column']:
                tv5.heading(column, text=column)
            tv5.column('#1', width=70, stretch=0, anchor='n')
            tv5.column('#2', width=90, stretch=0, anchor='w')
            tv5.column('#3', width=70, stretch=0, anchor='n')
            tv5.column('#4', width=50, stretch=0, anchor='n')
            tv5.column('#5', stretch=0, anchor='n')
            tv5.column('#6', width=70, stretch=0, anchor='n')
            tv5.column('#7', width=350, stretch=0, anchor='w')
            teacher_rows_df = rs.to_numpy().tolist()
            for row in teacher_rows_df:
                tv5.insert("", "end", value=row)

            tv5.pack(fill=BOTH, pady=10, padx=10)
        except sqlite3.OperationalError:
            messagebox.showinfo("Info!", "Nothing to show yet!\nPlease run the algorithm first.")
            review_.destroy()
            return home_
        except pd.io.sql.DatabaseError:
            messagebox.showinfo("Info!", "Nothing to show yet!\nPlease run the algorithm first.")
            review_.destroy()
            return home_

    def exit_rv():
        review_.destroy()

    # Buttons
    btn_schedule = Button (f0, command=view_schedule, bd=0, bg='white', image=img_view_schedule,
                              activebackground='white')
    btn_schedule.pack(padx=20, pady=20)
    btn_view_teacher = Button(f0, command=view_teacher_page, bd=0, bg='white', image=img_view_teacher,
                              activebackground='white')
    btn_view_teacher.pack()
    btn_view_course = Button(f0, command=view_course_page, bd=0, bg='white', image=img_view_course,
                             activebackground='white')
    btn_view_course.pack(padx=20, pady=20)
    btn_view_exit = Button(f0, command=exit_rv, bd=0, bg='white', image=img_view_exit,
                           activebackground='white')
    btn_view_exit.place(x=125, y=488)
    review_.mainloop()


def analysis_page():
    queue = Queue()
    analyze_window = Toplevel(home_)
    analyze_window.title(f"Genetic algorithm")
    analyze_window.geometry('1366x768')
    analyze_window['bg']='#dad299'
    analyze_window.resizable(0,0)
    # analyze_window.iconbitmap('chromosome.ico')
    db_conn = sqlite3.connect("database.db")
    cursor = db_conn.cursor()
    cursor.executescript(""" 
        DROP TABLE IF EXISTS convert_ShiftOD;
        CREATE TABLE IF NOT EXISTS convert_ShiftOD(
            TestDate INTEGER NOT NULL,
            ShiftOD INTEGER,
            totalOfInvigilator INTEGER,
            new_ShiftOD INTEGER,
            CONSTRAINT fk_date
            FOREIGN KEY (TestDate, ShiftOD)
            REFERENCES schedule_db(TestDate, ShiftOD)
            ); 
        """)
    convert_ShiftOD = pd.read_sql("SELECT * FROM schedule_db", db_conn)
    convert_ShiftOD = convert_ShiftOD.groupby(['TestDate', 'ShiftOD'])['QuantityOfInvigilator'].sum().reset_index(
        name='totalOfInvigilator')
    df = convert_ShiftOD[['TestDate', 'ShiftOD']]
    TestDate = convert_ShiftOD['TestDate'].drop_duplicates().reset_index()
    TestDate = TestDate['TestDate']

    for n in range(1, 5):
        for i in TestDate:
            df1 = [i, n]
            rr = (df == df1).all(1).any()
            if rr == False:
                df1 = pd.DataFrame([[i, n, 0]],
                                   columns=['TestDate', 'ShiftOD', 'totalOfInvigilator'])
                convert_ShiftOD = pd.concat([df1, convert_ShiftOD], ignore_index=True)

    convert_ShiftOD = convert_ShiftOD.sort_values(['TestDate', 'ShiftOD'], ascending=True, ignore_index=True)
    convert_ShiftOD['new_ShiftOD'] = range(1, len(convert_ShiftOD) + 1)
    convert_ShiftOD.to_sql('convert_ShiftOD', db_conn, if_exists='append', index=False)

    new_ShiftofDay = pd.read_sql("""SELECT schedule_db.CourseID, convert_ShiftOD.new_ShiftOD, schedule_db.QuantityOfInvigilator 
                        FROM schedule_db, convert_ShiftOD 
                        WHERE schedule_db.TestDate=convert_ShiftOD.TestDate AND schedule_db.ShiftOD=convert_ShiftOD.ShiftOD""",
                                 db_conn)

    number_of_supervisors_shift = []  # mảng lưu số lượng người coi thi của mỗi ca
    for i in range(0, len(convert_ShiftOD)):
        number_of_supervisors_shift.append(convert_ShiftOD.iat[i, 2])

    cases_without_supervision = []  # mảng lưu những ca thi không cần người coi
    for i in range(0, len(convert_ShiftOD)):
        if convert_ShiftOD.iat[i, 2] == 0:
            cases_without_supervision.append(convert_ShiftOD.iat[i, 3])

    # Variables
    a = pd.read_sql("SELECT ID FROM invigilator_db", db_conn)

    x = a['ID'].value_counts().count()

    b = convert_ShiftOD['new_ShiftOD'].value_counts().count()  # tổng số ca thi

    c = convert_ShiftOD['totalOfInvigilator'].sum(axis=0)  # tong so ca thi can coi

    d = c // x  # so ca thi trung binh mot Can Bo Coi Thi can coi

    f = c % x  # so CBCT coi nhieu hon trung binh(d)

    n = x * b  # size of individual (chromosome)

    m = 100  # số lượng cá thể trong quần thể

    def tao_cathe(arr):  # tạo một cá thể
        k = 0
        for i in range(0, x):
            sum = 0
            for j in range(0, b):
                if k < f:  # f=c%a
                    if sum < d + 1:
                        arr[0][i][j] = 1
                        sum = sum + arr[0][i][j]
                else:
                    if sum < d:
                        arr[0][i][j] = 1
                        sum = sum + arr[0][i][j]
            random.shuffle(arr[0][i])
            k = k + 1
        return arr

    def chinh_cathe():  # sắp xếp lại thành cá thể hoàn chỉnh
        arr = np.zeros((1, x, b), dtype=int)
        tao_cathe(arr)

        drr = arr[0].sum(axis=0)
        brr = []
        for i in range(len(number_of_supervisors_shift)):
            brr.append(drr[i] - number_of_supervisors_shift[i])
        for i in range(0, len(brr)):
            while brr[i] < 0:
                temp = 0
                for m in range(0, b):
                    if brr[m] > 0:
                        for j in range(0, x):
                            if arr[0][j][i] == 0 and arr[0][j][m] == 1:
                                arr[0][j][i], arr[0][j][m] = arr[0][j][m], arr[0][j][i]
                                brr[m] = brr[m] - 1
                                brr[i] = brr[i] + 1
                                temp = 1
                                break
                if temp == 0:
                    for j in range(x - 1, 0, -1):
                        if arr[0][j][i] == 0:
                            arr[0][j][i] = 1
                            brr[i] = brr[i] + 1
                            break
                    for m in range(0, b):
                        if brr[m] > 0:
                            for j in range(0, x):
                                if arr[0][j][m] == 1:
                                    arr[0][j][m] = 0
                                    brr[m] = brr[m] - 1
                                    break

        return arr

    def create_population():
        population = np.zeros((0, x, b), dtype=int)  # khởi tạo quần thể ban đầu
        for i in range(0, m):
            arr = chinh_cathe()
            population = np.concatenate((population, arr))
        return population

    def weight_compute(bin_matrix, pen_val=10):
        """
        Compute weight overall weight on input binary matrix
        arguments:
        - bin_matrix (numpy array): binary matrix with shape num_of_staff x num_of_exam
        - pen_value: the penalty value for each day longer than expected
        return:
        overall weight: type int
        """
        # compute the number of "1" value on each row
        num_of_ones = np.sum(bin_matrix, axis=1)
        # compute number of day expected from exam assignment
        actual_days = list(map(lambda x: math.ceil(x), num_of_ones / 4))
        # Find the position of 1 value on each row
        one_pos = np.where(bin_matrix == 1)[1]
        # print(one_pos)
        # Compute temporary indices for reshaping one_pos
        adj_indices = [0]
        sum_temp = 0
        for i in range(0, len(num_of_ones)):
            sum_temp = sum_temp + num_of_ones[i]
            adj_indices.append(sum_temp)
        for i in range(1, len(adj_indices)):
            if adj_indices[i] == adj_indices[i - 1]:
                return 20000
        # print(adj_indices)
        # Reshaping one_pos to array with len=num_of_staff and each element is
        # an array store index of 1  value
        shaped_one_pos = [one_pos[adj_indices[i]:adj_indices[i + 1]] for i in range(0, len(adj_indices) - 1)]
        # print(shaped_one_pos)
        # Find min and max position of 1 value on each staff
        min_pos = list(map(min, shaped_one_pos))
        # print(min_pos)
        max_pos = list(map(max, shaped_one_pos))
        # Compute number of maximum 1 value could have between min_pos and max_pos for each staff
        exp_ones = [max - min + 1 for min, max in zip(min_pos, max_pos)]
        # Compute number of 0 value between min_pos and max_pos
        num_of_zero = [m_one - n_one for m_one, n_one in zip(exp_ones, num_of_ones)]
        # Compute number of days current spaned on each staff
        day_spans = [math.ceil((max + 1) / 4) - min // 4 for min, max in zip(min_pos, max_pos)]
        # Compute number of days for penalizing
        day_pens = [c_day - a_day for c_day, a_day in zip(day_spans, actual_days)]
        # compute overall weight
        weight = sum(num_of_zero) + sum(day_pens) * pen_val
        return weight

    def kiem_tra(individual1):  # hàm kiểm tra các ca thi có khớp nhau hay không
        temp = (np.array(individual1) == np.array(number_of_supervisors_shift))
        for i in temp:
            if i == False:
                return False
                break

    # tinh fitness
    def compute_fitness(individual):
        fitness = 0
        tong_coithi = individual.sum()  # tổng số buổi coi thi trong kì thi
        individual_copy = individual.copy()
        for i in cases_without_supervision:
            individual_copy[:, i - 1] = 1
        fitness = weight_compute(individual_copy)
        if tong_coithi != c:  # nếu ràng buộc cứng bị vi phạm thì phạt nặng
            fitness = fitness + 10000
        if kiem_tra(individual.sum(axis=0)) == False:
            fitness = fitness + 10000
        return fitness

    # chon loc
    def selection(sorted_population):
        index1 = random.randint(0, m - 1)
        while True:
            index2 = random.randint(0, m - 1)
            if index2 != index1:
                break
        individual = sorted_population[index1]
        if index2 > index1:
            individual = sorted_population[index2]
        return individual

    # lai ghep:
    def crossover(individual1, individual2, crossover_rate=0.5):
        individual1_new = np.zeros((1, x, b), dtype=int)
        individual2_new = np.zeros((1, x, b), dtype=int)
        individual1_new[0] = individual1.copy()
        individual2_new[0] = individual2.copy()
        for i in range(0, x):
            for j in range(0, b):
                if random.random() < crossover_rate:
                    individual1_new[0][i][j] = individual2[i][j]
                    individual2_new[0][i][j] = individual1[i][j]
        return individual1_new, individual2_new

    # dot bien
    def mutate(individual, mutation_rate=0.05):
        individual_m = np.zeros((1, x, b), dtype=int)
        individual_m = individual.copy()
        for i in range(0, x):
            for j in range(0, b):
                if random.random() < mutation_rate:
                    individual_m[0][i][j] = random.randint(0, 1)
        return individual_m

    # tao quan the moi
    fitnesses = []

    def create_new_population(sorted_old_population):
        # luu vao losses
        fitnesses.append(compute_fitness(sorted_old_population[-1]))

        # in cac gia tri tot nhat qua tung doi
        print(fitnesses[-1])
        # print(sorted_old_population[-1])
        new_population = np.zeros((0, x, b), dtype=int)
        while len(new_population) < m - 30:
            # chon loc
            individual1 = selection(sorted_old_population)
            individual2 = selection(sorted_old_population)
            # lai ghep
            individual_c1, individual_c2 = crossover(individual1, individual2)
            # dot bien
            individual_m1 = mutate(individual_c1)
            individual_m2 = mutate(individual_c2)
            # cho vao quan the moi

            if compute_fitness(individual_m1[0]) > 10000:  # nếu không thỏa mãn ràng buộc cứng thay bằng cá thể mới
                individual_m1 = chinh_cathe()

            if compute_fitness(individual_m2[0]) > 10000:
                individual_m2 = chinh_cathe()
            new_population = np.concatenate((new_population, individual_m1))
            new_population = np.concatenate((new_population, individual_m2))
        # cho 30 con dep nhat cua quan the cu vao quan the moi
        for i in range(1, 31):
            new_individual = np.zeros((1, x, b), dtype=int)
            new_individual[0] = sorted_old_population[-i].copy()
            new_population = np.concatenate((new_population, new_individual))
        return new_population

    # hàm GAs
    def GAs():
        db_conn1 = sqlite3.connect('database.db')
        cursor1 = db_conn1.cursor()
        t0 = time.time()
        # tao quan the ban dau
        population = create_population()
        n_generations = 1
        for _ in range(n_generations):
            sorted_old_population = sorted(population, reverse=True, key=compute_fitness)
            population = create_new_population(sorted_old_population)
        t1 = time.time()
        total_time = t1 - t0
        obj = sorted_old_population[-1]
        queue.put(obj)
        # hien thi tuyen duong ngan nhat
        print('Shortest path \n', sorted_old_population[-1], '\nCosts: ', fitnesses[-1], '\n', 'Time(s): ',
              total_time)

        new_shiftof_day1 = new_ShiftofDay.copy()

        invigilatorID = []
        CourseID = []
        for i in range(len(sorted_old_population[-1])):
            for j in range(len(sorted_old_population[-1][0])):
                if sorted_old_population[-1][i][j] == 1:
                    invigilatorID.append(i + 1)
                    for p in range(len(new_shiftof_day1)):
                        if (new_shiftof_day1.iat[p, 1] == j + 1) and (new_shiftof_day1.iat[p, 2] > 0):
                            CourseID.append(p + 1) # Lỗi
                            new_shiftof_day1.iat[p, 2] = new_shiftof_day1.iat[p, 2] - 1
                            break
        data = {'ID': invigilatorID,
                'CourseID': CourseID}
        assign_df = pd.DataFrame(data)
        cursor1.executescript("""
                        drop table if exists assign_db;
                        create table if not exists assign_db(
                        ID Integer,
                        CourseID Integer,
                        FOREIGN KEY(ID) REFERENCES invigilator_db(ID),
                        FOREIGN KEY(CourseID) REFERENCES schedule_db(CourseID)
                        );""")
        assign_df.to_sql('assign_db', db_conn1, if_exists='append', index=False)
        scheduler_df = pd.read_sql("""SELECT assign_db.CourseID,  schedule_db.CourseName, schedule_db.Room, schedule_db.ShiftOD, schedule_db.TestDate, schedule_db.QuantityOfInvigilator, GROUP_CONCAT(invigilator_db.Full_Name) Invigilator
    FROM assign_db, invigilator_db, schedule_db
    WHERE assign_db.ID=invigilator_db.ID and schedule_db.CourseID = assign_db.CourseID
    GROUP BY assign_db.CourseID
    ORDER BY assign_db.CourseID;""", db_conn1)
        scheduler_df.to_excel("output.xlsx", index=False)

        db_conn1.commit()
        db_conn1.close()

    # Dataframe chứa output

    thread1=threading.Thread(target=GAs)

    def run_thread():
        work=progress(thread1, queue)
    # Function to check state of thread1 and to update progressbar #
    def progress(thread, queue):
        # starts thread #
        thread.start()

        # defines indeterminate progress bar (used while thread is alive) #
        _bar = ttk.Progressbar(analyze_window, orient=HORIZONTAL, mode='indeterminate', maximum=100, length=330)

        # defines determinate progress bar (used when thread is dead) #

        # places and starts progress bar #
        _bar.place(x=40,y=380)
        _bar.start()

        # checks whether thread is alive #
        while thread.is_alive():
            analyze_window.update()
            pass

        # once thread is no longer active, remove pb1 and place the '100%' progress bar #
        _bar.destroy()
        kq_df = pd.read_excel("output.xlsx")
        run_btn.config(state='disabled')
        tv4 = ttk.Treeview(lbl_treeview)
        tv4.delete(*tv4.get_children())

        tv4['column'] = list(kq_df.columns)
        tv4['show'] = 'headings'
        for column in tv4['column']:
            tv4.heading(column, text=column)
        tv4.column('#1', width=70, stretch=0, anchor='n')
        tv4.column('#2', width=250, stretch=0, anchor='w')
        tv4.column('#3', width=70, stretch=0, anchor='n')
        tv4.column('#4', width=70, stretch=0, anchor='n')
        tv4.column('#5', stretch=0, anchor='n')
        tv4.column('#6', width=200, stretch=0, anchor='n')
        tv4.column('#7', width=400, stretch=0, anchor='w')
        teacher_rows_df = kq_df.to_numpy().tolist()
        for row in teacher_rows_df:
            tv4.insert("", "end", value=row)

        tv4.pack(fill=BOTH, pady=10, padx=10)

        # retrieves obj from queue #
        work = queue.get()
        return work


    img_load = Image.open('images\\Kye-Meh.jpg')
    render = ImageTk.PhotoImage(img_load)
    img_name = PhotoImage(file='images\\name_Genetic_Algorithm.png')
    img_run = PhotoImage(file='images\\generate_ga.png')
    # UI #

    # FRAMES
    """fr_bg_analyze = Frame(analyze_window, width=1366, height=768)
    fr_bg_analyze.place(x=0, y=0)  # khung background
    fr_analyze = Frame(analyze_window, bg='white', width=1326, height=728)
    fr_analyze.pack(padx=20, pady=20)  # khung trắng"""

    # LABELS
    #lbl_bg_analyze = Label(analyze_window, image=render)
    #lbl_bg_analyze.place(x=0, y=0)  # chứa background
    lbl_name_analyze = Label(analyze_window, bg='#dad299', image=img_name)
    lbl_name_analyze.place(x=20, y=20)
    # GAs Information
    l0 = Label(analyze_window, bg='#dad299', text=f"Number Of Individual: ", font=20)
    l0.place(x=40, y=140)
    l1 = Label(analyze_window, bg='#dad299', text=str(m), font=20, width=10, borderwidth=2, relief="groove")
    l1.place(x=250, y=140)
    l2 = Label(analyze_window, bg='#dad299', text="No. Of Generation: ", font=20)
    l2.place(x=40, y=170)
    l3 = Label(analyze_window, bg='#dad299', text='100', font=20, width=10, borderwidth=2, relief="groove")
    l3.place(x=250, y=170)
    l4 = Label(analyze_window, bg='#dad299', text="Crossover Rate: ", font=20)
    l4.place(x=40, y=200)
    l5 = Label(analyze_window, bg='#dad299', text="0.5",font=20, width=10, borderwidth=2, relief="groove")
    l5.place(x=250, y=200)
    l6 = Label(analyze_window, bg='#dad299', text="Mutation Rate: ", font=20)
    l6.place(x=40, y=230)
    l7 = Label(analyze_window, bg='#dad299', text="0.05", font=20, width=10, borderwidth=2, relief="groove")
    l7.place(x=250, y=230)

    run_btn = Button(analyze_window, image=img_run, command=run_thread, bg='#dad299', bd=0, activebackground='#dad299')
    run_btn.place(x=170, y=290)

    lbl_treeview = Label(analyze_window, bg='#dad299', width=160, height=15, borderwidth=2, relief='solid')  # , width=160, height=15, borderwidth=2, relief='solid'
    lbl_treeview.place(x=40, y=450)

    analyze_window.mainloop()


def home_page():
    try:
        conn_ = sqlite3.connect("database.db")
        check_case = pd.read_sql("Select * from invigilator_db where ID = 1", conn_)
        root_.destroy()
        global home_
        home_ = Tk()
        home_.geometry("1366x768")
        home_.resizable(0, 0)
        home_.title("HOME PAGE")
        load = Image.open("images\\Autumn.jpg")
        render = ImageTk.PhotoImage(load)
        img_name_home = PhotoImage(file="images\\name_blue_black.png")
        img_view = PhotoImage(file="images\\view_data.png")
        img_run = PhotoImage(file="images\\run_algorithm.png")
        # Frames
        fr_home = Frame(home_, width=1368, height=768, bg="#B5D9B5")
        fr_home.place(x=0, y=0)
        # Labels
        # lbl_bg_home = Label(fr_home, bg="#B5D9B5")  # background
        # lbl_bg_home.place(x=0, y=0)
        lbl_title_home = Label(fr_home, image=img_name_home, bg='#B5D9B5')
        lbl_title_home.place(x=360, y=100)

        btn_view = Button(fr_home, command=review_page, image=img_view, bd=0, bg='white', activebackground='white')
        btn_view.place(x=200, y=400)

        btn_run = Button(fr_home, command=analysis_page, image=img_run, bd=0, bg='white', activebackground='white')
        btn_run.place(x=750, y=400)

        home_.mainloop()
    except pd.io.sql.DatabaseError:
        messagebox.showerror("Error!", f"There are no data to execute.\nPlease make sure you already import data!")
        return btn_GAs.config(state='disabled')


root_ = Tk()
root_.geometry("720x800")  # width x height
root_.resizable(0, 0)
root_.title('Exam invigilator scheduler')
# IMG
img_title = PhotoImage(file='images\\name.png')
img_imp_teacher = PhotoImage(file='images\\imp_teacher.png')
img_imp_course = PhotoImage(file='images\\imp_course.png')
img_started = PhotoImage(file='images\\started.png')
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
                 activebackground='#dad299')  # gọi home window (GET STARTED!)
btn_GAs.place(x=202, y=600)
root_.mainloop()
