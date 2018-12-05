
# Aspire Assembly Registration App 
# Will Grey
# 23/11/2018

import base64 
import sqlite3
from tkinter import *
import datetime
import hashlib
import csv 

class Db():

    def __init__(self):
        
        self.openDb()

        self.db.execute("""CREATE TABLE IF NOT EXISTS students
                   (studentID INTEGER PRIMARY KEY,
                    surname TEXT,
                    firstname TEXT,
                    groupID TEXT,
                    year INTEGER,
                    rfid TEXT,
                    last_registration INTEGER)""")   

        self.closeDb()

    def openDb(self):
	
        try:
            self.conn = sqlite3.connect('assembly-app.db')
            self.db = self.conn.cursor()
		
        except:
            print("Cannot open or create database file")
			
    def closeDb(self):
        self.conn.commit()
        self.conn.close()        


class Help():

    def help(self):
        comment=("Take Register:\t\tRun this while register is open. \n\n"
                         "Create Register: \t\tThis will create an attendance_date.csv file\n"
                         "\t\t\twhere date is the current date.\n"
                         "\t\t\tFormat: surname, firstname, group, year, '/ or N'\n\n"
                         "Export Students: \t\tThis will export a list of students\n"
                         "\t\t\tinto a file called students.csv\n\n"
                         "Import Students: \t\tThis will import a list of students\n"
                         "\t\t\tinto a file called students.csv\n"
                         "\t\t\tThe file is in the form: \n \t\t\tsurname, firstname, group, year, rfid\n"
	           "\t\t\tIf RFID is unavailable enter NULL\n\n"
                         "Add Student:  \t\tAdd students to database.\n\n"
                         "Remove Student:  \tRemove students from database.\n"
                          "\t\t\tTo update a student record first remove the \n"
                          "\t\t\tstudent then add the student again with the\n"
                          "\t\t\tupdated details.\n\n"
                         "Update Student RFID:  \tUpdate student RFID in database.\n\n"
                          "End of Year Update: \tRemoves all Year 13 from database\n"
                         "\t\t\tand updates Year 12 students to Year 13.\n"
                         "\t\t\tWARNING: THIS MAKES SUBSTANTIAL CHANGES\n"
                         "\t\t\tTO THE DATABASE THAT CANNOT BE RECOVERED\n\n"
                         "Help: \t\t\tDisplay this help menu\n\n"
                         "Exit: \t \t\tQuit application")

        self.help_window = Toplevel()
        self.help_window.wm_title("Help")
        self.help_window.geometry("450x580")
        self.help_window.resizable(False, False)
        self.help_window.configure(background="white")
        Label( self.help_window,text="Help", font=("Helvetica",18), background="white").pack()
        Label( self.help_window, text=comment, bg="white",justify=LEFT).pack(side="top", fill="both", expand=True, padx=10, pady=10)
        Button( self.help_window,text="Close",background="white",command=self.help_window.destroy).pack()

