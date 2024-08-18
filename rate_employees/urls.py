from django.urls import path
from . import views

urlpatterns = [
    
    path('home/',views.home, name='home'),
    path('show_employees/',views.employees_info),
    path('home/select-evaluatee/',views.select_evaluatee, name='select-evaluatee'),
    path('home/select-evaluatee/evaluate/<int:emp_id>/',views.evaluate, name='evaluate'),
    #path('home/select-evaluatee/evaluate',views.evaluate, name='testEvaluate'),

   
    path('home/show_employees/mark',views.mark_employees),
    path('registration/',views.registerPage, name='registration'),
    path('login/',views.loginPage, name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('home/profile/',views.showProfileData, name='profile'),
    path('home/query/',views.showReport, name='query'),
    path('home/awardreport/',views.AwardReport, name='awardreport'),
    path('home/award/',views.AwardSystem, name='award'),
    path('home/write-award-description/<int:emp_id>/',views.writeAwardDescription, name='writeAwardDescription'),
    path('approve_award/<int:notification_id>/', views.approve_award, name='approve_award'),
    path('home/dashboard/', views.dashboard, name='dashboard'),
    path('change-password/',views.change_password,name='change-password'),
    path('home/dashboard/api/award-distribution/<int:enothi_id>/', views.award_distribution, name='award_distribution'),
    path('home/dashboard/api/advisor-status/', views.advisor_status, name='advisor_status'),
    path('home/dashboard/api/award-data/', views.award_data, name='award_data'),
    path('home/dashboard/api/search-employee/', views.search_employee, name='search_employee'),
    path('home/award/api/search-award/', views.search_employee, name='search_award'),
    #path('home/dashboard/api/search-advisor/', views.search_advisor, name='search_advisor'),
    path('home/dashboard/api/award_pie/<int:enothi_id>/', views.award_pie, name='award_pie'),
    path('home/dashboard/api/top-employees/', views.top_employees, name='top-employees'),
    path('home/dashboard/api/employee-awards/<int:enothi_id>/', views.get_employee_awards, name='employee_awards'),
    path('home/dashboard/', views.dashboard, name='dashboard'),

    #path('api/top-evaluators-evaluatees/', views.top_evaluators_evaluatees, name='top_evaluators_evaluatees'),
]
     

