import datetime
import os
from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from datetime import timedelta
from django.conf import settings

# Create your models here.
sex_choice = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

time_slots = (
    ('7:30 - 8:30', '7:30 - 8:30'),
    ('8:30 - 9:30', '8:30 - 9:30'),
    ('9:30 - 10:30', '9:30 - 10:30'),
    ('11:00 - 11:50', '11:00 - 11:50'),
    ('11:50 - 12:40', '11:50 - 12:40'),
    ('12:40 - 1:30', '12:40 - 1:30'),
    ('2:30 - 3:30', '2:30 - 3:30'),
    ('3:30 - 4:30', '3:30 - 4:30'),
    ('4:30 - 5:30', '4:30 - 5:30'),
)

DAYS_OF_WEEK = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)

test_name = (
    ('Internal test 1', 'Internal test 1'),
    ('Internal test 2', 'Internal test 2'),
    ('Internal test 3', 'Internal test 3'),
    ('Event 1', 'Event 1'),
    ('Event 2', 'Event 2'),
    ('Semester End Exam', 'Semester End Exam'),
)


class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, 'student'):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, 'teacher'):
            return True
        return False


class Dept(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Course(models.Model):
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=50)
    shortname = models.CharField(max_length=50, default='X')

    def __str__(self):
        return self.name


class Class(models.Model):
    # courses = models.ManyToManyField(Course, default=1)
    id = models.CharField(primary_key='True', max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    section = models.CharField(max_length=100)
    sem = models.IntegerField()

    class Meta:
        verbose_name_plural = 'classes'

    def __str__(self):
        d = Dept.objects.get(name=self.dept)
        return '%s : %d %s' % (d.name, self.sem, self.section)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    USN = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=50, choices=sex_choice, default='Male')
    DOB = models.DateField(default='1998-01-01')

    def generate_duty_card(self):
        department_name = self.class_id.dept.name if self.class_id and self.class_id.dept else "No Department"
        fee_details = Fee.objects.filter(student=self).first()
        fee_info = f"""
        Fee Details:
        Amount Due: {fee_details.amount_due if fee_details else 'N/A'}
        Amount Paid: {fee_details.amount_paid if fee_details else 'N/A'}
        Due Date: {fee_details.due_date if fee_details else 'N/A'}
        Status: {'Cleared' if fee_details and fee_details.is_cleared else 'Pending'}
        """
        fine_summary = self.get_fine_summary()
        active_loans = self.get_active_loans()
        
        loan_info = "\nLibrary Loans:\n"
        for loan in active_loans:
            loan_info += f"- {loan.book.title} (Due: {loan.issue_date + datetime.timedelta(days=14)})\n"
        
        fine_info = f"""
        Fines Summary:
        Library Fines: {fine_summary['library_fines']}
        Late Fees: {fine_summary['late_fees']}
        Total Outstanding: Rs. {fine_summary['total_amount']}
        """
        
        return f"""
        Duty Card
        =========
        Department: {department_name}
        USN: {self.USN}
        Name: {self.name}
        Gender: {self.sex}
        Date of Birth: {self.DOB}
        Class ID: {self.class_id.id if self.class_id else "N/A"}
        User ID: {self.user.id if self.user else "N/A"}
        {fee_info}
        {loan_info}
        {fine_info}
        """

    def generate_duty_card_file(self):
        duty_card_content = self.generate_duty_card()
        file_path = os.path.join(settings.MEDIA_ROOT, f"duty_cards/{self.USN}.txt")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
        with open(file_path, 'w') as f:
            f.write(duty_card_content)
        return file_path  # Return the file path for further use

    def check_clearance(self):
        clearance, created = Clearance.objects.get_or_create(student=self)
        clearance.is_fee_cleared = not Fee.objects.filter(student=self, is_cleared=False).exists()
        clearance.is_fine_cleared = not Fine.objects.filter(student=self, is_paid=False).exists()
        clearance.is_course_completed = self.studentcourse_set.count() == Assign.objects.filter(class_id=self.class_id).count()
        clearance.is_degree_awarded = clearance.is_fee_cleared and clearance.is_fine_cleared and clearance.is_course_completed
        clearance.save()
        return clearance

    def generate_transcript(self):
        results = Result.objects.filter(student=self).order_by('semester')
        transcript = "Transcript\n==========\n"
        for result in results:
            transcript += f"Semester {result.semester}: GPA {result.gpa}\n"
        return transcript

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if this is a new student
        if not self.USN:  # Generate USN only if it is not already set
            self.USN = self.generate_usn()
        super().save(*args, **kwargs)
        
        # Create fee entry for new students
        if is_new:
            Fee.objects.create(
                student=self,
                semester=self.class_id.sem,
                amount_due=50000.00,  # Default fee amount
                due_date=datetime.date.today() + datetime.timedelta(days=30),  # Due in 30 days
            )

    def get_active_loans(self):
        return LibraryLoan.objects.filter(student=self, returned=False)

    def get_fine_summary(self):
        fines = Fine.objects.filter(student=self, is_paid=False)
        total = sum(fine.amount for fine in fines)
        return {
            'library_fines': fines.filter(category='LIBRARY').count(),
            'late_fees': fines.filter(category='LATE_FEE').count(),
            'total_amount': total
        }

    def is_eligible_for_degree(self):
        clearance = self.check_clearance()
        return clearance.is_degree_awarded

    def generate_usn(self):
        year = datetime.date.today().year % 100  # Get the last two digits of the current year
        dept_code = self.class_id.dept.id.lower()  # Use the department ID as the department code
        # Filter students by year and department to get the last serial number for the department
        last_student = Student.objects.filter(USN__startswith=f"{year}-{dept_code}-").order_by('-USN').first()
        if last_student:
            last_serial = int(last_student.USN.split('-')[-1])
            new_serial = f"{last_serial + 1:02d}"  # Increment and format as two digits
        else:
            new_serial = "01"  # Start with 01 if no students exist for the department
        return f"{year}-{dept_code}-{new_serial}"

    def save(self, *args, **kwargs):
        if not self.USN:  # Generate USN only if it is not already set
            self.USN = self.generate_usn()
        super().save(*args, **kwargs)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=sex_choice, default='Male')
    DOB = models.DateField(default='1980-01-01')

    def __str__(self):
        return self.name