class UpdateStudents(Db):

    def  list_students(self):

        self.openDb()
        
        self.db.execute("SELECT surname, firstname, groupID FROM students ORDER BY surname")
        all_rows = self.db.fetchall()
        self.students=[]
       
        for row in all_rows:
            self.students.append(row[0] + " " + row[1] + " " + row[2])

        self.closeDb()

        self.update_students_win()

    def update_students_win(self):

        add_win = Toplevel()
        add_win.wm_title("Update Students")
        add_win.geometry("250x180")
        add_win.resizable(False, False)
        add_win.configure(background="white")

        self.rfid= Entry(add_win,show="*")

        self.st = StringVar(add_win)
        self.st.set(self.students[0])

        self.entryVal2=StringVar()
        self.entryVal2.set("")
        
        Label(add_win, text="Update Students", font=("Helvetica",16), bg="white").grid(row=1, column=1,columnspan=2)        
        Label(add_win, text="Student", font=("Helvetica",12), bg="white").grid(row=2,column=1)
        o=OptionMenu(add_win, self.st, *self.students)
        o.configure(background="white")
        o.grid(row=2,column=2)

        Label(add_win, text="RFID", font=("Helvetica",12), bg="white").grid(row=3,column=1)
        self.rfid.grid(row=3,column=2)
        Label(add_win, textvariable=self.entryVal2, bg="white").grid(row=4,column=1,columnspan=2)
        Button(add_win,text="Update Student RFID",background="white",command=self.update_students_sql).grid(row=5,column=1,columnspan=2)
        Button(add_win,text="Close",background="white",command=add_win.destroy).grid(row=6,column=1,columnspan=2)
        
    def update_students_sql(self):
        hashed_rfid=hashlib.md5(str(self.rfid.get()).encode('utf-8')).hexdigest()
        print(self.st.get(),hashed_rfid)
       
        a=self.st.get().split()
        self.entryVal2.set("Updated RFID of "+ self.st.get())

        self.openDb()
        self.db.execute("UPDATE students SET rfid=? WHERE surname=? AND firstname=? AND groupID=?",(hashed_rfid,a[0],a[1],a[2]))
        self.closeDb()
        
        self.rfid.delete(0, END)
        self.rfid.insert(0, "")

class ImportStudents(Db):
    
    def import_students(self):
        
        self.w = Toplevel()
        self.w.wm_title("Import Students")
        self.w.geometry("150x100")
        self.w.configure(background="white")
        self.w.resizable(False, False)
        Label(self.w, text="Import Students", font=("Helvetica",16), bg="white").pack()
        Button(self.w,text="Select CSV file",background="white",command=self.import_csv_file).pack()
        Button(self.w,text="Exit",background="white",command=self.w.destroy).pack()

    def import_csv_file(self):

        self.csv_file=filedialog.askopenfilename()
        self.read_csv_file()
        self.add_records_to_db()

    def read_csv_file(self):
        self.l=[]
        file=open(self.csv_file)
        r=csv.reader(file)
        self.num=0
        for i in r:
            self.l.append(i)
            self.num=self.num+1
        file.close()
       # print( self.l)

    def add_records_to_db(self):
        print("Start Import")
        self.openDb()
		
        try:
            self.db.execute("""SELECT * FROM students""")
            all_rows = self.db.fetchall()
            #print(self.l[10][0],self.l[10][1],self.l[10][2])
            for i in range(self.num):
            
                flag=0
                for row in all_rows:
                    if self.l[i][0].lower() == row[1].lower() and self.l[i][1].lower() == row[2].lower()  and self.l[i][2].lower()== row[3].lower():
                        flag=1
                        break
            
                if flag==0:
                
                    if self.l[i][4]!="NULL":    
                        self.l[i][4]=hashlib.md5(str(self.rfid.get()).encode('utf-8')).hexdigest()
                
                    self.db.execute("INSERT INTO students VALUES(NULL,?,?,?,?,?,NULL)",(self.l[i]))
                
                else:
                    print(self.l[i][0],self.l[i][1], "already in database")
        except:
        
            self.closeDb()
            print("Problem importing the file. This is most likely because it is not in the correct format:\n\
            surname, firstname, group, year, rfid_number. \n\
            If RFID number is unavailable use NULL")
        
        else:
            self.closeDb()
            print("End Import")
        
        
class UpdateEndOfYear(Db):
    
    def update_students(self):
        
        u=(     "Removes all Year 13 from database\n"
                   "and updates Year 12 students to Year 13\n"
                   "WARNING: THIS MAKES SUBSTANTIAL CHANGES\n"
                   "TO THE DATABASE THAT CANNOT BE RECOVERED")
        
        self.w = Toplevel()
        self.w.wm_title("Update students")
        self.w.geometry("500x150")
        self.w.configure(background="white")
        self.w.resizable(False, False)
        Label(self.w, text=u, font=("Helvetica",12), bg="white").pack()
        Button(self.w,text="Update",background="white",command=self.update_db).pack()
        Button(self.w,text="Exit",background="white",command=self.w.destroy).pack()
        
    def update_db(self):

        self.openDb()
        self.db.execute("DELETE FROM students WHERE year=13")
        self.db.execute("UPDATE students SET year=13 WHERE year=12")

        self.db.execute("""SELECT * FROM students""")
        all_rows = self.db.fetchall()

        for row in all_rows:
            old_group=row[3]
            new_group=old_group.replace("L","U")
            self.db.execute("UPDATE students SET groupID=? WHERE studentID=?",(new_group,row[0]))
        
        self.closeDb()
        self.w.destroy()


