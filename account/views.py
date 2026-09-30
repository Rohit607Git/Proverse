from django.shortcuts import render,redirect
from .models import User
from stage.models import Project
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
from random import sample
def home(req):
    return render(req,'homeweb.html')
def publicprojects(req):
    if req.method=='GET':
        q=req.GET.get("search")
        if q!="" and q!= None:
            projects=list(Project.objects.filter(Q(title__icontains=q.strip()) | Q(description__icontains=q.strip()),status='Public').values_list('id', flat=True))
        else:
            q=""
            projects=list(Project.objects.filter(status='Public').values_list('id', flat=True))
    else:
        q=""
        projects=list(Project.objects.filter(status='Public').values_list('id', flat=True))
    projects=sample(projects, min(10, len(projects)))
    projects=Project.objects.filter(id__in=projects)
    return render(req,'projectsweb.html',{'query':q,'projects':projects})
def about(req):
    return render(req,'aboutusweb.html')
def signin(req):
    if req.method=='POST':
        username=req.POST.get('username').strip()
        password=req.POST.get('password').strip()
        if username and password:
            try:
                user=User.objects.get(username=username)
                if check_password(password,user.password):
                    req.session['user_id']=user.id
                    return redirect('/dashboard')
                else:
                    error="Invalid Password"
            except User.DoesNotExist:
                error="User Not Found"
        else:
            error='All Fields Are Required!'
        return render(req, 'loginweb.html',{'error':error,'user_data':req.POST})
    return render(req,'loginweb.html')
def signout(req):
    try:
        del req.session['user_id']
    except:
        pass
    return redirect('/signin')
def signup(req):
    if req.method=='POST':
        username=req.POST.get('username').strip()
        email=req.POST.get('email').strip()
        password=req.POST.get('password').strip()
        cpassword=req.POST.get('confirm_password').strip()
        gender=req.POST.get('gender')
        if username and email and password and cpassword and gender:
            if User.objects.filter(username=username).exists():
                error='Username Already Exist! Try Another One'
            elif len(password)<4:
                error='Please Enter Password Atleast 4 Characters'
            elif password!=cpassword:
                error='Password Not Matched!'
            else:
                User.objects.create(
                    username=username,
                    email=email,
                    gender=gender,
                    password=make_password(password))
                return redirect('/signin')
        else:
            error='All Fields Are Required!'
        return render(req, 'registerweb.html',{'error':error,'user_data':req.POST})
    else:
        return render(req, 'registerweb.html')
def acinfo(req):
    user_id=req.session.get('user_id')
    if not user_id:
        return redirect('/signin')
    try:
        user=User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('/signin')
    if req.method == 'POST':
        user.delete()
        return redirect('/')
    return render(req,'ac1.html',{'user': user,'active_page':'account'})
def acedit(req):
    user_id = req.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('/signin')
    if req.method == 'POST':
        fullname=req.POST.get('fullname').strip()
        username=req.POST.get('username').strip()
        email=req.POST.get('email').strip()
        gender=req.POST.get('gender')
        role=req.POST.get('role')
        role=role if role else None
        skills=','.join(req.POST.getlist('skills'))
        skills=None if skills=="" else skills
        f=fullname.replace(' ','')
        if not(username and email and gender):
            error='Username, Email and Gender Fields Are Required!'
        elif fullname and not f.replace(" ","").isalpha():
            error='Full name must use letters and spaces only.'
        elif User.objects.filter(username=username).exclude(id=user_id).exists():
            error='Username Already Exist! Try Another One'
        else:
            m=User.objects.get(id=user_id)
            m.fullname=fullname if fullname else None
            m.username=username
            m.email=email
            m.gender=gender
            m.role=role
            m.skills=skills
            m.save()
            return redirect('/account')
        user.fullname="" if user.fullname is None else user.fullname
        user_data={i:dict(req.POST)[i][0] for i in dict(req.POST)}
        user_data['skills']=','.join(req.POST.getlist('skills'))
        return render(req,'ac2.html',{'active_page':'account','user':user_data,'error':error})
    else:
        user.skills=user.skills.split(',') if user.skills else []
        user.fullname= user.fullname if user.fullname else ""
        return render(req,'ac2.html',{'active_page': 'account','user':user})
def acchangepass(req):
    error=None
    if req.method == 'POST':
        user_id=req.session.get('user_id')
        cpassword=req.POST.get('comfirm_password')
        password=req.POST.get('new_password')
        if not user_id:
            return redirect('/signin')
        elif not(password or cpassword):
            error='Enter New Password And Type Again To Comfirm'
        elif len(password)<4:
            error='Please Enter Password Atleast 4 Characters'
        elif password!=cpassword:
            error='Password Not Matched!'
        else:
            try:
                m=User.objects.get(id=user_id)
                m.password=make_password(password)
                m.save()
                return redirect('/account')
            except User.DoesNotExist:
                return redirect('/signin')
    return render(req,'ac3.html',{'active_page':'account','error':error})