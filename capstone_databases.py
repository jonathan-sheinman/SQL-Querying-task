# *** Functions *** 


# function to correct user input if not in the right format 

def usage_is_incorrect(input, num_args):
    if len(input) != num_args + 1:
        print(f"The {input[0]} command requires {num_args} arguments.")
        return True
    return False

# function to store the query data, up to here in dictionary format, as a .json file if requested

def store_data_as_json(dictionary, filename):
    import json
    dictionary = json.dumps(dictionary)
    with open(filename, 'w', encoding='utf-8') as outfile:
        outfile = json.dump(dictionary, outfile, sort_keys=True, indent=4)
    print('Saved as .json file') 

# nested function which converts values of a dictionary into xml elements when they are themselves in dictionary format 

def create_tree(root2, dictionary2):

    import xml.etree.ElementTree as ET
    for k, v in dictionary2.items():
        child = ET.SubElement(root2, k)
        if isinstance(v, dict):
            create_tree(child, v)
        else:
            child.text = v

# function to store the query data, up to here in dictionary format, as an xml, using the nested create_tree functino

def store_data_as_xml(dictionary, filename):

    import xml.etree.ElementTree as ET
    root = ET.Element(rootname)
    create_tree(root, dictionary)
    tree = ET.ElementTree(root)
    tree.write(filename)
    print('Saved as .xml file')

# function giving the user choice whether to store the data and, if so, whether in JSON or XML format using, using the functions defined above

def offer_to_store(data):
    while True:
        print("Would you like to store this result?")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(data, filename)
                break
            elif ext == 'json':
                store_data_as_json(data, filename)
                break
            else:
                print("Invalid file extension. Please use .xml or .json")
                break

        elif choice == 'n':
            break

        else:
            print("Invalid choice")
            break




# *** THE PROGRAMME *** 

# Import sqlite and connect to the HyperionDev.db database, using a try/except clause to catch exceptions

import sqlite3

try:
    db = sqlite3.connect("HyperionDev.db")

except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

# create a cursor variable to make queries on the database

cursor = db.cursor()

# provide a menu offering the user: a demo which displays all the names, a student's course, address, reviews, a teacher's courses, 
# a list of students who haven't completed their course and a list of students with marks below 30

usage = '''
What would you like to do?

d - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taken by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here: '''

print("Welcome to the data querying app!")