class ExportStudents(Db):

    def get_students(self):
        
        f=open("students.csv","w")
        self.openDb()
        self.db.execute("""SELECT * FROM students ORDER BY surname""")
        all_rows = self.db.fetchall()

        for row in all_rows:
            f.write(str(row[1])+str(",")+str(row[2])+str(",")+str(row[3])+str(",")+str(row[4])+str("\n"))
           
        f.close()
        self.closeDb()
        self.get_students_window()

    def get_students_window(self):
        
        s = Toplevel()
        s.wm_title("Export Students")
        s.geometry("350x100")
        s.resizable(False, False)
        s.configure(background="white")
        Label(s,text="Export Students", font=("Helvetica",18), background="white").pack()
        Label(s, text="List of students successfully exported into students.csv file.", bg="white", justify=LEFT).pack(side="top", fill="both", expand=True, padx=10, pady=10)
        Button(s,text="Exit",background="white",command=s.destroy).pack()


class RemoveStudent(Db):

    def  remove_student(self):

        self.openDb()
        
        self.db.execute("SELECT surname, firstname, groupID FROM students ORDER BY surname")
        all_rows = self.db.fetchall()
        self.students=[]
       
        for row in all_rows:
            self.students.append(row[0] + " " + row[1] + " " + row[2])

        self.closeDb()

        self.remove_students_win()

    def remove_students_win(self):

        self.add_win = Toplevel()
        self.add_win.wm_title("Update Students")
        self.add_win.geometry("180x130")
        self.add_win.resizable(False, False)
        self.add_win.configure(background="white")

        self.st = StringVar(self.add_win)
        self.st.set(self.students[0])

        self.entryVal=StringVar()
        self.entryVal.set("")
        
        Label(self.add_win, text="Remove Students", font=("Helvetica",16), bg="white").grid(row=1)        
        o=OptionMenu(self.add_win, self.st, *self.students)
        o.configure(background="white")
        o.grid(row=2)

        Button(self.add_win,text="Remove Student",background="white",command=self.remove_students_sql).grid(row=3)
        Button(self.add_win,text="Close",background="white",command=self.add_win.destroy).grid(row=4)
        
    def remove_students_sql(self):
        
        print("Removed Student: "+ self.st.get())
        a=self.st.get().split()
        self.entryVal.set("Removed Student: "+ self.st.get())

        self.openDb()
        self.db.execute("DELETE from students WHERE surname=? AND firstname=? AND groupID=?",(a[0],a[1],a[2]))
        self.closeDb()
        self.add_win.destroy()


