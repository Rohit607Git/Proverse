from django.shortcuts import render,redirect
from account.models import User
from stage.models import Project,Task
from member.models import Invite,Team
from random import sample
from django.db.models import Q

def recive_invite(req):
    user_id = req.session.get('user_id')
    if user_id:
        if req.method=='POST':
            a=req.POST.get('action')
            p=req.POST.get('pid')
            try:
                i=Invite.objects.get(id=p)
            except:
                return redirect('/invites')
            if a=="accept":
                Team.objects.create(
                    project=i.project,
                    user=i.to_user,
                )
                i.delete()
            elif a=="reject":
                i.delete()
        invited_project=Invite.objects.filter(to_user=user_id,status="Invited")
        return render(req,'i1.html',{'active_page': 'invites','num_invites':len(invited_project),'user_invites':invited_project})
    else:
        return redirect('/signup')
def join_invite(req):
    user_id = req.session.get('user_id')
    if user_id:
        if req.method=='POST':
            a=req.POST.get('action')
            if a=="search":
                q=req.POST.get("search").strip()
                if q!="" and q!= None:
                    projects=list(Project.objects.filter(Q(title__icontains=q) | Q(description__icontains=q),status='Public').values_list('id', flat=True))
                else:
                    q=""
                    projects=list(Project.objects.filter(status='Public').exclude(created_by=user_id).values_list('id', flat=True))
            elif a=="requested":
                p=req.POST.get('pid')
                project=Project.objects.get(id=p)
                team_users = Team.objects.filter(project=p).values_list('user', flat=True)
                request_users=Invite.objects.filter(project=p,status__in=["Requested","Rejected"]).values_list('from_user', flat=True)
                invite_users=Invite.objects.filter(project=p,status__in=["Invited","Rejected"]).values_list('to_user', flat=True)
                if user_id == project.created_by.id or user_id in team_users or user_id in request_users or user_id in invite_users:
                    return redirect('/public')
                user_f=User.objects.get(id=user_id)
                user_t=User.objects.get(id=project.created_by.id)
                Invite.objects.create(
                    from_user=user_f,
                    to_user=user_t,
                    project=project,
                    status='Requested',
                )
                q=""
                projects=list(Project.objects.filter(status='Public').exclude(created_by=user_id).values_list('id', flat=True))
        else:
            q=""
            projects=list(Project.objects.filter(status='Public').exclude(created_by=user_id).values_list('id', flat=True))
        team_users = Team.objects.filter(user=user_id).values_list('project', flat=True)
        request_users=Invite.objects.filter(from_user=user_id,status="Requested").values_list('project', flat=True)
        invite_users=Invite.objects.filter(to_user=user_id,status="Invited").values_list('project', flat=True)
        projects=sample(projects, min(10, len(projects)))
        projects=Project.objects.filter(id__in=projects)
        projects_status=[]
        for p in projects:
            if p.created_by.id==user_id:
                status = 'Owner'
            elif p.id in team_users:
                status = 'Already Joined'
            elif p.id in request_users:
                status = 'Requested'
            elif p.id in invite_users:
                status = 'Invited'
            else:
                status = 'Join'
            projects_status.append({'p': p,'s': status})
        return render(req,'pp.html',{'active_page': 'public','query':q,'projects':projects_status})
    else:
        return redirect('/signup')
def dashboard_user(req):
    user_id = req.session.get('user_id')
    if user_id:
        if req.method=='POST':
            a=req.POST.get('action')
            iid=req.POST.get('iid')
            if a=='cancel':
                i=Invite.objects.get(id=iid)
                if i.from_user.id == user_id:
                    i.delete()
            elif a=='accept':
                i=Invite.objects.get(id=iid)
                if i.to_user.id == user_id:
                    Team.objects.create(
                        project=i.project,
                        user=i.from_user,
                    )
                    i.delete()
            elif a=='reject':
                i=Invite.objects.get(id=iid)
                if i.to_user.id == user_id:
                    i.status='Rejected'
                    i.save()
            elif a=='remove':
                i=Invite.objects.get(id=iid)
                if i.from_user.id == user_id:
                    i.delete()
        users=[]
        n=User.objects.get(id=user_id)
        users.append(n)
        n=Project.objects.filter(created_by=user_id).count()
        users.append(n)
        n=Team.objects.filter(user=user_id).values_list('id',flat=True)
        tasks=Task.objects.filter(assigned_to__in=n).order_by('-due_date')
        users.append(tasks.count())
        n=Invite.objects.filter(to_user=user_id,status='Invited').count()
        from_views=Invite.objects.filter(from_user=user_id)
        to_views=Invite.objects.filter(to_user=user_id,status='Requested')
        users.append(n)
        return render(req,'dashboardweb.html',{'active_page': 'dashboard','no_kpi':users,'tasks':tasks,'from_views':from_views,'to_views':to_views})
    else:
        return redirect('/signup')
