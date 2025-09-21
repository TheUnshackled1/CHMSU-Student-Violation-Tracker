from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Count
from .models import Student, Violation
from .forms import ViolationForm, StudentForm

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # ✅ Require approval
            user.save()
            # Don’t log them in yet
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
    return redirect("tracker:login")


@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, "tracker/student_list.html", {"students": students})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "tracker/student_detail.html", {"student": student})


@login_required
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


@login_required
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
            violation = form.save()  # save violation with selected level

            # ✅ Update student.noted automatically if violation is "Third Offense"
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

    # Labels & data
    college_labels = list(college_choices.values())
    violation_data = [violation_counts.get(abbr, 0) for abbr, name in Student.college.field.choices]

    # Match colors to abbreviations
    college_colors = {
        "CAS": "rgba(0, 128, 0, 0.6)",   # Green
        "CIT": "rgba(255, 0, 0, 0.6)",   # Red
        "COE": "rgba(255, 165, 0, 0.6)", # Orange
        "CBMA": "rgba(255, 255, 0, 0.6)",# Yellow
        "CCS": "rgba(128, 128, 128, 0.6)",# Gray
        "COED": "rgba(0, 0, 255, 0.6)",  # Blue
    }

    background_colors = [college_colors.get(abbr, "rgba(0,0,0,0.6)") for abbr, _ in Student.college.field.choices]
    border_colors = [color.replace("0.6", "1") for color in background_colors]  # darker border

    context = {
        "college_labels": college_labels,
        "violation_data": violation_data,
        "background_colors": background_colors,
        "border_colors": border_colors,
    }
    return render(request, "tracker/college_analytics.html", context)