class AddStudent(Db):

    def  add_student(self):

        add_win = Toplevel()
        add_win.wm_title("Add Student")
        add_win.geometry("200x370")
        add_win.resizable(False, False)
        add_win.configure(background="white")
        self.years=["12","13"]
        
        self.firstname = Entry(add_win)
        self.surname = Entry(add_win)
        self.group = Entry(add_win)
        self.rfid = Entry(add_win,show="*")

        self.entryVal = StringVar(add_win)
        
        self.year = StringVar(add_win)

        Label(add_win, text="Add Student", font=("Helvetica",16), bg="white").pack()

        Label(add_win, text="Firstname", font=("Helvetica",12), bg="white").pack()
        self.firstname.pack() 

        Label(add_win, text="Surname", font=("Helvetica",12), bg="white").pack()
        self.surname.pack()
        
        Label(add_win, text="Year", font=("Helvetica",12), bg="white").pack()
        o=OptionMenu(add_win, self.year, *self.years)
        o.configure(background="white")
        o.pack()
        
        Label(add_win, text="Group", font=("Helvetica",12), bg="white").pack()
        self.group.pack()

        Label(add_win, text="RFID", font=("Helvetica",12), bg="white").pack()
        self.rfid.pack()

        Label(add_win, textvariable=self.entryVal, bg="white").pack()

        Button(add_win,text="Add Student",background="white",command=self.add_students_sql).pack()
        Button(add_win,text="Close",background="white",command=add_win.destroy).pack()


    def reset_student_values(self):
        
        self.rfid.delete(0, END)
        self.rfid.insert(0, "")

        self.firstname.delete(0, END)
        self.firstname.insert(0, "")

        self.surname.delete(0, END)
        self.surname.insert(0, "")

        self.group.delete(0, END)
        self.group.insert(0, "")
        
        
    def add_students_sql(self):
        
        if self.surname.get() !="" and self.firstname.get() !="":
            hashed_rfid=hashlib.md5(str(self.rfid.get()).encode('utf-8')).hexdigest()
            print("Added student:",self.surname.get(),self.firstname.get(),self.group.get(),int(self.year.get()),hashed_rfid)
            self.entryVal.set("Added: "+ self.firstname.get() + " " + self.surname.get())
       
            self.openDb()
            self.db.execute("SELECT * FROM students")
            all_rows = self.db.fetchall()

            flag=0
            for row in all_rows:
                if self.surname.get().lower() == row[1].lower() and self.firstname.get().lower() == row[2].lower()  and self.group.get().lower() == row[3].lower():
                    flag=1
                    break
            
            if flag==0:
                self.db.execute("INSERT INTO students VALUES(NULL,?,?,?,?,?,NULL)"\
                           ,(self.surname.get(),self.firstname.get(),self.group.get(),int(self.year.get()),hashed_rfid))
                self.entryVal.set("Added: "+ self.firstname.get() + " " + self.surname.get())            
            else:
                self.entryVal.set(self.surname.get(),self.firstname.get(), "already in database")
        
            self.closeDb()
            
        self.reset_student_values()

class Rfid(Db):

    def __init__(self):
        self.tag=""
        self.todays_date=datetime.datetime.today().strftime("%Y%m%d")

    def rfid_win(self):

        self.win = Toplevel()
        self.win.wm_title("Take Register")
        self.win.geometry("200x200")
        self.win.resizable(False, False)
        self.win.configure(background="white")

        Label(self.win,text="Click here\n to take register", font=("Helvetica",16), background="white").pack()
        self.frame = Frame(self.win, width=200, height=100, background="white")
        self.frame.bind("<Key>", self.key)
        self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()
        
        Button(self.win,text="Close",background="white",command=self.win.destroy).pack()

    def key(self,event):
        press = repr(event.char)
        if ord(event.char) != 13:
            self.tag +=press.strip("'")
        else:
           if len(self.tag) > 0:
                    self.hashed_rfid=hashlib.md5(str(self.tag).encode('utf-8')).hexdigest()
                    self.rfid_sql()
                    #print(self.hashed_rfid)
                    self.tag = ""         

    def callback(self,event):
        self.frame.focus_set()

    def rfid_sql(self):
        self.openDb()
        self.db.execute("UPDATE students SET last_registration=? WHERE rfid=?",(int(self.todays_date),self.hashed_rfid,))
        self.db.execute("SELECT surname, firstname, groupID FROM students WHERE rfid=?",(self.hashed_rfid,))
        record = self.db.fetchone()
        self.closeDb()
        print(record[0]+","+record[1]+","+record[2])

