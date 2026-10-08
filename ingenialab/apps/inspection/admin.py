from django.contrib import admin

from .models import InspectionExercise, InspectionFragment


class FragmentInline(admin.TabularInline):
    model = InspectionFragment
    extra = 0


@admin.register(InspectionExercise)
class InspectionExerciseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "is_active")
    inlines = [FragmentInline]
