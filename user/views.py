from multiprocessing import context, dummy
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
from requisition.settings.base import EMAIL_HOST_USER
from django.forms.models import model_to_dict
from copy import copy
from django.template import RequestContext



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


# PROFILE PAGE======================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def profile(request):
    profil = request.user.newuser
    user_profil = request.user
   

    context = {
        'user_profil': user_profil,
        'profil':profil,
    }
    return render(request, "user/profile.html", context)




# PROFILE UPDATE PAGE======================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def update_profile(request):
    profil = request.user.newuser
    user_profil = request.user
    form = UpdateProfileForm(instance= profil)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            print('invalid form')

    context = {
        'user_profil': user_profil,
        'profil':profil,
        'form': form,
    }
    return render(request, "user/update_profile.html", context)



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

    all_pending_to_user = u_r.filter(status = 'Pending').exclude(submitted_by__name= employee.name).order_by('-id')
    all_processing_to_user = u_r.filter(status = 'Processing').exclude(submitted_by__name= employee.name).order_by('-id')
    all_delivered_to_user = u_r.filter(status = 'Delivered').exclude(submitted_by__name= employee.name).order_by('-id')

    all_pending_by_user = u_r.filter(status = 'Pending', submitted_by__name= employee.name).order_by('-id')
    all_processing_by_user = u_r.filter(status = 'Processing', submitted_by__name= employee.name).order_by('-id')
    all_delivered_by_user = u_r.filter(status = 'Delivered', submitted_by__name= employee.name).order_by('-id')


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
    files = requisition.files.all()
    notes = requisition.notes.all()
    pending_update = False
    
    # submitted_by = requisition.submitted_by
    # submitted_to = requisition.send_to.exclude(user = submitted_by)
    if requisition.status == 'Pending':
        if requisition.submitted_by == employee.newuser:
            pending_update = True
            update = False
        else:
            update = True
    elif requisition.status == 'Processing':
        update = True
    elif requisition.status == 'Delivered':
        update = False
    else:
        update = True


    context = {
        'requisition':requisition,
        'employee' : employee,
        'files':files,
        'notes':notes,
        'update':update,
        'pending_update' : pending_update,
        
        # 'submitted_to': submitted_to,

    }
    return render(request, 'user/detail_requisition.html', context) 



# CREATE REQUISITION PAGE =======================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def create_requisition(request, pk):
    employee = NewUser.objects.get(id=pk)
    form = RequisitionForm()
    formfile = MultiFileForm()
    formnote = MultiNoteForm()


    if request.method == 'POST':
        if 'req_hidden' in request.POST:
            pass
        form = RequisitionForm(request.POST)
        formfile = MultiFileForm(request.POST or None, request.FILES or None)
        if 'note_hidden' in request.POST:
            pass
        if 'file_hidden' in request.POST:
            pass
        formnote = MultiNoteForm(request.POST)

        files = request.FILES.getlist('file')

 
        if form.is_valid() and formfile.is_valid() and formnote.is_valid():
            
            r= form.save()
            r.submitted_by = employee
            r.send_to.add(employee)
            # # created by stamp
            r.status= 'Pending'
            r.save()
            n = formnote.save(commit=False)

            try:
                MultiNote.objects.create(
                    req = r,
                    note = n,
                    written = employee,
                )
            except:
                print("invalid object couldnt be created")

            for f in files:
                MultiFile.objects.create(
                    req = r,
                    file = f,
                )
            # f = formfile.save(commit=False)
            # f.save()


            # r.submitted_by = employee
            # r.send_to.add(employee)
            # # # created by stamp
            # r.status= 'Pending'
            # r.save()
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

            return redirect('requisitions', r.id)

            # return redirect('/')
    context = {
        'form':form,
        'formfile':formfile,
        'formnote':formnote,
    }        

    return render(request, 'user/new_requisition.html', context)



# UPDATE REQUISITION==========================
@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def update_requisition(request, pk):
    requisition= Requisition.objects.get(id=pk)
    formfile = MultiFileForm()
    formnote = MultiNoteForm()
    form = UpdateForm(instance=requisition)

    if request.method == 'POST':
        if 'update_hidden' in request.POST:
            form = UpdateForm(request.POST or None, instance=requisition) 
            if form.is_valid():
                r = form.save()

            # req_title = requisition.title
            # employee = request.user.newuser
            # mail_subject = 'A requisition has been Updated'  
            # print(request.user.first_name)
            # message = 'A new requisition has been updated\n' + 'under the name of ---' + req_title +'---'+ '\n by  ' + employee.name
            # r3 = requisition.send_to.values_list('email', flat=True)
            # tomail = list(r3)
            # tomail.remove(request.user.email)
            # try:
            #     send_mail(mail_subject, message,  EMAIL_HOST_USER, tomail)
            #     print('success')
            # except BadHeaderError:
            #     return HttpResponse('Invalid header found.') 

       


        if 'file_hidden' in request.POST:
            formfile = MultiFileForm(request.POST or None, request.FILES or None)
            files = request.FILES.getlist('file')

            if formfile.is_valid():
                for f in files:
                    MultiFile.objects.create(
                                req = requisition,
                                file = f,
                            )

    
        if 'note_hidden' in request.POST:
            formnote = MultiNoteForm(request.POST or None)
            if formnote.is_valid():
                n = formnote.save(commit=False)

                try:
                    MultiNote.objects.create(
                            req = requisition,
                            note = n,
                            written = request.user.newuser,
                    )
                except:
                    print("invalid object couldnt be created")
    
        return redirect('requisitions', pk)
        

    
        

           # email section->
            

    context = {
        'form':form,
        'requisition':requisition,
        'formfile':formfile,
        'formnote':formnote,

    }
    return render(request, 'user/update_requisition.html', context)



@login_required(login_url='loginpage')
@allowed_users(allowed_roles=['employee'])
def update_pending_requisition(request, pk):
    requisition= Requisition.objects.get(id=pk)

    formfile = MultiFileForm()
    formnote = MultiNoteForm()
    form = RequisitionForm(instance=requisition)
    employee = request.user.newuser

    if request.method == 'POST':
        if 'req_hidden' in request.POST:
            form = RequisitionForm(request.POST, instance=requisition)
            if form.is_valid():
                r= form.save()
                r.submitted_by = employee
                r.send_to.add(employee)
                r.status= 'Pending'
                r.save()

        if 'file_hidden' in request.POST:
            formfile = MultiFileForm(request.POST or None, request.FILES or None)
            files = request.FILES.getlist('file')

            if formfile.is_valid():
                for f in files:
                    MultiFile.objects.create(
                                req = requisition,
                                file = f,
                            )

    
        if 'note_hidden' in request.POST:
            formnote = MultiNoteForm(request.POST or None)
            if formnote.is_valid():
                n = formnote.save(commit=False)

                try:
                    MultiNote.objects.create(
                            req = requisition,
                            note = n,
                            written = request.user.newuser,
                    )
                except:
                    print("invalid object couldnt be created")

        


        return redirect('requisitions', pk)




    context = {
        'form':form,
        'requisition':requisition,
        'formfile':formfile,
        'formnote':formnote,

    }
    return render(request, 'user/update_pending_requisition.html', context)



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


