from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),  # ✅ added signup
    path("", views.student_list, name="student_list"),
    path("students/add/", views.add_student, name="add_student"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("violations/add/", views.add_violation, name="add_violation"),
    path("analytics/", views.college_analytics, name="college_analytics"),
]
