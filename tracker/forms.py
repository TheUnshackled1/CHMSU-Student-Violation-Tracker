from django import forms
from .models import Violation, Student


class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ["student", "offense", "level"]
        widgets = {
            "offense": forms.TextInput(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-select"}),
            "student": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_level(self):
        level = self.cleaned_data.get("level")
        if level == 1:  # placeholder
            raise forms.ValidationError("Please select a valid offense level.")
        return level



class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_id", "first_name", "last_name", "course_year_section", "college"]
        widgets = {
            "student_id": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "course_year_section": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. BSIS 3A"}),
            "college": forms.Select(attrs={"class": "form-control"}),
        }
