

from django.http import HttpResponse
from django.shortcuts import render, redirect
from rate_employees.models import Employee, Evaluation, Designation, Award,Notification
from . registrationForm import EmployeeRegistration
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F
from .serializers import AwardSerializer
from django.contrib.auth.models import User

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.core.serializers import serialize
import json
from . import petro


# Create your views here.

@login_required(login_url='login')
def home(request):
    #current_user=Employee.objects.get(enothi_id=request.user.username)
    #if not current_user:
    if request.user.username == '0001' or request.user.username == '0002' or request.user.username == '0003' :
        current_user = User.objects.get(username=request.user.username)
        employee_name=current_user.first_name
    else:
        current_user=Employee.objects.get(enothi_id=request.user.username)
        employee_name=current_user.ename
        
    context={
            'employee_name':employee_name
        }
    
    return render(request,'employees/homePage.html',context)

@login_required(login_url='login')
def employees_info(request):
    employee = Employee.objects.all()
    return render (request, 'employees/evaluation.html', {'emp': employee} )

@login_required(login_url='login')
def mark_employees(request):
    return render (request, 'employees/mark.html')

def registerPage(request):

    if request.user.is_authenticated:
        current_user=Employee.objects.get(enothi_id=request.user)
        counter=current_user.counter
        context={
            'counter':counter
        }
        return redirect('home',context)
    else:

        if request.method == "POST":
            fm = UserCreationForm(request.POST)
            if fm.is_valid():
                fm.save()
                print("this post from registration")
                return redirect('home')
        else:
            fm = UserCreationForm()
        return render(request,'employees/registration.html',{'form': fm})

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else :
                messages.info(request, 'Username or Password is incorrect')

        return render(request,'employees/login.html')
    #reza_update
    