class Assign(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('course', 'class_id', 'teacher'),)

    def __str__(self):
        cl = Class.objects.get(id=self.class_id_id)
        cr = Course.objects.get(id=self.course_id)
        te = Teacher.objects.get(id=self.teacher_id)
        return '%s : %s : %s' % (te.name, cr.shortname, cl)


class AssignTime(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    period = models.CharField(max_length=50, choices=time_slots, default='11:00 - 11:50')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)


class AttendanceClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance'


class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendanceclass = models.ForeignKey(AttendanceClass, on_delete=models.CASCADE, default=1)
    date = models.DateField(default='2018-10-23')
    status = models.BooleanField(default='True')

    def __str__(self):
        sname = Student.objects.get(name=self.student)
        cname = Course.objects.get(name=self.course)
        return '%s : %s' % (sname.name, cname.shortname)


class AttendanceTotal(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('student', 'course'),)

    @property
    def att_class(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        att_class = Attendance.objects.filter(course=cr, student=stud, status='True').count()
        return att_class

    @property
    def total_class(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        return total_class

    @property
    def attendance(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        att_class = Attendance.objects.filter(course=cr, student=stud, status='True').count()
        if total_class == 0:
            attendance = 0
        else:
            attendance = round(att_class / total_class * 100, 2)
        return attendance

    @property
    def classes_to_attend(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        att_class = Attendance.objects.filter(course=cr, student=stud, status='True').count()
        cta = math.ceil((0.75 * total_class - att_class) / 0.25)
        if cta < 0:
            return 0
        return cta


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('student', 'course'),)
        verbose_name_plural = 'Marks'

    def __str__(self):
        sname = Student.objects.get(name=self.student)
        cname = Course.objects.get(name=self.course)
        return '%s : %s' % (sname.name, cname.shortname)

    def get_cie(self):
        marks_list = self.marks_set.all()
        m = []
        for mk in marks_list:
            m.append(mk.marks1)
        cie = math.ceil(sum(m[:5]) / 2)
        return cie

    def get_attendance(self):
        a = AttendanceTotal.objects.get(student=self.student, course=self.course)
        return a.attendance


class Marks(models.Model):
    studentcourse = models.ForeignKey(StudentCourse, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=test_name, default='Internal test 1')
    marks1 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        unique_together = (('studentcourse', 'name'),)

    @property
    def total_marks(self):
        if self.name == 'Semester End Exam':
            return 100
        return 20


class MarksClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=test_name, default='Internal test 1')
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = (('assign', 'name'),)

    @property
    def total_marks(self):
        if self.name == 'Semester End Exam':
            return 100
        return 20


class AttendanceRange(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()


class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.IntegerField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    is_cleared = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - Semester {self.semester} Fee"

    def calculate_balance(self):
        return self.amount_due - self.amount_paid

    def save(self, *args, **kwargs):
        if not self.semester and self.student.class_id:
            self.semester = self.student.class_id.sem  # Auto-fill semester from the student's class
        super().save(*args, **kwargs)


class Fine(models.Model):
    CATEGORY_CHOICES = [
        ('LIBRARY', 'Library Fine'),
        ('LATE_FEE', 'Late Fee'),
        ('OTHER', 'Other')
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')

    def __str__(self):
        return f"{self.student.name} - {self.reason}"


class Book(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.id})"


class LibraryLoan(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.book.title}"

    def save(self, *args, **kwargs):
        if self.returned and not self.return_date:
            self.return_date = datetime.date.today()
            # Calculate and create fine if returned late
            days_late = (self.return_date - self.issue_date).days - 14  # 14 days loan period
            if days_late > 0:
                Fine.objects.create(
                    student=self.student,
                    reason=f"Late return of book: {self.book.title}",
                    amount=days_late * 10,  # Rs. 10 per day
                    category='LIBRARY'
                )
        super().save(*args, **kwargs)


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.IntegerField()
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    transcript = models.TextField()

    def __str__(self):
        return f"{self.student.name} - Semester {self.semester} Result"


class Clearance(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    is_fee_cleared = models.BooleanField(default=False)
    is_fine_cleared = models.BooleanField(default=False)
    is_course_completed = models.BooleanField(default=False)
    is_degree_awarded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - Clearance Status"

    def update_status(self):
        """Automatically update clearance status"""
        self.student.check_clearance()
        return self.is_degree_awarded


# Triggers

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


days = {
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
}


def create_attendance(sender, instance, **kwargs):
    if kwargs['created']:
        start_date = AttendanceRange.objects.all()[:1].get().start_date
        end_date = AttendanceRange.objects.all()[:1].get().end_date
        for single_date in daterange(start_date, end_date):
            if single_date.isoweekday() == days[instance.day]:
                try:
                    AttendanceClass.objects.get(date=single_date.strftime("%Y-%m-%d"), assign=instance.assign)
                except AttendanceClass.DoesNotExist:
                    a = AttendanceClass(date=single_date.strftime("%Y-%m-%d"), assign=instance.assign)
                    a.save()


def create_marks(sender, instance, **kwargs):
    if kwargs['created']:
        if hasattr(instance, 'name'):
            ass_list = instance.class_id.assign_set.all()
            for ass in ass_list:
                try:
                    StudentCourse.objects.get(student=instance, course=ass.course)
                except StudentCourse.DoesNotExist:
                    sc = StudentCourse(student=instance, course=ass.course)
                    sc.save()
                    sc.marks_set.create(name='Internal test 1')
                    sc.marks_set.create(name='Internal test 2')
                    sc.marks_set.create(name='Internal test 3')
                    sc.marks_set.create(name='Event 1')
                    sc.marks_set.create(name='Event 2')
                    sc.marks_set.create(name='Semester End Exam')
        elif hasattr(instance, 'course'):
            stud_list = instance.class_id.student_set.all()
            cr = instance.course
            for s in stud_list:
                try:
                    StudentCourse.objects.get(student=s, course=cr)
                except StudentCourse.DoesNotExist:
                    sc = StudentCourse(student=s, course=cr)
                    sc.save()
                    sc.marks_set.create(name='Internal test 1')
                    sc.marks_set.create(name='Internal test 2')
                    sc.marks_set.create(name='Internal test 3')
                    sc.marks_set.create(name='Event 1')
                    sc.marks_set.create(name='Event 2')
                    sc.marks_set.create(name='Semester End Exam')


def create_marks_class(sender, instance, **kwargs):
    if kwargs['created']:
        for name in test_name:
            try:
                MarksClass.objects.get(assign=instance, name=name[0])
            except MarksClass.DoesNotExist:
                m = MarksClass(assign=instance, name=name[0])
                m.save()


def delete_marks(sender, instance, **kwargs):
    stud_list = instance.class_id.student_set.all()
    StudentCourse.objects.filter(course=instance.course, student__in=stud_list).delete()


post_save.connect(create_marks, sender=Student)
post_save.connect(create_marks, sender=Assign)
post_save.connect(create_marks_class, sender=Assign)
post_save.connect(create_attendance, sender=AssignTime)
post_delete.connect(delete_marks, sender=Assign)
