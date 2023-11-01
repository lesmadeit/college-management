from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
import datetime
from .models import CustomUser, Staffs, Courses, Subjects, Students, Attendance, AttendanceReport, LeaveReoprtStudent, FeedBackStudent, StudentResult

def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj,
                                                         status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj,
                                                         status=False).count()
    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_subjects = Subjects.objects.filter(course_id=course_obj).count()
    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance,
															status=True,
															student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance,
															status=False,
															student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance.present_count)
        data_absent.append(attendance_absent_count)

        context={
            "total_attendance": total_attendance,
            "attendance_present": attendance_present,
            "attendance_absent": attendance_absent,
		    "total_subjects": total_subjects,
		    "subject_name": subject_name,
		    "data_present": data_present,
		    "data_absent": data_absent
        }
        return render(request, "student_template/student_home_template.html")
    

def student_view_attendance(request):

    # Getting Logged in Student Data
    student = Students.objects.get(admin=request.user.id)

    # Getting Course Enrolled of LoggedIn Student
    course = student.course_id

    # Getting the Subjects of Course Enrolled
    subjects = Subjects.objects.filter(course_id=course) 
    context = {
		"subjects": subjects
	}
    return render(request, "student_template/student_view_attendance.html", context)


def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')
    else:
        # Getting all the input data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        subject_obj = Subjects.objects.get(id=subject_id)

        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)

        # Getting Student Data Based on Logged in Data
        stud_obj = Students.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date
		# Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse,
																	end_date_parse),
											subject_id=subject_obj)
        # Getting Attendance Report based on the attendance
		# details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance,
															student_id=stud_obj)
        

        context = {
			"subject_obj": subject_obj,
			"attendance_reports": attendance_reports
		}
        
        return render(request, 'student_template/student_attendance_data.html', context)


