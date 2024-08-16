from django.contrib import admin
from rate_employees.models import Employee,Award


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'empid', 'enothi_id', 'ename', 'eemail', 'edesignation', 'edept', 'esection','edivision','edirectorate','counter')
# Register your models here.
admin.site.register(Employee, EmployeeAdmin)
class Awardemployees(admin.ModelAdmin):
    list_display = ('awardid', 'award_evaluatorid', 'award_evaluateeid', 'purposeid', 'description','created_date')
admin.site.register(Award, Awardemployees)