# use a while loop so the user can make another query without leaving the programme, and in case the user has made a mistake caught by the usage_is_incorrect function 
while True:

    # request input from user in response to the usage menu
    user_input = input(usage).split(" ")

    # Parse user input into command and args
    command = user_input[0]
    if len(user_input) > 1:
        args = user_input[1:]

    # demo option - prints all student names and surnames 
    if command == 'd': 
        data = cursor.execute("SELECT * FROM Student")
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")
    
    # vs option - view subjects by student_id
    elif command == 'vs': 

        # check format of input using usage_is_incorrect function (do this for the other as well)
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]

        # execute the query (do this for the other as well)
        data = cursor.execute (
'''SELECT Course.course_name, Student.first_name, Student.last_name
FROM Course
INNER JOIN StudentCourse
ON StudentCourse.course_code = Course.course_code
INNER JOIN Student 
ON StudentCourse.student_id = Student.student_id
WHERE StudentCourse.student_id == ?''', (student_id,))
        
        # store the query data in dictionary format, print a user-friendly display, and offer to store it using the offer_to_store function  (do this for the other as well)
        dictionary = {}
        for a, b, c in data:
            subject_index = 0
            display = f'Student: {b} {c}\nStudent ID: {student_id}\nSubject: {a}\n\n'
            dictionary = {'Student': f'{b} {c}', 'StudentID': student_id, 'Subject': a}
        print(display)
        rootname = 'Student subject'
        offer_to_store(dictionary)
        db.commit()
        pass

    # la option - list address by name and surname
    elif command == 'la':
        if usage_is_incorrect(user_input, 2):
            continue
        firstname, lastname = args[0], args[1]
        data = cursor.execute (
'''SELECT Address.street, Address.city
FROM Address
LEFT JOIN Student
ON Student.address_id = Address.address_id
WHERE Student.first_name == ? AND Student.last_name == ?''', (firstname, lastname))
        dictionary = {}
        for a, b in data:
            display = f'Student: {firstname} {lastname}\nAddress: {a}, {b}\n\n'
            dictionary = {'Student': f'{firstname} {lastname}', 'address': f'{a}, {b}'}
        print(display)
        rootname = 'Student Address'
        offer_to_store(dictionary)
        db.commit()
        pass
    
        # lc option - list courses by teacher
    elif command == 'lc':
        if usage_is_incorrect(user_input, 1):
            continue
        teacher_id = args[0]
        data = cursor.execute(
'''SELECT Course.course_name, Teacher.first_name, Teacher.last_name
FROM Course
INNER JOIN Teacher
ON Course.teacher_id = Teacher.teacher_id AS teacher_id
WHERE teacher_id == ?''', (teacher_id,))
        display = ''
        dictionary = {}
        course_list = []
        course_list_index = 0
        for a,b,c  in data:
            if course_list == []:
                course_list = course_list.append(a)
            else:
                course_list_index += 1
                course_list = course_list.append(a)
                strcourse_list = ', '.join(course_list)
                if (len(course_list) - 1) == course_list_index:
                    display = f'Teacher: {b} {c}\nTeacher ID: {teacher_id}\nCourses: {strcourse_list}\n\n'
                    dictionary = {'Teacher': f'{b} {c}', 'Teacher ID': teacher_id, 'Courses': strcourse_list}
        print(display)
        rootname = 'Teacher Courses'
        offer_to_store(dictionary)
        db.commit()
        pass

    # list reviews by student_id
    elif command == 'lr':
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = cursor.execute (
'''SELECT Review.completeness, Review.efficiency, Review.style, Review.documentation, Review.review_text, Student.first_name, Student.last_name, Course.course_name
FROM student
INNER JOIN Review
ON Student.student_id = Review.student_id 
INNER JOIN Student.student_id = StudentCourse.student_id
WHERE student_id == ?''', (student_id,))
        dictionary = {}
        for a,b,c,d,e,f,g,h in data:
            display = f'''
Student: {f}{g}
Student ID: {student_id}
Course: {h}
Scores
    Completeness: {a}
    Efficiency: {b}
    Style: {c}
    Documentation: {d}
Review: 
    {e}'''
            dictionary = {'Student': f'{f} {g}', 'Student ID': student_id, 'Course': h, 'Scores': {f'Completeness {a}', f'Efficiency {b}', f'Style {c}', f'Documentation {d}'}, 'Review': e}
        print(display)
        rootname = 'Student Reviews'
        offer_to_store(dictionary)
        db.commit()
        pass

        # list all students who haven't completed their course
    elif command == 'lnc':
        data = cursor.execute(
'''SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name 
FROM StudentCourse 
INNER JOIN Student 
ON StudentCourse.student_id = Student.student_id
INNER JOIN Course
ON  StudentCourse.course_code = Course.course_code
WHERE StudentCourse.is_complete = 0'''
)
        dictionary = {}
        display = ''
        for a, b, c, d, e in data:
            display += f'Student: {b}{c}\n Student ID: {a}\n Student\'s Email: {d} \nCourse: {e}\n\n'
            dictionary[f'{b}{c}'] = {'Student ID': a, 'Email': d, 'Course': e}
        display += '\n'
        print(display)
        rootname = 'Students not Completed Course'
        offer_to_store(dictionary)
        db.commit()
        pass

    # list all students who have completed their course and got a mark <= 30
    elif command == 'lf':
        data = cursor.execute(
'''SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name 
FROM StudentCourse 
INNER JOIN Student 
ON StudentCourse.student_id = Student.student_id
INNER JOIN Course
ON  StudentCourse.course_code = Course.course_code
WHERE StudentCourse.mark < 30 and StudentCourse.is_complete == 1''')
        dictionary = {}
        display = ''
        for a, b, c, d, e in data:
            display += f'Student: {b}{c}\n Student ID: {a}\n Student\'s Email: {d} \nCourse: {e}\n\n'
            dictionary[f'{b}{c}'] = {'Student ID': a, 'Email': d, 'Course': e}  
        display += '\n' 
        print(display)
        rootname = 'Students with mark under 30'
        offer_to_store(dictionary)
        db.commit()
        pass
    
        # option to exit the programme 
    elif command == 'e': 
        print("Programme exited successfully!")
        break
    
    else:
        print(f"Incorrect command: '{command}'")
    
    db.close


