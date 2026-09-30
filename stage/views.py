from django.shortcuts import render,redirect
from .models import Project,Task
from account.models import User
from member.models import Invite,Team
from django.utils.dateparse import parse_date
from django.db.models import Q
from random import sample
def projectowns(req):
    user_id = req.session.get('user_id')
    if user_id:
        projects = Project.objects.filter(created_by_id=user_id).order_by('-start_date')
        projects_status=[]
        for p in projects:
            members=Team.objects.filter(project=p.id).count()
            projects_status.append({'p': p,'m': members})
        return render(req,'p1.html',{'active_page': 'projects','projects': projects_status})
    else:
        return redirect('/signup')
def project_create(req):
    if req.method=='POST':
        title=req.POST.get('title').strip()
        description=req.POST.get('description').strip()
        status=req.POST.get('status').title()
        start_date=parse_date(req.POST.get('start_date'))
        end_date=parse_date(req.POST.get('end_date'))
        if title and description and status and start_date and end_date:
            if Project.objects.filter(title=title).exists():
                error='Project Title Already Exist! Choose Another Title'
            elif start_date>=end_date:
                error='Please Enter End Date Must After The Start Date'
            else:
                user_id=req.session.get('user_id')
                if not user_id:
                    return redirect('/signup')
                try:
                    user=User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return redirect('/signup')
                p=Project.objects.create(
                    title=title,
                    description=description,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    created_by=user
                )
                Team.objects.create(
                    project=p,
                    user=user,
                )
                return redirect('/project')
        else:
            error='All fields are required!'
        return render(req, 'p2.html', {'active_page':'projects','error': error,'user_data':req.POST})
    else:
        return render(req,'p2.html',{'active_page':'projects'})