class GenerateRegister(Db):
	
    def generate_register(self):

        self.win = Toplevel()
        self.win.wm_title("Generate Register")
        self.win.geometry("200x200")
        self.win.resizable(False, False)
        self.win.configure(background="white")

        Label(self.win,text="Generate register", font=("Helvetica",16), background="white").pack()
        
        self.years=["Year 12","Year 13"]
        self.year = StringVar(self.win)

        Label(self.win, text="Year", font=("Helvetica",12), bg="white").pack()
        o=OptionMenu(self.win, self.year, *self.years)
        o.configure(background="white")
        o.pack()
		
        Button(self.win,text="Generate Register",background="white",command=self.generate_register_sql).pack()
	
	
    def generate_register_sql(self):
        print("Generate Register")
        self.openDb()
		
        self.db.execute("""SELECT MAX(last_registration) FROM students""")
        last_registration_date = self.db.fetchall()
        print(last_registration_date[0][0])
        register="register_"+str(last_registration_date[0][0])+".csv"
        f=open(register,"w")

        if self.year.get()=="Year 12":
            self.db.execute("SELECT * FROM students WHERE year=12 ORDER BY surname")
        elif self.year.get()=="Year 13":
            self.db.execute("SELECT * FROM students WHERE year=13 ORDER BY surname")
            
        all_records = self.db.fetchall()
    
        for record in all_records:
            if record[6]==last_registration_date[0][0]:
                f.write(record[1]+str(",")+record[2]+str(",")+record[3]+str(",/\n"))
            else:
                f.write(record[1]+str(",")+record[2]+str(",")+record[3]+str(",N\n"))   
        f.close()
        
        self.closeDb()
        self.win.destroy()


		
class Gui(Db):

    def __init__(self):

        self.d=ExportStudents()
        self.h=Help()
        self.u=UpdateEndOfYear()
        self.adds=AddStudent()
        self.impStudents=ImportStudents()
        self.us=UpdateStudents()
        self.rs=RemoveStudent()
        self.rfid=Rfid()
        self.gr=GenerateRegister()
        
        self.window = Tk()
        self.window.title("Assembly Registration App")
        self.window.configure(background="white")
        self.window.resizable(False, False)

      #  self.image = PhotoImage(data=self.encode64())
     #   self.image = self.image.subsample(3, 3)
        self.label1 = Label(self.window,text="Aspire Assembly \nRegistration App", font=("Helvetica",18), background="white").grid(row=1)
      #  self.label2 = Label(self.window, image=self.image).grid(row=2,padx=20,pady=5)

        Button(self.window, text='Take Register',background="white",command=self.rfid.rfid_win,font=("Helvetica",10),width=15,pady=5).grid(row=3)
        Button(self.window, text='Export Register',background="white",command=self.gr.generate_register,font=("Helvetica",10),width=15,pady=5).grid(row=4)
        Button(self.window, text='Import Students',background="white",command=self.impStudents.import_students,font=("Helvetica",10),width=15,pady=5).grid(row=5)
        Button(self.window, text='Export Students',background="white",command=self.d.get_students,font=("Helvetica",10),width=15,pady=5).grid(row=6)
        Button(self.window, text='Add Student',background="white",command=self.adds.add_student,font=("Helvetica",10),width=15,pady=5).grid(row=7)
        Button(self.window, text='Remove Student',background="white",command=self.rs.remove_student,font=("Helvetica",10),width=15,pady=5).grid(row=8)
        Button(self.window, text='Update Student RFID',background="white", command=self.us.list_students, font=("Helvetica",10),width=15,pady=5).grid(row=9)
        Button(self.window, text='End of Year Update',background="white",command=self.u.update_students, font=("Helvetica",10),width=15,pady=5).grid(row=10)
        Button(self.window, text='Help',background="white",command=self.h.help,font=("Helvetica",10),width=15,pady=5).grid(row=11)
        Button(self.window, text='Exit',background="white",command=self.window.destroy,font=("Helvetica",10),width=15,pady=5).grid(row=12)
 
        self.window.mainloop()

 #   def encode64(self):
 #       self.image = open('csf-logo.png', 'rb').read()
 #       self.image_64_encode = base64.b64encode(self.image)
 #       return self.image_64_encode

class App():
    def __init__(self):
        Db()
        Gui()

if __name__ == '__main__':
    App()
