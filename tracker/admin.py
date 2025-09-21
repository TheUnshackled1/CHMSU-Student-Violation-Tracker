from django.contrib import admin
from .models import Student, Violation


class ViolationInline(admin.TabularInline):
	model = Violation
	extra = 0
	readonly_fields = ("occurred_at",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("student_id", "first_name", "last_name", "noted", "violation_count")
	list_filter = ("noted",)
	search_fields = ("student_id", "first_name", "last_name")
	inlines = (ViolationInline,)

	def violation_count(self, obj):
		return obj.violations.count()


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
	list_display = ("student", "offense", "level", "occurred_at")
	list_filter = ("level",)
	search_fields = ("offense", "student__student_id", "student__first_name", "student__last_name")
