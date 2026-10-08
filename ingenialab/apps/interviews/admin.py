from django.contrib import admin

from .models import InterviewQuestion, MasterRequirement, ScenarioVersion, StudentAttempt


class QuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0


@admin.register(ScenarioVersion)
class ScenarioVersionAdmin(admin.ModelAdmin):
    list_display = ("scenario_code", "version_number", "title", "is_active")
    inlines = [QuestionInline]


admin.site.register(MasterRequirement)
admin.site.register(StudentAttempt)
