from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Count
from .models import Student, Violation
from .forms import ViolationForm, StudentForm


def log_view(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role == "faculty":
            return redirect("tracker:login")
        elif role == "student":
            return redirect("tracker:student_login")
    return render(request, "tracker/log.html")


def student_login_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        if not student_id:
            messages.error(request, "Please enter a student ID.")
            return render(request, "tracker/login-2.html")

        try:
            student = Student.objects.get(student_id=student_id)
            return redirect("tracker:student_violation", pk=student.pk)
        except Student.DoesNotExist:
            messages.error(request, "Student ID not found.")
            return render(request, "tracker/login-2.html")

    return render(request, "tracker/login-2.html")


def student_violation_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "tracker/student_violations.html", {"student": student})



def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            return render(request, "tracker/pending_approval.html")
    else:
        form = UserCreationForm()
    return render(request, "tracker/signup.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("tracker:student_list")
    else:
        form = AuthenticationForm()
    return render(request, "tracker/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("tracker:log")

def about_view(request):
    return render(request, "tracker/about.html")


@login_required(login_url='tracker:log')
def student_list(request):
    # allow optional ?sort=name or ?sort=college
    sort = request.GET.get("sort", "college")
    if sort == "name":
        students = Student.objects.all().order_by("last_name", "first_name")
    else:
        students = Student.objects.all().order_by("college", "last_name", "first_name")
    return render(request, "tracker/student_list.html", {"students": students})


@login_required(login_url='tracker:log')
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "tracker/student_detail.html", {"student": student})


@login_required(login_url='tracker:log')
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added")
            return redirect("tracker:student_list")
    else:
        form = StudentForm()
    return render(request, "tracker/violation_form.html", {"form": form})


@login_required(login_url='tracker:log')
def add_violation(request):
    initial = {}
    student_pk = request.GET.get("student")
    if student_pk:
        try:
            initial["student"] = Student.objects.get(pk=student_pk)
        except Student.DoesNotExist:
            pass

    if request.method == "POST":
        form = ViolationForm(request.POST)
        if form.is_valid():
            violation = form.save() 
            student = violation.student
            student.noted = violation.level == 3
            student.save(update_fields=["noted"])

            messages.success(request, "Violation recorded")
            return redirect("tracker:student_list")
    else:
        form = ViolationForm(initial=initial)

    return render(request, "tracker/violation_form.html", {"form": form})


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def college_analytics(request):
    college_choices = dict(Student.college.field.choices)
    violation_counts_query = (
        Violation.objects.values("student__college")
        .annotate(count=Count("id"))
        .order_by("student__college")
    )

    violation_counts = {item["student__college"]: item["count"] for item in violation_counts_query}

    
    college_labels = list(college_choices.values())
    violation_data = [violation_counts.get(abbr, 0) for abbr, name in Student.college.field.choices]

    
    college_colors = {
        "CAS": "rgba(0, 128, 0, 0.6)",   
        "CIT": "rgba(255, 0, 0, 0.6)",  
        "COE": "rgba(255, 165, 0, 0.6)", 
        "CBMA": "rgba(255, 255, 0, 0.6)",
        "CCS": "rgba(128, 128, 128, 0.6)",
        "COED": "rgba(0, 0, 255, 0.6)",
    }

    background_colors = [college_colors.get(abbr, "rgba(0,0,0,0.6)") for abbr, _ in Student.college.field.choices]
    border_colors = [color.replace("0.6", "1") for color in background_colors]  

    context = {
        "college_labels": college_labels,
        "violation_data": violation_data,
        "background_colors": background_colors,
        "border_colors": border_colors,
    }
    return render(request, "tracker/college_analytics.html", context)


