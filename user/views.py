from multiprocessing import dummy
from unicodedata import name
from urllib import request
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import *
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .token import account_activation_token  
from django.contrib.auth.models import User  
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from requisition.settings import EMAIL_HOST_USER
from django.forms.models import model_to_dict
from copy import copy



@unauthenticated_user

def registerpage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # user = form.save()
            user = form.save(commit=False)
            user.is_active = False  
            user.save()  

            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('user/account_activation.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            # email = EmailMessage(  
            #             mail_subject, message, to=[to_email]  
            # )  
            # email.send() 


            try:
                send_mail(mail_subject, message,  EMAIL_HOST_USER, [to_email])
                print('success')
            except BadHeaderError:
                return HttpResponse('Invalid header found.') 
            dummy = -1
            # return HttpResponse('Please confirm your email address to complete the registration')  
            return render(request, 'user/confirmation.html', { 'dummy' : dummy } )
            
            
        # else:  
        #     form = CreateUserForm()  

    context =  {'form': form}
    return render(request, 'user/register.html', context)

def activate(request, uidb64, token):  
    # User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        
        dummy = 1

        # messages.success(request, 'Account Has Been Successfully Created For ' + username)
            # return redirect('loginpage')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.', )  
        return render(request, 'user/confirmation.html', { 'dummy' : dummy })
    else:  
        dummy = 0
        # return HttpResponse('Activation link is invalid!')  
        return render(request, 'user/confirmation.html', { 'dummy' : dummy })


@unauthenticated_user

def loginpage(request):
    if request.method == 'POST':
        username= request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password = password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Account Does Not Exist')

    context =  {}
    return render(request, 'user/login.html', context)

def logoutuser(request):
    logout(request)
    return redirect('loginpage')


# USER PAGE=============================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def userpage(request):
    requisitions = request.user.newuser.requisition_set.all().order_by('-id')
    employee = request.user.newuser


    print(employee)
    print(requisitions)
     
    context = {
        'requisitions':requisitions,
        'employee':employee
    }
    return render(request, "user/userpage.html", context)

@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def userpage0(request):
    requisitions = request.user.newuser.requisition_set.all().order_by('-id')
    u_r = request.user.newuser.requisition_set.all()
    employee = request.user.newuser

    all_pending_to_user = u_r.filter(status = 'Pending').exclude(submitted_by__name= employee.name)
    all_processing_to_user = u_r.filter(status = 'Processing').exclude(submitted_by__name= employee.name)
    all_delivered_to_user = u_r.filter(status = 'Delivered').exclude(submitted_by__name= employee.name)

    all_pending_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name)
    all_processing_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name)
    all_delivered_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name)


    total_pending_to_user = u_r.filter(status = 'Pending').exclude(submitted_by__name= employee.name).count()
    total_processing_to_user = u_r.filter(status = 'Processing').exclude(submitted_by__name= employee.name).count()
    total_delivered_to_user = u_r.filter(status = 'Delivered').exclude(submitted_by__name= employee.name).count()

    total_pending_by_user = u_r.filter(status = 'Pending', submitted_by__name= employee.name).count()
    total_processing_by_user = u_r.filter(status = 'Processing', submitted_by__name= employee.name).count()
    total_delivered_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name).count()

    


    
     
    context = {
        'requisitions':requisitions,
        'employee':employee,

        'all_pending_to_user':all_pending_to_user,
        'all_processing_to_user': all_processing_to_user,
        'all_delivered_to_user':all_delivered_to_user,

        'all_pending_by_user':all_pending_by_user,
        'all_processing_by_user':all_processing_by_user, 
        'all_delivered_by_user':all_delivered_by_user,


        'total_pending_to_user' : total_pending_to_user,
        'total_processing_to_user': total_processing_to_user,
        'total_delivered_to_user': total_delivered_to_user,
        'total_pending_by_user' : total_pending_by_user ,
        'total_processing_by_user':total_processing_by_user,
        'total_delivered_by_user':total_delivered_by_user,

    }
    return render(request, "user/dashboard.html", context)


def userpage1(request):
    requisitions = request.user.newuser.requisition_set.all().order_by('-id')
    u_r = request.user.newuser.requisition_set.all()
    employee = request.user.newuser

    all_pending_to_user = u_r.filter(status = 'Pending').exclude(submitted_by__name= employee.name)
    all_processing_to_user = u_r.filter(status = 'Processing').exclude(submitted_by__name= employee.name)
    all_delivered_to_user = u_r.filter(status = 'Delivered').exclude(submitted_by__name= employee.name)

    all_pending_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name)
    all_processing_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name)
    all_delivered_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name)


    total_pending_to_user = u_r.filter(status = 'Pending').exclude(submitted_by__name= employee.name).count()
    total_processing_to_user = u_r.filter(status = 'Processing').exclude(submitted_by__name= employee.name).count()
    total_delivered_to_user = u_r.filter(status = 'Delivered').exclude(submitted_by__name= employee.name).count()

    total_pending_by_user = u_r.filter(status = 'Pending', submitted_by__name= employee.name).count()
    total_processing_by_user = u_r.filter(status = 'Processing', submitted_by__name= employee.name).count()
    total_delivered_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name).count()

    


    
     
    context = {
        'requisitions':requisitions,
        'employee':employee,

        'all_pending_to_user':all_pending_to_user,
        'all_processing_to_user': all_processing_to_user,
        'all_delivered_to_user':all_delivered_to_user,

        'all_pending_by_user':all_pending_by_user,
        'all_processing_by_user':all_processing_by_user, 
        'all_delivered_by_user':all_delivered_by_user,


        'total_pending_to_user' : total_pending_to_user,
        'total_processing_to_user': total_processing_to_user,
        'total_delivered_to_user': total_delivered_to_user,
        'total_pending_by_user' : total_pending_by_user ,
        'total_processing_by_user':total_processing_by_user,
        'total_delivered_by_user':total_delivered_by_user,

    }
    return render(request, "user/dashboard_detail.html", context)