def change_password(request):
    current_user=Employee.objects.get(enothi_id=request.user)
    employee_name=current_user.ename  
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session with new password hash
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
    else:
        print("executed!!")
        form = PasswordChangeForm(request.user)
        
     
        context = {
               
                'form': form,
                'employee_name':employee_name
               
                }
    return render (request,'employees/change_password.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

#reza_update

@login_required(login_url='login')
def showProfileData(request):
    # user_id = request.user.username
    mydata = Employee.objects.filter(enothi_id=request.user).values()
    evaluation_count = Evaluation.objects.filter(evaluatorid=mydata[0]['empid']).count()
    employee_count = Employee.objects.values().count()
    current_user=Employee.objects.get(enothi_id=request.user)
    counter=current_user.counter
    print("Evaluation count!!!")
    print("employee id ", mydata[0]['empid'])
    print(evaluation_count, " ", employee_count)
    if mydata.exists():
        print("mydata exists!!")
        print(request.POST)
        context = {
            'myProfileData': mydata[0],
            'division_name': mydata[0]['edivision'],
            'designation_name' : mydata[0]['edesignation'],
            'evaluation_count': evaluation_count,
            'employee_count': employee_count,
            'counter': counter,
            'employee_name': current_user.ename
            
        }

        print("This is my data", mydata[0]['ename'])

        return render(request, 'employees/profile3.html', context)

    print("No employee data!!!")
    return redirect('home')


#reza_update
@login_required(login_url='login')
def select_evaluatee(request):
    evaluator_empid = Employee.objects.filter(Q(enothi_id = request.user)).values('empid')[0]['empid']
    #preevaluatees = Evaluation.objects.filter(Q(evaluatorid = int(request.user.username))).values('evaluateeid')
    preevaluatees = Evaluation.objects.filter(Q(evaluatorid = evaluator_empid)).values('evaluateeid')
    current_user=Employee.objects.get(enothi_id=request.user)
    #preevaluatee_ids = [item['evaluateeid'] for item in preevaluatees]

    if request.method == 'POST':
      
        print(int(request.user.username))
        if 'designations' in request.POST:
            selected_designations = request.POST.getlist('designations')
            print(selected_designations)
            print(request.user)
            evaluator_empid = Employee.objects.filter(Q(enothi_id = request.user)).values('empid')[0]['empid']
            print("Evaluator employee id",evaluator_empid)
            employees = Employee.objects.filter(Q(edesignation__in=selected_designations), ~Q(empid = evaluator_empid),  ~Q(empid__in=preevaluatees) ).values('empid', 'ename','enothi_id')
            
            employee_list = list(employees)
            return JsonResponse(employee_list, safe=False)
        elif 'employee' in request.POST: # Go for evaluation

            print("no designation here")
            print(request.POST['employee'][0:5])
            evaluatee_empid = int(request.POST['employee'][0:5])
            evaluator_empid = Employee.objects.filter(Q(enothi_id = request.user)).values('empid')[0]['empid']
            evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()
            context = {
                'evaluateeData': evaluatee,
                'employee_name': current_user.ename
                }
            return redirect('evaluate',emp_id = evaluatee_empid)
        else: # without selecting designations
            
            evaluator_empid = Employee.objects.filter(Q(enothi_id = request.user)).values('empid')[0]['empid']
            employees = Employee.objects.filter(~Q(empid = evaluator_empid), ~Q(empid__in=preevaluatees)).values('empid', 'ename','enothi_id')
            employee_list = list(employees)
            #return JsonResponse(employee_list, safe=False)
            return redirect('select-evaluatee')
           
    
    else:
        evaluator_empid = Employee.objects.filter(Q(enothi_id = request.user)).values('empid')[0]['empid']
        print("this is working now!!")
        employees = Employee.objects.filter(~Q(empid = evaluator_empid),  ~Q(empid__in=preevaluatees)).values('empid', 'ename','enothi_id')
        #employees = Employee.objects.all()
        context = {
            'employeeData': employees,
            'employee_name': current_user.ename
        }
        return render(request, 'employees/select_evaluatee.html', context)
    
#reza_update

@login_required(login_url='login')
def evaluate(request, emp_id):
    current_user=Employee.objects.get(enothi_id=request.user)
    if request.method == 'POST':
        print("Evaluate Post Method ",request.user)
        for key, value in request.POST.items():
            print('Key: %s' % (key) ) 
            # print(f'Key: {key}') in Python >= 3.7
            print('Value %s' % (value) )
            # print(f'Value: {value}') in Python >= 3.7
        #print(request.GET['employee'][1:5]) # need to check
        print("Data type check ",type(request.user.id))
        print("Data type check ",(request.user))
        evaluateeid = int(request.POST['evaluateeid'])
        
        if 'secDept' in request.POST:
            secDeptEv = int(request.POST['secDept'])
        else:
            secDeptEv = 5

        if 'committee' in request.POST:
            commEv = int(request.POST['committee'])
        else:
            commEv = 5


        evaluatorid =  Employee.objects.filter(enothi_id = int(request.user.username)).values()[0]['empid']
        behavEv = int(request.POST['behaviour'])
        comid = 1 # need to be modified
        new_eval = Evaluation(evaluateeid = evaluateeid, evaluatorid = evaluatorid , secDeptEv = secDeptEv, commEv = commEv, behavEv = behavEv, comid = comid)
        #print(fm.cleaned_data)
        new_eval.save()
        return redirect('home')
    evaluatee_empid = emp_id #employee id must be of 4 digits
    evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()[0]
  
    print("Evaluate function")
    print(evaluatee)
       
    context = {
                'evaluateeData': evaluatee,
                'division_name': evaluatee['edivision'],
                'designation_name': evaluatee['edesignation'],
                'evaluateeDesignation' : evaluatee['edesignation'],
                'employee_name': current_user.ename
                }
    print("test ",context['evaluateeData']['ename'])
    return render(request,'employees/evaluate.html',context)
        #return render(request,'employees/evaluate.html') 
        
        
  #reza_update      
@login_required(login_url='login')
def showReport(request):
    current_user = User.objects.get(username=request.user.username)
    employeename=current_user.first_name



    if request.method == 'POST':
        print("Report Post method called")
        print(request.POST)
        if request.POST['profile'] == "Back to Query":
            designations = Designation.objects.all()
            employees = Employee.objects.all()
            context = {
                'designationData': designations,
                'employeeData': employees,
                'employee_name':  employeename,

                
            }
            return render(request,'employees/query.html',context)
        
        elif request.POST['evalBased'] == "everyone" :
            #print("Everyone's Evaluation ",)
            #print(request.POST['employee'])
            #print(int(request.POST['employee'][1:5]))
            #print(int(request.POST['employee'][0:5]))
            #evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
            all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'])).values()
            results = []
            evaluatee_name = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['ename']
            evaluatee_designation = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['edesignation']
            evaluatee_division = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['edivision']
            #print(evaluatee_info)
            #print(type(all_evals))
            #print("Evaluatee Section : ",evaluatee_section)

            
            for eval in all_evals:
                results.append(eval)
                print("Evaluator ID : ",eval['evaluatorid'])
                print(type(eval['evaluatorid']))
                #evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
               
            final_report = []
            #print(results)
            print("check eval")
            for eval in results:
                #print(eval['evaluatorid'])
                #print(Employee.objects.filter(empid = eval['evaluatorid']).values())
                evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
                print("Evaluator Info : ",evaluator['ename'])
                print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
                print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
                print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
                print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

                final_report.append({
                                  'evaluatee': Employee.objects.filter(empid = eval['evaluateeid']).values()[0]['ename'],
                                  'evaluator': evaluator['ename'], 
                                  'division': evaluator['edivision'],
                                  'secDeptEval' : petro.remarks[int(eval['secDeptEv'])-1][1],
                                  'comEval' : petro.remarks[int(eval['commEv'])-1][1],
                                  'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
                                    }
                                  )
            print("final Report")
            print(final_report)


            divisional_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0
            }
            committee_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0
            }
            behav_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0
            }
            all_cat = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0
            }

            for eval in final_report:
                #print(eval['secDeptEval'])
                if eval['secDeptEval'] != 'No Observation':
                    if eval['secDeptEval'] in divisional_work:
                        divisional_work[eval['secDeptEval']] += 1
                    else:
                        divisional_work[eval['secDeptEval']] += 1

            labels1 = list(divisional_work.keys())
            data1 = list(divisional_work.values())

            labels_json1 = json.dumps(labels1)
            data_json1 = json.dumps(data1)


            for eval in final_report:
                #print(eval['comEval'])
                if eval['comEval'] != 'No Observation':
                    if eval['comEval'] in committee_work:
                        committee_work[eval['comEval']] += 1
                    else:
                        committee_work[eval['comEval']] += 1

            print("Committee Work!!!!")
            #divisional_work['Good'] = 6
            print(committee_work)

            labels2 = list(committee_work.keys())
            data2 = list(committee_work.values())

            labels_json2 = json.dumps(labels2)
            data_json2 = json.dumps(data2)


            for eval in final_report:
                #print(eval['secDeptEval'])
                if eval['behavEval'] != 'No Observation':
                    if eval['behavEval'] in  behav_work:
                        behav_work[eval['behavEval']] += 1
                    else:
                        behav_work[eval['behavEval']] += 1

            labels3 = list(behav_work.keys())
            data3 = list(behav_work.values())

            labels_json3 = json.dumps(labels3)
            data_json3 = json.dumps(data3)


            all_cat['Excellent'] += divisional_work['Excellent'] + committee_work['Excellent'] + behav_work['Excellent']
            all_cat['Very Good'] += divisional_work['Very Good'] + committee_work['Very Good'] + behav_work['Very Good']
            all_cat['Good'] += divisional_work['Good'] + committee_work['Good'] + behav_work['Good']
            all_cat['Average'] += divisional_work['Average'] + committee_work['Average'] + behav_work['Average']




            print("change for chairman sir")
            total_entities = all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average']
            print(all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'])
            total_marks = all_cat['Excellent']*40 + all_cat['Very Good']*30 + all_cat['Good']*20 + all_cat['Average']*10
            max_possible_marks = total_entities * 40
            percentage = ((round(((total_marks / max_possible_marks) * 100),2)))
            print(percentage)




            labels4 = list(all_cat.keys())
            data4 = list(all_cat.values())

            labels_json4 = json.dumps(labels4)
            data_json4 = json.dumps(data4)


            div_percent = []
            div_percent.append(round(((divisional_work['Excellent']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100),2))

            div_percent.append(round(((divisional_work['Very Good']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100),2))

            div_percent.append(round(((divisional_work['Good']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100), 2))

            div_percent.append(round(((divisional_work['Average']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] ))*100),2))

            print("Divisional Percentage")
            print(div_percent)


            com_percent = []
            com_percent.append(round(((committee_work['Excellent']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Very Good']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Good']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Average']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))


            behave_percent = []
            behave_percent.append(round(((behav_work['Excellent']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Very Good']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Good']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Average']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            allcat_percent = []
            allcat_percent.append(round(((all_cat['Excellent']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Very Good']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Good']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Average']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))           
    
            context = {
                'evaluatee_name' :  evaluatee_name,
                'evaluatee_designation' : evaluatee_designation,
                'evaluatee_division' : evaluatee_division,
                'report_data': final_report,
                'labels_json1': labels_json1,
                'data_json1': data_json1,
                'labels_json2': labels_json2,
                'data_json2': data_json2,
                'labels_json3': labels_json3,
                'data_json3': data_json3,
                'labels_json4': labels_json4,
                'data_json4': data_json4,
                'div_percent': div_percent,
                'com_percent': com_percent,
                'behave_percent': behave_percent,
                'allcat_percent':allcat_percent,
                'percentage':  percentage, 
                'employee_name':  employeename,

                }
            



            return render(request,'employees/report.html',context)
        elif request.POST['evalBased'] == "secDept":
            print("Section or Department's evaluation")
            #print(type(int(request.POST['employee'][1:5])))
            #evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
            all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'])).values()
            results = []
            evaluatee_name = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['ename']
            evaluatee_designation = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['edesignation']
            evaluatee_division = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['edivision']
            print(type(all_evals))
            #print("Evaluatee Section : ",evaluatee_section)

            
            for eval in all_evals:
                print("Evaluator ID : ",eval['evaluatorid'])
                print(type(eval['evaluatorid']))
                evaluator_division = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['edivision']
                if evaluatee_division == evaluator_division:
                    print("Matched!! This should be inserted")
                    results.append(eval)
                #print("Evaluator Section : " ,query_set[0]['esection'])
                
                #results.append(eval)
            final_report = []
            print(results)
            for eval in results:
                evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
                print("Evaluator Info : ",evaluator['ename'])
                print("Evaluator's division : ",evaluator['edivision'])
                print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
                print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
                print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
                print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

                final_report.append({
                                  'evaluatee': Employee.objects.filter(empid = eval['evaluateeid']).values()[0]['ename'],
                                  'evaluator': evaluator['ename'], 
                                  'division': evaluator['edivision'],
                                  'secDeptEval' : petro.remarks[int(eval['secDeptEv'])-1][1],
                                  'comEval' : petro.remarks[int(eval['commEv'])-1][1],
                                  'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
                                    }
                                  )
            print("final Report")
            print(final_report)



            divisional_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0, 'No Observation':0
            }
            committee_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0, 'No Observation':0
            }
            behav_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0
            }
            all_cat = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0, 'No Observation':0
            }

            for eval in final_report:
                #print(eval['secDeptEval'])
                if eval['secDeptEval'] in divisional_work:
                    divisional_work[eval['secDeptEval']] += 1
                else:
                    divisional_work[eval['secDeptEval']] += 1

            labels1 = list(divisional_work.keys())
            data1 = list(divisional_work.values())

            labels_json1 = json.dumps(labels1)
            data_json1 = json.dumps(data1)


            for eval in final_report:
                #print(eval['comEval'])
                if eval['comEval'] in committee_work:
                    committee_work[eval['comEval']] += 1
                else:
                    committee_work[eval['comEval']] += 1

            print("Committee Work!!!!")
            #divisional_work['Good'] = 6
            print(committee_work)

            labels2 = list(committee_work.keys())
            data2 = list(committee_work.values())

            labels_json2 = json.dumps(labels2)
            data_json2 = json.dumps(data2)


            for eval in final_report:
                #print(eval['secDeptEval'])
                if eval['behavEval'] in  behav_work:
                    behav_work[eval['behavEval']] += 1
                else:
                    behav_work[eval['behavEval']] += 1

            labels3 = list(behav_work.keys())
            data3 = list(behav_work.values())

            labels_json3 = json.dumps(labels3)
            data_json3 = json.dumps(data3)


            all_cat['Excellent'] += divisional_work['Excellent'] + committee_work['Excellent'] + behav_work['Excellent']
            all_cat['Very Good'] += divisional_work['Very Good'] + committee_work['Very Good'] + behav_work['Very Good']
            all_cat['Good'] += divisional_work['Good'] + committee_work['Good'] + behav_work['Good']
            all_cat['Average'] += divisional_work['Average'] + committee_work['Average'] + behav_work['Average']

            labels4 = list(all_cat.keys())
            data4 = list(all_cat.values())

            labels_json4 = json.dumps(labels4)
            data_json4 = json.dumps(data4)


            print("change for chairman sir")
            total_entities = all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average']
            print(all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'])
            total_marks = all_cat['Excellent']*40 + all_cat['Very Good']*30 + all_cat['Good']*20 + all_cat['Average']*10
            max_possible_marks = total_entities * 40
            percentage = ((round(((total_marks / max_possible_marks) * 100),2)))
            print(percentage)


            div_percent = []
            div_percent.append(round(((divisional_work['Excellent']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100),2))

            div_percent.append(round(((divisional_work['Very Good']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100),2))

            div_percent.append(round(((divisional_work['Good']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100), 2))

            div_percent.append(round(((divisional_work['Average']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] ))*100),2))

            print("Divisional Percentage")
            print(div_percent)


            com_percent = []
            com_percent.append(round(((committee_work['Excellent']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Very Good']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Good']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Average']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))


            behave_percent = []
            behave_percent.append(round(((behav_work['Excellent']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Very Good']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Good']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Average']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            allcat_percent = []
            allcat_percent.append(round(((all_cat['Excellent']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Very Good']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Good']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Average']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))      


            context = {
                'evaluatee_name' :  evaluatee_name,
                'evaluatee_designation' : evaluatee_designation,
                'evaluatee_division' : evaluatee_division,
                'report_data': final_report,
                'labels_json1': labels_json1,
                'data_json1': data_json1,
                'labels_json2': labels_json2,
                'data_json2': data_json2,
                'labels_json3': labels_json3,
                'data_json3': data_json3,
                'labels_json4': labels_json4,
                'data_json4': data_json4,
                'div_percent': div_percent,
                'com_percent': com_percent,
                'behave_percent': behave_percent,
                'allcat_percent':allcat_percent,
                'percentage':  percentage,
                'employee_name':  employeename,

                }
            
            return render(request,'employees/report.html',context)
        elif request.POST['evalBased'] == "other":
            print("Other  Divisions Evaluation")
            #print(type(int(request.POST['employee'][1:5])))
            #evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
            all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'])).values()
            results = []
            evaluatee_name = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['ename']
            evaluatee_designation = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['edesignation']
            evaluatee_division = Employee.objects.filter(empid = int(request.POST['employee'])).values()[0]['edivision']
            print(type(all_evals))
            #print("Evaluatee Section : ",evaluatee_section)

            
            for eval in all_evals:
                print("Evaluator ID : ",eval['evaluatorid'])
                print(type(eval['evaluatorid']))
                evaluator_division = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['edivision']
                if evaluatee_division != evaluator_division:
                    print("UnMatched!! This should be inserted")
                    results.append(eval)
                #print("Evaluator Section : " ,query_set[0]['esection'])
                
                #results.append(eval)
            final_report = []
            print(results)
            for eval in results:
                evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
                print("Evaluator Info : ",evaluator['ename'])
                print("Evaluator's division : ",evaluator['edivision'])
                print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
                print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
                print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
                print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

                final_report.append({
                                  'evaluatee': Employee.objects.filter(empid = eval['evaluateeid']).values()[0]['ename'],
                                  'evaluator': evaluator['ename'], 
                                  'division': evaluator['edivision'],
                                  'secDeptEval' : petro.remarks[int(eval['secDeptEv'])-1][1],
                                  'comEval' : petro.remarks[int(eval['commEv'])-1][1],
                                  'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
                                    }
                                  )
            print("final Report")
            print(final_report)



            divisional_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0, 'No Observation':0
            }
            committee_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0, 'No Observation':0
            }
            behav_work = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0
            }
            all_cat = {
                    'Excellent':0, 'Very Good':0, 'Good':0, 'Average':0, 'No Observation':0
            }

            for eval in final_report:
                #print(eval['secDeptEval'])
                if eval['secDeptEval'] in divisional_work:
                    divisional_work[eval['secDeptEval']] += 1
                else:
                    divisional_work[eval['secDeptEval']] += 1

            labels1 = list(divisional_work.keys())
            data1 = list(divisional_work.values())

            labels_json1 = json.dumps(labels1)
            data_json1 = json.dumps(data1)


            for eval in final_report:
                #print(eval['comEval'])
                if eval['comEval'] in committee_work:
                    committee_work[eval['comEval']] += 1
                else:
                    committee_work[eval['comEval']] += 1

            print("Committee Work!!!!")
            #divisional_work['Good'] = 6
            print(committee_work)

            labels2 = list(committee_work.keys())
            data2 = list(committee_work.values())

            labels_json2 = json.dumps(labels2)
            data_json2 = json.dumps(data2)


            for eval in final_report:
                #print(eval['secDeptEval'])
                if eval['behavEval'] in  behav_work:
                    behav_work[eval['behavEval']] += 1
                else:
                    behav_work[eval['behavEval']] += 1

            labels3 = list(behav_work.keys())
            data3 = list(behav_work.values())

            labels_json3 = json.dumps(labels3)
            data_json3 = json.dumps(data3)


            all_cat['Excellent'] += divisional_work['Excellent'] + committee_work['Excellent'] + behav_work['Excellent']
            all_cat['Very Good'] += divisional_work['Very Good'] + committee_work['Very Good'] + behav_work['Very Good']
            all_cat['Good'] += divisional_work['Good'] + committee_work['Good'] + behav_work['Good']
            all_cat['Average'] += divisional_work['Average'] + committee_work['Average'] + behav_work['Average']

            labels4 = list(all_cat.keys())
            data4 = list(all_cat.values())

            labels_json4 = json.dumps(labels4)
            data_json4 = json.dumps(data4)

            print("change for chairman sir")
            total_entities = all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average']
            print(all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'])
            total_marks = all_cat['Excellent']*40 + all_cat['Very Good']*30 + all_cat['Good']*20 + all_cat['Average']*10
            max_possible_marks = total_entities * 40
            percentage = ((round(((total_marks / max_possible_marks) * 100),2)))
            print(percentage)


            div_percent = []
            div_percent.append(round(((divisional_work['Excellent']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100),2))

            div_percent.append(round(((divisional_work['Very Good']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100),2))

            div_percent.append(round(((divisional_work['Good']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] )) * 100), 2))

            div_percent.append(round(((divisional_work['Average']/ (divisional_work['Excellent'] + divisional_work['Very Good'] + divisional_work['Good'] + divisional_work['Average'] ))*100),2))

            print("Divisional Percentage")
            print(div_percent)


            com_percent = []
            com_percent.append(round(((committee_work['Excellent']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Very Good']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Good']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))

            com_percent.append(round(((committee_work['Average']/ (committee_work['Excellent'] + committee_work['Very Good'] + committee_work['Good'] + committee_work['Average'] )) * 100),2))


            behave_percent = []
            behave_percent.append(round(((behav_work['Excellent']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Very Good']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Good']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            behave_percent.append(round(((behav_work['Average']/ (behav_work['Excellent'] + behav_work['Very Good'] + behav_work['Good'] + behav_work['Average'] )) * 100),2))

            allcat_percent = []
            allcat_percent.append(round(((all_cat['Excellent']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Very Good']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Good']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))

            allcat_percent.append(round(((all_cat['Average']/ (all_cat['Excellent'] + all_cat['Very Good'] + all_cat['Good'] + all_cat['Average'] )) * 100),2))      

            context = {
                'evaluatee_name' :  evaluatee_name,
                'evaluatee_designation' : evaluatee_designation,
                'evaluatee_division' : evaluatee_division,
                'report_data': final_report,
                'labels_json1': labels_json1,
                'data_json1': data_json1,
                'labels_json2': labels_json2,
                'data_json2': data_json2,
                'labels_json3': labels_json3,
                'data_json3': data_json3,
                'labels_json4': labels_json4,
                'data_json4': data_json4,
                'div_percent': div_percent,
                'com_percent': com_percent,
                'behave_percent': behave_percent,
                'allcat_percent':allcat_percent,
                'percentage':  percentage,
                'employee_name':  employeename

                }
            
            return render(request,'employees/report.html',context)
        
        
        
        
        context = {
                'report_data': final_report,
                'employee_name':  employeename,

                }
        return render(request,'employees/report.html',context)
    
    designations = Designation.objects.all()
    employees = Employee.objects.all()
    context = {
                'designationData': designations,
                'employeeData': employees,
                'employee_name':  employeename,

            }
    return render(request,'employees/query.html',context)
@login_required(login_url='login')
def giveAward(request):
    if request.method == 'POST':

        print("checkkk!!!!!!!")
        print(request.POST['employee'])
        print(request.POST['permission'])
        return redirect('home')
        #return redirect('writeAwardDescription',emp_id = int(request.POST['employee']))
    employee = Employee.objects.all()
    #   evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
    #          'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
    #   all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'][1:5])).values()
    #        evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()
    #-   if request.method == 'POST':
     #  if form.is_valid():
      #      award = form.save(commit=False)
       #     award.user = request.user
        #    award.save()
         #   user_profile.counter -= 1
          #  user_profile.save()
           # return redirect('award_success')  # Redirect to a success page
    #else:
     #   form = AwardForm()
    #return render(request, 'give_award.html', {'form': form})
  #   evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
     #       all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'][1:5])).values()
     #       results = []
     #       print(type(all_evals))
      #      print("Evaluatee Section : ",evaluatee_section)

            
     #       for eval in all_evals:
        #        print("Evaluator ID : ",eval['evaluatorid'])
        #        print(type(eval['evaluatorid']))
        #        evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
        #        if evaluatee_section == evaluator_section:
        #            print("Matched!! This should be inserted")
        #            results.append(eval)
                #print("Evaluator Section : " ,query_set[0]['esection'])
                
                #results.append(eval)
       #     final_report = []
      #      print(results)
       #     for eval in results:
         #       evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
         #       print("Evaluator Info : ",evaluator['ename'])
          #      print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
          #      print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
          #      print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
          #      print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

            #    final_report.append({
                
    advisor = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']

    
    return render (request, 'employees/award.html', {'employeeData': employee} )



@login_required(login_url='login')
def getadvisor(request,emp_id):

    employee = Employee.objects.filter(id=employee_id).first()
    if employee:
        advisor_name = employee.advisor.name
        data = {
            'advisor_name': advisor_name
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    

@login_required(login_url='login')
def writeAwardDescription(request,emp_id):
    if request.method == 'POST':
        #print(request.POST['giveAward'])
        #print(request.POST['employee'])
        print("if from writeAwardDescription")
        
    print("get from write award")
    employee = Employee.objects.all()
    return render (request, 'employees/write_award_description.html', {'employeeData': employee} )

##############################Main award Function#############################################
@login_required(login_url='login')
def AwardSystem(request):
      #on post method. if counter>0 it will updatate award table
      #when advisor will login on clicking the notification bar it will redirect to the notfications.html where he will see the awardd table matchh with his enothi id.
      #on approving the report only then the counter value will be decreased


        
      if request.method == 'POST':
        current_user= Employee.objects.get(enothi_id = request.user) 
        counter=current_user.counter
        context={
            'counter':counter,
            'employee_name':current_user.ename
        }  
      
        #if fmis valied?
       

        
          # Decrement the counter by 1
        if current_user.counter > 0:

         current_user.counter=current_user.counter-1
         current_user.save()
             
         print("checkkk!!!!!!!")
         award_evaluetee=Employee.objects.get(enothi_id =request.POST['employee'])    #here
         current_user= Employee.objects.get(enothi_id = request.user)
         if award_evaluetee == current_user:
            current_user.counter=current_user.counter+1
            current_user.save()


            messages.error(request, "You cannot give reward to yourself.")
            return redirect('award')
         #current_user.counter=10 
         award_evaluatorname =current_user.ename,
         award_evaluateename = award_evaluetee.ename,
         purposeid=request.POST['purpose'],
         description= request.POST['description'],

         #advisor_deginations=petro.designations[advisor_object.edesignation-1][1]
         #print("dgdfgdg==============="+advisor_deginations)
         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
         print (type(current_user))
         print(current_user)





         #save data to award table:
         award = Award.objects.create(
         award_evaluatorid=current_user.enothi_id,
         award_evaluateeid=award_evaluetee.enothi_id,
         purposeid=request.POST.get('purpose'),
         description=request.POST.get('description'),
    )
         award.save()
            # Create notification for advisor
         notification_message = f'{award_evaluatorname} is trying to give an award to { award_evaluateename}.'
         no=Notification.objects.create(
                    recipient=award_evaluetee,  # Assuming advisor_object has a 'user' field
                    sender=current_user,  # Assuming current_user has a 'user' field
                    message=notification_message
                )
         

            # Provide feedback to the user
         messages.success(request, 'Reward has been Submitted.')
    
        

        return redirect('award')
      ###############get###################
      
      else:
        emp_id=request.user
        current_user= Employee.objects.get(enothi_id = request.user)
        if(current_user.counter==0):
            messages.error(request, 'You have used all your rewards.')
              
         # advisor=Employee.objects.get(edivision=request.user )
         # print(advisor.ename+ "===========advisor")
        print(current_user.ename+ "===========ename")
         # print(current_user.empid)
          #print(current_user.enothi_id)
        current_division = current_user.edivision
        advisor = Employee.objects.filter(edivision=current_division, edesignation="General Manager").first()  
        if not advisor:
            advisor = Employee.objects.filter(edivision=current_division, edesignation="Deputy General Manager").first()
         


        # Filter employees who are in the same department and have the designation "General Manager"
        print("cute!!!!")

        supervisor=advisor.ename
        print(supervisor+ "===========supervisor")


        division= current_user.edivision
         # print(division+ "===========edivision")
        designations = Designation.objects.all()
        employees = Employee.objects.all()
        advisor_designations=advisor.edesignation
        advisor_divisions=advisor.edivision
        counter=current_user.counter
        print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        print(advisor_divisions)
    
        context={
             'evaluator_division': division,
             'advisor':supervisor,
             'designationData': designations,
             'employeeData': employees,
             'ade':advisor_designations,
             'adi':advisor_divisions,
             'counter': counter,
             'employee_name':current_user.ename

         }

        return render(request,'employees/award.html',context)   

        # current_user.counter -= 1    
         #current_user.save()
         #new_award=Award (                
         #award_evaluatorname =current_user.ename,
         #award_evaluateename = award_evaluetee.ename,
         #purposeid=request.POST['purpose'],
         #description= request.POST['description'],
         #advisorname= request.POST['seek'] 

        #)
         #new_award.save()
         #messages.success(request, "Award given successfully.")
     
        #else:
         #   messages.error(request, "You have 0 award counter.")
            #return redirect('home')

        #return redirect('award')    
 

 # if request.method == 'POST':
    #    print ("o yes")
      #  print(request.POST['employee'][1:5]) # need to check
     #   evaluatee_empid = int(request.POST['employee'][1:5]) #employee id must be of 4 digits
     #   evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()
      #  #print("Select Evaluatee")
        #print(Designation.objects.filter(desigid = evaluatee[0]['edesignation']).values()[0]['designame'])
        #evaluatee_designation = Designation.objects.filter(desigid = evaluatee[0]['edesignation']).values()[0]['designame']
      #  print(evaluatee[0]['edesignation'])
      #  context = {
           #    'evaluateeeData': evaluatee,
                
           #     }
    #    return redirect('evaluate',emp_id = evaluatee_empid)



#if fm.is_valid():
          #  mydata = Employee.objects.filter(enothi_id = request.user)#this will ensure that form is saved to logged in user even if we repeatedly change data
          #  if mydata.exists():
    
              #  myProfileData = Employee.objects.get(enothi_id = request.user)
              #  #print(" My Objects ",myProfileData[0])
             #   myProfileData.ename = request.POST['name']
              #  myProfileData.eemail = request.POST['email']
              #  myProfileData.empid = request.POST['empid']
             #   myProfileData.edesignation = request.POST['designation']
            #    myProfileData.esection = request.POST['section']
             #   myProfileData.edept = request.POST['department']
             #   myProfileData.edivision = request.POST['division']
             #   myProfileData.edirectorate = request.POST['directorate']
           #     myProfileData.save()
           #     return redirect('home')#
def notifications_view(request):
    if hasattr(request.user, 'ename'):
        employee = request.user.ename
        notifications = Notification.objects.filter(recipient=employee, is_read=False)
        print("o yes")
        print(notifications)
        unread_notifications_count = notifications.count()
    else:
        print("o yes else ")
        notifications = []
        unread_notifications_count = 0

    context = {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'employees/notifications.html', context)

def approve_award(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    # Logic to approve the award
    award = Award.objects.create(
        award_evaluatorname=notification.sender.username,
        award_evaluateename=notification.message.split(' to ')[1].split('.')[0],
        purposeid=request.POST.get('purpose'),
        description=request.POST.get('description'),
        advisorname=notification.recipient.username,
    )

    # Decrease the counter of the evaluator
    evaluator = Employee.objects.get(ename=notification.sender.username)
    evaluator.counter -= 1
    evaluator.save()

    # Notify the evaluator
    notification_message = f'Your award to {award.award_evaluateename} has been approved.'
    Notification.objects.create(recipient=notification.sender, sender=request.user, message=notification_message)

    notification.is_read = True
    notification.save()

    return redirect('notifications_view')

@login_required(login_url='login')
def AwardReport(request):
 
 
    if request.method == 'GET':
        print(request.user)
        try:
            current_user = Employee.objects.get(enothi_id=request.user)
        except Employee.DoesNotExist:
            # Handle case where current user doesn't exist (optional)
            current_user = None
        
        if current_user:
            award_advisor = Award.objects.filter(award_evaluatorid=current_user.enothi_id)
            
            if award_advisor.exists():
                current_user.counter=current_user.counter-1
                finalawardreport = []
                
                for eval in award_advisor:
                    evaluator_employee = Employee.objects.get(enothi_id=eval.award_evaluatorid)
                    evaluatee_employee = Employee.objects.get(enothi_id=eval.award_evaluateeid)

                    finalawardreport.append({
                        'award_id': eval.awardid,
                        'evaluator_name': evaluator_employee.ename,
                        'evaluatee_name': evaluatee_employee.ename,
                        'purpose': eval.purposeid,
                        'description': eval.description,
                        'Counter': evaluator_employee.counter,
                        'evaluator_id': evaluator_employee.enothi_id,
                        'date':eval.created_date,
                        
                    })
                
                context = {
                    'report_data': finalawardreport,
                    'employee_name':current_user.ename
                }
                
                return render(request, 'employees/awardreport.html', context)
            else:
                # Redirect to homepage if no awards exist for the advisor
                return redirect('home')  # Assuming 'home' is the name of your homepage URL
        else:
            # Handle case where current user is None (optional)
            return redirect('home')  # Redirect to homepage if user doesn't exist or isn't logged in
    



@login_required(login_url='login')
def award_distribution(request, enothi_id):
    print("enothiid")
    print(enothi_id)
    employee = Employee.objects.get(enothi_id=enothi_id)
    print(employee.ename)
    own_department = Award.objects.filter(
        award_evaluateeid=employee.enothi_id,
        #employee__edept=employee.edept
    ).count()
   # other_department = Award.objects.filter(
       # award_evaluateeid=employee.enothi_id
   # ).exclude(employee__edept=employee.edept).count()
    
    data = {
        'own_department': own_department,
       # 'other_department': other_department
    }
    return JsonResponse(data)

def advisor_status(request):
    pending = Award.objects.filter(Status=0).count()
    approved = Award.objects.filter(Status=2).count()
    rejected = Award.objects.filter(Status=1).count()
    
    data = {
        'pending': pending,
        'approved': approved,
        'rejected': rejected
    }
    return JsonResponse(data)

    
@login_required(login_url='login')
def award_data(request):
    awards = Award.objects.all().values('advisorid', 'award_evaluatorid', 'award_evaluateeid', 'Status','remark')
    awards_data = []
    for award in awards:
        print("wtffffff")
        print(award['advisorid'])
  
        awards_data.append({
            'id': Employee.objects.get(enothi_id=award['advisorid']).ename,
            'evaluator': award['award_evaluatorid'],
            'evaluator_name':Employee.objects.get(enothi_id=award['award_evaluatorid']).ename,
            'evaluatee': award['award_evaluateeid'],
            'evaluatee_name':Employee.objects.get(enothi_id=award['award_evaluateeid']).ename,
            'status': petro.status[award['Status']][1],
            'remark': award['remark']
        })
    return JsonResponse({'awards': awards_data})

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def search_employee(request):
    query = request.GET.get('q', '')
    employees_data = []

    if query:
        try:
            employees = Employee.objects.filter(Q(ename__icontains=query) | Q(enothi_id__icontains=query))
            employees_data = [{'enothi_id': emp.enothi_id, 'name': emp.ename, 'division':emp.edivision, 'designation':emp.edesignation} for emp in employees]
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error searching employees: {e}")

    return JsonResponse({'employees': employees_data})

@login_required(login_url='login')

def award_pie(request,enothi_id):
    try:
        print(enothi_id)
        print("the great wall")
        # Fetch the employee by enothi_id
        evaluatee = Employee.objects.get(enothi_id=enothi_id)
        ename=evaluatee.ename
        enothi=evaluatee.enothi_id
        #evaluator=Award.objects.ge
        
        # Get awards where the evaluator is in the same department as the evaluatee
        own_department_awards = Award.objects.filter(
            award_evaluateeid=evaluatee.enothi_id,
            award_evaluatorid__in=Employee.objects.filter(edivision=evaluatee.edivision).values_list('enothi_id', flat=True)
            
        ).count()
        print(own_department_awards)
        print("BANKOK")
        
        # Get awards where the evaluator is in a different department than the evaluatee
        other_department_awards = Award.objects.filter(
             award_evaluateeid=evaluatee.enothi_id
             ).exclude(
             award_evaluatorid__in=Employee.objects.filter(edivision=evaluatee.edivision).values_list('enothi_id', flat=True)
              ).count()
        print(other_department_awards)
        print("BALI")
        
        # Return the results as a JSON response
        return JsonResponse({
            'own_department': own_department_awards,
            'other_department': other_department_awards,
            'name': ename,
            'enothi': enothi, 
        })
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
@login_required(login_url='login')   
def get_employee_awards(request, enothi_id):

    awards = Award.objects.filter(award_evaluateeid=enothi_id)
    award_data = []
  

    for award in awards:
        try:
            evaluator = Employee.objects.get(enothi_id=award.award_evaluatorid)
            evaluatee = Employee.objects.get(enothi_id=award.award_evaluateeid)
            
            award_data.append({
                'award_id': award.awardid,
                'evaluator_name': evaluator.ename,
                'evaluator_id': evaluator.enothi_id,
                'evaluatee_name': evaluatee.ename,
                'evaluatee_id': evaluatee.enothi_id,
                'purposeid': award.purposeid,
                'description': award.description,
                'date':award.created_date,

            })
        except Employee.DoesNotExist:
            award_data.append({
                'award_id': award.awardid,
                'evaluator_name': "Unknown Evaluator",
                'evaluator_id': award.award_evaluatorid,
                'evaluatee_name': "Unknown Evaluatee",
                'evaluatee_id': award.award_evaluateeid,
                'purposeid': award.purposeid,
                'description': award.description,
                'date':award.created_date,

            })
           

    return JsonResponse({'awards': award_data})




def search_advisor(request):
    print("srilanka")
    if request.method == 'GET':
       award=Award.objects.all()
       context={
        'advisorData':award
         }
       return render (request,'employees/dashboard.html',context)
   

def is_superuser(user):
    return user.is_superuser

# Apply the user_passes_test decorator to your view
@login_required(login_url='login')
def dashboard(request):
    top_employees = Award.objects.values('award_evaluateeid') \
    .annotate(total_awards=Count('award_evaluateeid')) \
    .order_by('-total_awards')[:5]
    # Assuming you have an Employee model to fetch employee details
    current_user = User.objects.get(username=request.user.username)
    employeename=current_user.first_name
    top_employees_details = []
    for emp in top_employees:
        employee = Employee.objects.get(enothi_id=emp['award_evaluateeid'])
        top_employees_details.append({
            'employee_name': employee.ename,
            'employee_empid': employee.empid,
            'total_awards': emp['total_awards']
        })
        

    context = {
        'top_employees': top_employees_details,
        'employee_name':  employeename
    }
    for employee in top_employees_details:
       
          print(employee['total_awards'])

    return render(request, 'employees/dashboard.html',context)
@login_required(login_url='login')
def top_employees_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    awards = Award.objects.filter(date__range=[start_date, end_date]) \
                .values('award_evaluateeid', 'employee_name', 'employee_empid') \
                .annotate(total_awards=Count('awardid')) \
                .order_by('-total_awards')[:5]

    data = {'top_employees': list(awards)}
    return JsonResponse(data)

    