def project_detail(req):
    if req.method=="POST":
        user_id=req.session.get("user_id")
        p=req.POST.get("pid")
        a=req.POST.get('action')
        if not user_id:
            return redirect("/signin")
        if a in("task_edit","task_save","task_cancel","task_delete"):
            try:
                project=Task.objects.get(id=p)
                teams=Team.objects.filter(project=project.project.id)
            except:
                return redirect("/project")
            if project.project.created_by.id!=user_id or not a:
                return redirect("/project")
        else:
            try:
                if a=="remove_team":
                    t=Team.objects.get(id=p)
                    p=t.project.id
                    t.delete()
                project=Project.objects.get(id=p)
                teams=Team.objects.filter(project=p)
            except:
                return redirect("/project")
            if project.created_by.id!=user_id or not a:
                return redirect("/project")
        if a in ("view","remove_team"):
            tasks=Task.objects.filter(project=p).order_by('-due_date')
            return render(req,"p3.html",{'active_page':'projects',"project":project,"tasks":tasks,"teams":teams})
        elif a=="project_edit":
            project.start_date=str(project.start_date)
            project.end_date=str(project.end_date)
            return render(req,"p7.html",{'active_page':'projects',"project":project})
        elif a=="invite":
            user_f=User.objects.get(id=user_id)
            user_t=User.objects.get(id=req.POST.get("user_invite_id"))
            if user_t:
                if not Invite.objects.filter(from_user=user_id,to_user=user_t).exists():
                    Invite.objects.create(
                        from_user=user_f,
                        to_user=user_t,
                        project=project,
                        status='Invited',
                    )
            tasks=Task.objects.filter(project=p).order_by('-due_date')
            return render(req,"p3.html",{'active_page':'projects',"project":project,"tasks":tasks,"teams":teams})
        elif a=="search":
            q=req.POST.get("search")
            if q!="" and q!= None:
                users=list(User.objects.filter(Q(username__icontains=q) | Q(email__icontains=q)).values_list('id', flat=True))
            else:
                q=""
                users=list(User.objects.values_list('id', flat=True))
            team_users = Team.objects.filter(project=p).values_list('user', flat=True)
            invite_users=Invite.objects.filter(project=p).values_list('to_user', flat=True)
            request_users=Invite.objects.filter(project=p).values_list('from_user', flat=True)
            users=sample(users, min(10, len(users)))
            users=User.objects.filter(id__in=users)
            users_status=[]
            for user in users:
                if user.id==user_id:
                    status = 'Owner'
                elif user.id in team_users:
                    status = 'Already Joined'
                elif user.id in invite_users:
                    status = 'Invited'
                elif user.id in request_users:
                    status = 'Requested'
                else:
                    status = 'Invite'
                users_status.append({'user': user,'status': status})
            return render(req,"p6.html",{'active_page':'projects','pname':project.title,'pid':p,"query":q,"users":users_status})
        elif a=="delete":
            project.delete()
            return redirect('/project')
        elif a=="task_create":
            return render(req,"p4.html",{'active_page':'projects',"project":project,"teams":teams})
        elif a=="create":
            title=req.POST.get('title').strip()
            description=req.POST.get('description').strip()
            assigned_to=req.POST.get('assigned_to')
            status=req.POST.get('status').title()
            priority=req.POST.get('priority').title()
            due_date=parse_date(req.POST.get('due_date'))
            if assigned_to and Team.objects.filter(id=assigned_to).exists():
                members=Team.objects.get(id=assigned_to)
            else:
                members=None
            if title and description and status and priority and due_date:
                if Task.objects.filter(title=title).exists():
                    error='Task Title Already Exist! Choose Another Title'
                elif due_date>project.end_date or project.start_date>due_date:
                    error='Please Enter Due Date Must Between The Start Date And End Date Of Project'
                else:
                    Task.objects.create(
                        project=project,
                        title=title,
                        description=description,
                        assigned_to=members,
                        status=status,
                        priority=priority,
                        due_date=due_date,
                    )
                    tasks=Task.objects.filter(project=p).order_by('-due_date')
                    return render(req,"p3.html",{'active_page':'projects',"project":project,"tasks":tasks,"teams":teams})
            else:
                error='All fields are required!'
            teams=Team.objects.filter(project=p)
            return render(req,"p4.html",{'active_page':'projects',"project":project,"error":error,"teams":teams,'user_data':req.POST})
        elif a=="task_edit":
            project.due_date=str(project.due_date)
            return render(req,"p5.html",{'active_page':'projects',"task":project,"teams":teams})
        elif a=="save":
            title=req.POST.get('title').strip()
            description=req.POST.get('description').strip()
            status=req.POST.get('status').title()
            start_date=parse_date(req.POST.get('start_date'))
            end_date=parse_date(req.POST.get('end_date'))
            if title and description and status and start_date and end_date:
                if Project.objects.filter(title=title).exclude(id=p).exists():
                    error='Project Title Already Exist! Choose Another Title'
                elif start_date>=end_date:
                    error='Please Enter End Date Must After The Start Date'
                else:
                    project.title=title
                    project.description=description
                    project.status=status
                    project.start_date=start_date
                    project.end_date=end_date
                    project.save()
                    tasks=Task.objects.filter(project=p).order_by('-due_date')
                    return render(req,"p3.html",{'active_page':'projects',"project":project,"tasks":tasks,"teams":teams})
            else:
                error='All fields are required!'
            return render(req,"p7.html",{'active_page':'projects',"project":req.POST,'error':error})
        elif a in("task_save","task_cancel","task_delete"):
            p=project.project.id
            task=project
            project=Project.objects.get(id=p)
            if a=="task_save":
                title=req.POST.get('title').strip()
                description=req.POST.get('description').strip()
                assigned_to=req.POST.get('assigned_to')
                status=req.POST.get('status')
                priority=req.POST.get('priority')
                due_date=parse_date(req.POST.get('due_date'))
                members=None if assigned_to=="" else Team.objects.get(id=assigned_to) 
                if not(title and description and status and priority and due_date):
                    error='All fields are required!'
                elif Task.objects.filter(title=title).exclude(id=task.id).exists():
                    error='Task Title Already Exist! Choose Another Title'
                elif due_date>project.end_date or project.start_date>due_date:
                    error='Please Enter Due Date Must Between The Start Date And End Date Of Project'
                else:
                    error=None
                    task.project=project
                    task.title=title
                    task.description=description
                    task.assigned_to=members
                    task.status=status
                    task.priority=priority
                    task.due_date=due_date
                    task.save()
                if error:
                    task={i: dict(req.POST)[i][0] for i in dict(req.POST)}
                    task['due_date']=str(task['due_date'])
                    task['assigned_to']={'id':int(task['assigned_to'])}
                    return render(req,"p5.html",{'active_page':'projects',"task":task,"teams":teams,'error':error})
            elif a=="task_delete":
                task.delete()
            tasks=Task.objects.filter(project=p).order_by('-due_date')
            return render(req,"p3.html",{"active_page":"projects","project":project,"tasks":tasks,"teams":teams})
        else:
            return redirect('/signin')
    return redirect("/signin")
def taskowns(req):
    user_id=req.session.get("user_id")
    if user_id:
        if req.method=='POST':
            p=req.POST.get("tid")
            a=req.POST.get('action')
            if a=="view":
                task=Task.objects.get(id=p)
                return render(req,'t2.html',{'active_page':'tasks',"task":task,'userid':user_id})
            elif a=="update":
                task=Task.objects.get(id=p)
                status=req.POST.get('status')
                task.status=status
                task.save()
            elif a=="leave_task":
                task=Task.objects.get(id=p)
                team=Team.objects.get(id=task.assigned_to.id)
                team.delete()
            elif a=="leave_project":
                team=Team.objects.filter(user=user_id,project=p)
                if team and len(team)==1:
                    team.delete()
            return redirect('/tasks')
        else:
            team=Team.objects.filter(user=user_id)
            tasks=Task.objects.filter(assigned_to__in=team).order_by('-due_date')
            projects=Project.objects.filter(id__in=team.values_list('project', flat=True)).exclude(id__in=tasks.values_list('project', flat=True).distinct()).exclude(created_by=user_id)
            return render(req,'t1.html',{'active_page':'tasks',"tasks":tasks,"projects":projects})
    else:
        return redirect("/signin")