# @login_required(login_url='loginpage')
# @admin_only
# def home(request):
#     employees = NewUser.objects.all()
#     requisitions = Requisition.objects.all()
    

#     total_requisitions= requisitions.count()
#     total_pending = requisitions.filter(status='Pending').count()
#     total_delivered = requisitions.filter(status='Delivered').count()

    
#     context = {
#         'employees': employees,
#         'requisitions': requisitions,
#         'total_requisitions': total_requisitions,
#         'total_pending': total_pending,
#         'total_delivered': total_delivered,
#     }
#     return render(request, 'user/home.html', context ) 




# def employee(request, pk):
#     employee = NewUser.objects.get(id = pk)
#     requisitions = employee.requisition_set.all()
#     context = {
#         'employee' : employee,
#         'requisitions' : requisitions,
#     }

#     return render(request, 'user/employee.html', context) 




# DETAIL REQUISITION PAGE =======================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def requisitions(request, pk):
    requisition = Requisition.objects.get(id=pk)
    employee = request.user
    # submitted_by = requisition.submitted_by
    # submitted_to = requisition.send_to.exclude(user = submitted_by)

    context = {
        'requisition':requisition,
        'employee' : employee,
        # 'submitted_to': submitted_to,

    }
    return render(request, 'user/detail_requisition.html', context) 



# CREATE REQUISITION PAGE =======================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def create_requisition(request, pk):
    employee = NewUser.objects.get(id=pk)
    form = RequisitionForm()
    if request.method == 'POST':
        form = RequisitionForm(request.POST, request.FILES)
        # form.employee = [request.user,]
        
        if form.is_valid():
            
            r= form.save()
            r.submitted_by = employee
            r.send_to.add(employee)
            # # created by stamp
            r.status= 'Pending'
            r.save()
            
            
            # email section 
            req_title = form.cleaned_data.get('title')
            mail_subject = 'A new requisition has been requested'  
            message = 'A new requisition has been requested\n' + 'under the name of ---' + req_title +'---'+ '\ncreated by  ' + employee.name

            r3 = r.send_to.values_list('email', flat=True)

            tomail = list(r3)
            tomail.remove(employee.email)
            

            try:
                send_mail(mail_subject, message,  EMAIL_HOST_USER, tomail)
                print('success')
            except BadHeaderError:
                return HttpResponse('Invalid header found.') 
            # end of email section


            return redirect('/')

    return render(request, 'user/new_requisition.html', {'form':form })



# UPDATE REQUISITION==========================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def update_requisition(request, pk):
    requisition= Requisition.objects.get(id=pk)
    print(requisition.send_to.all())
    print(request.user)
    print('test')
    form = UpdateForm(instance=requisition)
    if request.method == 'POST':
        form = UpdateForm(request.POST or None, instance=requisition) 
        form.has_changed()
        

        if form.is_valid():
            form.save()
            # form.send_to.create(requisition)
            # r= form.save(commit=False)
            # r.send_to = requisition.send_to.all()
            # print(r)
            # r.save()
            # form.save_m2m()


            # email section->
            
            req_title = requisition.title
            employee = request.user.newuser
           
            mail_subject = 'A requisition has been Updated'  
            print(request.user.first_name)
            message = 'A new requisition has been updated\n' + 'under the name of ---' + req_title +'---'+ '\n by  ' + employee.name

            
            r3 = requisition.send_to.values_list('email', flat=True)

            tomail = list(r3)
            tomail.remove(request.user.email)
            

            try:
                send_mail(mail_subject, message,  EMAIL_HOST_USER, tomail)
                print('success')
            except BadHeaderError:
                return HttpResponse('Invalid header found.') 
            
            return redirect('requisitions', pk)
        else:
            print('not valid')

    return render(request, 'user/update_requisition.html', {'form':form, 'requisition':requisition })


@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def delete_requisition(request, pk):
    requisition = Requisition.objects.get(id=pk)
    if request.method == 'POST':
        
        from_email = request.user.email
        from_name = request.user.username
        
        req_title = requisition.title
        mail_subject = 'A requisition has been deleted'  
        message = 'A new requisition has been DELETED\n' + 'under the name of ---' + req_title +'---'+ '\n by  ' + from_name
        
        r3 = requisition.send_to.values_list('user', flat=True)
        x = User.objects.filter(id__in=list(r3)).values_list('email', flat=True)
        tomail = list(x)

        try:
            send_mail(mail_subject, message,  EMAIL_HOST_USER, tomail)
            print('success')
        except BadHeaderError:
            return HttpResponse('Invalid header found.') 

        requisition.delete()

        return redirect('/')
    

    return render(request, 'user/delete.html', { 'requisition':requisition })


