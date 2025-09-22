from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import RegexValidator

class Student(models.Model):
    student_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{1,8}$', message="ID must be numeric and up to 8 digits.")]
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    course_year_section = models.CharField(max_length=150, blank=True, null=True)

    college = models.CharField(
        max_length=100,
        choices=[
            ("CAS", "College of Arts and Sciences"),
            ("CIT", "College of Industrial Technology"),
            ("COE", "College of Engineering"),
            ("CBMA", "College of Business Management and Accountancy"),
            ("CCS", "College of Computer Studies"),
            ("COED", "College of Education"),
        ],
        blank=True,
        null=True,
    )

    noted = models.BooleanField(default=False)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.student_id} - {self.last_name}, {self.first_name}"


class Violation(models.Model):
    OFFENSE_LEVELS = [
        (0, "Select Offense Level"),  
        (1, "First Offense"),
        (2, "Second Offense"),
        (3, "Third Offense"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="violations")
    offense = models.CharField(
        max_length=255,
        verbose_name="Reason for the Offense / Student’s Explanation",
        help_text="(Provide your reason or explanation why the violation occurred. Include any circumstances you want the Office of Student Affairs to consider.)"
    )
    level = models.PositiveSmallIntegerField(choices=OFFENSE_LEVELS, default=1)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.student.student_id} - {self.offense} ({self.get_level_display()})"

def _update_noted_status(student_or_pk):
    """Mark student.noted True if total violations >= 3."""
    if isinstance(student_or_pk, Student):
        pk = student_or_pk.pk
    else:
        pk = student_or_pk

    student = Student.objects.filter(pk=pk).first()
    if not student:
        return  # student deleted

    # Count total violations
    total_violations = student.violations.count()
    should_be_noted = total_violations == 3  # noted if 3 or more violations

    if student.noted != should_be_noted:
        student.noted = should_be_noted
        student.save(update_fields=["noted"])



@receiver(post_save, sender=Violation)
def on_violation_saved(sender, instance: Violation, created, **kwargs):
    _update_noted_status(instance.student_id)

@receiver(post_delete, sender=Violation)
def on_violation_deleted(sender, instance: Violation, **kwargs):
    if Student.objects.filter(pk=instance.student_id).exists():
        _update_noted_status(instance.student_id)
