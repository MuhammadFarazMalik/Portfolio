from datetime import timedelta, datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path
import os
from django.utils.safestring import mark_safe

from .models import Dept, Class, Student, Attendance, Course, Teacher, Assign, AssignTime, AttendanceClass
from .models import StudentCourse, Marks, User, AttendanceRange, Fee, Fine, Result, Clearance, Book, LibraryLoan

# Register your models here.

days = {
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
}


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class ClassInline(admin.TabularInline):
    model = Class
    extra = 0


class DeptAdmin(admin.ModelAdmin):
    inlines = [ClassInline]
    list_display = ('name', 'id')
    search_fields = ('name', 'id')
    ordering = ['name']


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'dept', 'sem', 'section')
    search_fields = ('id', 'dept__name', 'sem', 'section')
    ordering = ['dept__name', 'sem', 'section']
    inlines = [StudentInline]


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dept')
    search_fields = ('id', 'name', 'dept__name')
    ordering = ['dept', 'id']


class AssignTimeInline(admin.TabularInline):
    model = AssignTime
    extra = 0


class AssignAdmin(admin.ModelAdmin):
    inlines = [AssignTimeInline]
    list_display = ('class_id', 'course', 'teacher')
    search_fields = ('class_id__dept__name', 'class_id__id', 'course__name', 'teacher__name', 'course__shortname')
    ordering = ['class_id__dept__name', 'class_id__id', 'course__id']
    raw_id_fields = ['class_id', 'course', 'teacher']


class MarksInline(admin.TabularInline):
    model = Marks
    extra = 0


class StudentCourseAdmin(admin.ModelAdmin):
    inlines = [MarksInline]
    list_display = ('student', 'course',)
    search_fields = ('student__name', 'course__name', 'student__class_id__id', 'student__class_id__dept__name')
    ordering = ('student__class_id__dept__name', 'student__class_id__id', 'student__USN')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('USN', 'name', 'class_id', 'user_id', 'usn_user_id', 'display_duty_card', 'download_duty_card_link', 'display_fee_status')
    search_fields = ('USN', 'name', 'class_id__id', 'class_id__dept__name')
    ordering = ['class_id__dept__name', 'class_id__id', 'USN']
    readonly_fields = ('USN',)  # Make USN read-only in the admin panel

    class Media:
        # Include custom JavaScript for auto-filling the USN field
        js = ('admin/js/student_usn_autofill.js',)

    def usn_user_id(self, obj):
        return f"{obj.USN}-{obj.user_id}"

    usn_user_id.short_description = "USN-User ID"

    def display_duty_card(self, obj):
        duty_card = obj.generate_duty_card().replace('\n', '<br>')
        return mark_safe(duty_card)  # Render HTML properly

    display_duty_card.short_description = "Duty Card"

    def download_duty_card_link(self, obj):
        link = f'<a href="/admin/info/student/{obj.USN}/download_duty_card/">Download Duty Card</a>'
        return mark_safe(link)  # Render HTML properly

    download_duty_card_link.short_description = "Download Duty Card"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<str:usn>/download_duty_card/', self.admin_site.admin_view(self.download_duty_card), name='download_duty_card'),
        ]
        return custom_urls + urls

    def download_duty_card(self, request, usn):
        student = Student.objects.get(USN=usn)
        file_path = student.generate_duty_card_file()

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{usn}_duty_card.txt"'
                response.write(f"\nUSN-User ID: {student.USN}-{student.user_id}")  # Add USN-User ID to file
                return response
        else:
            self.message_user(request, "Duty card file not found.")
            return HttpResponseRedirect("../")

    def display_fee_status(self, obj):
        fee = Fee.objects.filter(student=obj).first()
        if fee:
            status = 'Cleared' if fee.is_cleared else 'Pending'
            return mark_safe(f"""
                Fee Status: {status}<br>
                Amount Due: {fee.amount_due}<br>
                Amount Paid: {fee.amount_paid}<br>
                Due Date: {fee.due_date}
            """)
        return 'No fee record'

    display_fee_status.short_description = "Fee Status"


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'dept')
    search_fields = ('name', 'dept__name')
    ordering = ['dept__name', 'name']


class AttendanceClassAdmin(admin.ModelAdmin):
    list_display = ('assign', 'date', 'status')
    ordering = ['assign', 'date']
    change_list_template = 'admin/attendance/attendance_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('reset_attd/', self.reset_attd, name='reset_attd'),
        ]
        return my_urls + urls

    def reset_attd(self, request):

        start_date = datetime.strptime(request.POST['startdate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST['enddate'], '%Y-%m-%d').date()

        try:
            a = AttendanceRange.objects.all()[:1].get()
            a.start_date = start_date
            a.end_date = end_date
            a.save()
        except AttendanceRange.DoesNotExist:
            a = AttendanceRange(start_date=start_date, end_date=end_date)
            a.save()

        Attendance.objects.all().delete()
        AttendanceClass.objects.all().delete()
        for asst in AssignTime.objects.all():
            for single_date in daterange(start_date, end_date):
                if single_date.isoweekday() == days[asst.day]:
                    try:
                        AttendanceClass.objects.get(date=single_date.strftime("%Y-%m-%d"), assign=asst.assign)
                    except AttendanceClass.DoesNotExist:
                        a = AttendanceClass(date=single_date.strftime("%Y-%m-%d"), assign=asst.assign)
                        a.save()

        self.message_user(request, "Attendance Dates reset successfully!")
        return HttpResponseRedirect("../")


class FeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'amount_due', 'amount_paid', 'due_date', 'is_cleared')
    search_fields = ('student__name', 'semester')
    ordering = ['student__name', 'semester']

    class Media:
        # Include custom JavaScript for auto-filling the semester field
        js = ('admin/js/fee_autofill.js',)

    def save_model(self, request, obj, form, change):
        # Auto-fill the semester field if not already set
        if not obj.semester and obj.student.class_id:
            obj.semester = obj.student.class_id.sem  # Assuming `sem` is the semester field in the Class model
        super().save_model(request, obj, form, change)


class FineAdmin(admin.ModelAdmin):
    list_display = ('student', 'category', 'reason', 'amount', 'is_paid', 'created_date')
    search_fields = ('student__name', 'reason')
    list_filter = ('category', 'is_paid')
    ordering = ['-created_date']


class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'gpa')
    search_fields = ('student__name', 'semester')
    ordering = ['student__name', 'semester']


class ClearanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'is_fee_cleared', 'is_fine_cleared', 'is_course_completed', 'is_degree_awarded')
    search_fields = ('student__name',)
    ordering = ['student__name']


class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'isbn', 'available')
    search_fields = ('id', 'title', 'author', 'isbn')
    ordering = ['title']


class LibraryLoanAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'issue_date', 'return_date', 'returned', 'days_overdue')
    search_fields = ('student__name', 'book__title')
    list_filter = ('returned',)
    ordering = ['-issue_date']

    def days_overdue(self, obj):
        if not obj.returned:
            due_date = obj.issue_date + datetime.timedelta(days=14)
            if datetime.date.today() > due_date:
                return (datetime.date.today() - due_date).days
        return 0
    days_overdue.short_description = 'Days Overdue'


admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Assign, AssignAdmin)
admin.site.register(StudentCourse, StudentCourseAdmin)
admin.site.register(AttendanceClass, AttendanceClassAdmin)
admin.site.register(Fee, FeeAdmin)
admin.site.register(Fine, FineAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Clearance, ClearanceAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(LibraryLoan, LibraryLoanAdmin)
