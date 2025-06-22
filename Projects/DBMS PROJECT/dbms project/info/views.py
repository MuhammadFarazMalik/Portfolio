from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from .models import Book, Dept, Class, Fee, Fine, LibraryLoan, Student, Attendance, Course, Teacher, Assign, AttendanceTotal, time_slots, \
    DAYS_OF_WEEK, AssignTime, AttendanceClass, StudentCourse, Marks, MarksClass
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages


User = get_user_model()

# Create your views here.


@login_required
def index(request):
    if request.user.is_teacher:
        return render(request, 'info/t_homepage.html')
    if request.user.is_student:
        return render(request, 'info/homepage.html')
    if request.user.is_superuser:
        return render(request, 'info/admin_page.html')
    return render(request, 'info/logout.html')


@login_required()
def attendance(request, stud_id):
    stud = Student.objects.get(USN=stud_id)
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    att_list = []
    for ass in ass_list:
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/attendance.html', {'att_list': att_list})


@login_required()
def attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, USN=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/att_detail.html', {'att_list': att_list, 'cr': cr})


# Teacher Views

@login_required
def t_clas(request, teacher_id, choice):
    teacher1 = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'info/t_clas.html', {'teacher1': teacher1, 'choice': choice})


@login_required()
def t_student(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    att_list = []
    for stud in ass.class_id.student_set.all():
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/t_students.html', {'att_list': att_list})


@login_required()
def t_class_date(request, assign_id):
    now = timezone.now()
    ass = get_object_or_404(Assign, id=assign_id)
    att_list = ass.attendanceclass_set.filter(date__lte=now).order_by('-date')
    return render(request, 'info/t_class_date.html', {'att_list': att_list})


@login_required()
def cancel_class(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assc.status = 2
    assc.save()
    return HttpResponseRedirect(reverse('t_class_date', args=(assc.assign_id,)))


@login_required()
def t_attendance(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    ass = assc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'assc': assc,
    }
    return render(request, 'info/t_attendance.html', context)


@login_required()
def edit_att(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    cr = assc.assign.course
    att_list = Attendance.objects.filter(attendanceclass=assc, course=cr)
    context = {
        'assc': assc,
        'att_list': att_list,
    }
    return render(request, 'info/t_edit_att.html', context)


@login_required()
def confirm(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    ass = assc.assign
    cr = ass.course
    cl = ass.class_id
    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        if assc.status == 1:
            try:
                a = Attendance.objects.get(course=cr, student=s, date=assc.date, attendanceclass=assc)
                a.status = status
                a.save()
            except Attendance.DoesNotExist:
                a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
                a.save()
        else:
            a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
            a.save()
            assc.status = 1
            assc.save()

    return HttpResponseRedirect(reverse('t_class_date', args=(ass.id,)))


@login_required()
def t_attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, USN=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/t_att_detail.html', {'att_list': att_list, 'cr': cr})


@login_required()
def change_att(request, att_id):
    a = get_object_or_404(Attendance, id=att_id)
    a.status = not a.status
    a.save()
    return HttpResponseRedirect(reverse('t_attendance_detail', args=(a.student.USN, a.course_id)))


@login_required()
def t_extra_class(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
    }
    return render(request, 'info/t_extra_class.html', context)


@login_required()
def e_confirm(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    cr = ass.course
    cl = ass.class_id
    assc = ass.attendanceclass_set.create(status=1, date=request.POST['date'])
    assc.save()

    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        date = request.POST['date']
        a = Attendance(course=cr, student=s, status=status, date=date, attendanceclass=assc)
        a.save()

    return HttpResponseRedirect(reverse('t_clas', args=(ass.teacher_id, 1)))


@login_required()
def t_report(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    sc_list = []
    for stud in ass.class_id.student_set.all():
        a = StudentCourse.objects.get(student=stud, course=ass.course)
        sc_list.append(a)
    return render(request, 'info/t_report.html', {'sc_list': sc_list})


@login_required()
def timetable(request, class_id):
    asst = AssignTime.objects.filter(assign__class_id=class_id)
    matrix = [['' for i in range(12)] for j in range(6)]

    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(12):
            if j == 0:
                matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                a = asst.get(period=time_slots[t][0], day=d[0])
                matrix[i][j] = a.assign.course_id
            except AssignTime.DoesNotExist:
                pass
            t += 1

    context = {'matrix': matrix}
    return render(request, 'info/timetable.html', context)


@login_required()
def t_timetable(request, teacher_id):
    asst = AssignTime.objects.filter(assign__teacher_id=teacher_id)
    class_matrix = [[True for i in range(12)] for j in range(6)]
    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(12):
            if j == 0:
                class_matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                a = asst.get(period=time_slots[t][0], day=d[0])
                class_matrix[i][j] = a
            except AssignTime.DoesNotExist:
                pass
            t += 1

    context = {
        'class_matrix': class_matrix,
    }
    return render(request, 'info/t_timetable.html', context)


@login_required()
def free_teachers(request, asst_id):
    asst = get_object_or_404(AssignTime, id=asst_id)
    ft_list = []
    t_list = Teacher.objects.filter(assign__class_id__id=asst.assign.class_id_id)
    for t in t_list:
        at_list = AssignTime.objects.filter(assign__teacher=t)
        if not any([True if at.period == asst.period and at.day == asst.day else False for at in at_list]):
            ft_list.append(t)

    return render(request, 'info/free_teachers.html', {'ft_list': ft_list})


# student marks


@login_required()
def marks_list(request, stud_id):
    stud = Student.objects.get(USN=stud_id, )
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    sc_list = []
    for ass in ass_list:
        try:
            sc = StudentCourse.objects.get(student=stud, course=ass.course)
        except StudentCourse.DoesNotExist:
            sc = StudentCourse(student=stud, course=ass.course)
            sc.save()
            sc.marks_set.create(type='I', name='Internal test 1')
            sc.marks_set.create(type='I', name='Internal test 2')
            sc.marks_set.create(type='I', name='Internal test 3')
            sc.marks_set.create(type='E', name='Event 1')
            sc.marks_set.create(type='E', name='Event 2')
            sc.marks_set.create(type='S', name='Semester End Exam')
        sc_list.append(sc)

    return render(request, 'info/marks_list.html', {'sc_list': sc_list})


# teacher marks


@login_required()
def t_marks_list(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    m_list = MarksClass.objects.filter(assign=ass)
    return render(request, 'info/t_marks_list.html', {'m_list': m_list})


@login_required()
def t_marks_entry(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'mc': mc,
    }
    return render(request, 'info/t_marks_entry.html', context)


@login_required()
def marks_confirm(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    cr = ass.course
    cl = ass.class_id
    for s in cl.student_set.all():
        mark = request.POST[s.USN]
        sc = StudentCourse.objects.get(course=cr, student=s)
        m = sc.marks_set.get(name=mc.name)
        m.marks1 = mark
        m.save()
    mc.status = True
    mc.save()

    return HttpResponseRedirect(reverse('t_marks_list', args=(ass.id,)))


@login_required()
def edit_marks(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    cr = mc.assign.course
    stud_list = mc.assign.class_id.student_set.all()
    m_list = []
    for stud in stud_list:
        sc = StudentCourse.objects.get(course=cr, student=stud)
        m = sc.marks_set.get(name=mc.name)
        m_list.append(m)
    context = {
        'mc': mc,
        'm_list': m_list,
    }
    return render(request, 'info/edit_marks.html', context)


@login_required()
def student_marks(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    sc_list = StudentCourse.objects.filter(student__in=ass.class_id.student_set.all(), course=ass.course)
    return render(request, 'info/t_student_marks.html', {'sc_list': sc_list})


@login_required()
def add_teacher(request):
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        dept = get_object_or_404(Dept, id=request.POST['dept'])
        name = request.POST['full_name']
        id = request.POST['id'].lower()
        dob = request.POST['dob']
        sex = request.POST['sex']
        
        # Creating a User with teacher username and password format
        # USERNAME: firstname + underscore + unique ID
        # PASSWORD: firstname + underscore + year of birth(YYYY)
        user = User.objects.create_user(
            username=name.split(" ")[0].lower() + '_' + id,
            password=name.split(" ")[0].lower() + '_' + dob.replace("-","")[:4]
        )
        user.save()

        Teacher(
            user=user,
            id=id,
            dept=dept,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')
    
    all_dept = Dept.objects.order_by('-id')
    context = {'all_dept': all_dept}

    return render(request, 'info/add_teacher.html', context)


@login_required()
def add_student(request):
    # If the user is not admin, they will be redirected to home
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        # Retrieving all the form data that has been inputted
        class_id = get_object_or_404(Class, id=request.POST['class'])
        name = request.POST['full_name']
        dob = request.POST['dob']
        sex = request.POST['sex'] 

        # Creating a User with student username and password format
        # USERNAME: firstname + underscore + year of birth(YYYY)
        user = User.objects.create_user(
            username=name.split(" ")[0].lower() + '_' + dob.replace("-", "")[:4],
            password=name.split(" ")[0].lower() + '_' + dob.replace("-", "")[:4]
        )
        user.save()

        # Creating a new student instance with given data and saving it.
        student = Student(
            user=user,
            class_id=class_id,
            name=name,
            sex=sex,
            DOB=dob
        )
        student.save()  # USN will be generated automatically in the save method
        return redirect('/')
    
    all_classes = Class.objects.order_by('-id')
    context = {'all_classes': all_classes}
    return render(request, 'info/add_student.html', context)


def get_student_semester(request, student_id):
    try:
        student = Student.objects.get(USN=student_id)
        semester = student.class_id.sem if student.class_id else None
        return JsonResponse({
            'status': 'success',
            'semester': semester,
            'message': f'Found semester {semester} for student {student_id}'
        })
    except Student.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'semester': None,
            'message': f'Student with USN {student_id} not found'
        }, status=200)  # Return 200 even for not found, with null semester
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'semester': None,
            'message': str(e)
        }, status=200)  # Return 200 for other errors


@login_required
def library_books(request):
    books = Book.objects.filter(available=True)
    user_loans = LibraryLoan.objects.filter(student=request.user.student, returned=False) if request.user.is_student else None
    return render(request, 'info/library_books.html', {
        'books': books,
        'user_loans': user_loans
    })

@login_required
def borrow_book(request, book_id):
    if not request.user.is_student:
        return HttpResponseRedirect('/library/')
    
    book = get_object_or_404(Book, id=book_id)
    if book.available:
        loan = LibraryLoan.objects.create(
            student=request.user.student,
            book=book
        )
        book.available = False
        book.save()
        return HttpResponseRedirect('/library/')
    return HttpResponseRedirect('/library/')

@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(LibraryLoan, id=loan_id, student=request.user.student)
    loan.returned = True
    loan.save()
    loan.book.available = True
    loan.book.save()
    return HttpResponseRedirect('/library/')

@login_required
def degree_status(request):
    if not request.user.is_student:
        return redirect('/')
        
    student = request.user.student
    clearance = student.check_clearance()
    
    context = {
        'student': student,
        'clearance': clearance,
        'pending_fees': Fee.objects.filter(student=student, is_cleared=False),
        'pending_fines': Fine.objects.filter(student=student, is_paid=False),
        'courses_completed': StudentCourse.objects.filter(student=student, marks__marks1__gte=40).distinct().count(),
        'total_courses': Assign.objects.filter(class_id=student.class_id).count(),
    }
    
    return render(request, 'info/degree_status.html', context)

@login_required
def download_transcript(request):
    if not request.user.is_student:
        return redirect('/')

    student = request.user.student
    clearance = student.check_clearance()

    # Only generate transcript if all requirements are met
    if clearance.is_fee_cleared and clearance.is_fine_cleared and clearance.is_course_completed:
        courses = StudentCourse.objects.filter(student=student)
        transcript_content = f"""
        ACADEMIC TRANSCRIPT
        ==================
        Name: {student.name}
        USN: {student.USN}
        Department: {student.class_id.dept.name}
        Semester: {student.class_id.sem}

        Course Details:
        --------------
        """
        
        for course in courses:
            marks = course.marks_set.all()
            transcript_content += f"""
            {course.course.name}
            - Internal Test 1: {marks.get(name='Internal test 1').marks1}
            - Internal Test 2: {marks.get(name='Internal test 2').marks1}
            - Internal Test 3: {marks.get(name='Internal test 3').marks1}
            - Event 1: {marks.get(name='Event 1').marks1}
            - Event 2: {marks.get(name='Event 2').marks1}
            - Semester End Exam: {marks.get(name='Semester End Exam').marks1}
            """

        # Create response with file download
        response = HttpResponse(transcript_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{student.USN}_transcript.txt"'
        return response
    else:
        messages.error(request, "Cannot generate transcript. Please clear all dues and complete all courses.")
        return redirect('degree_status')