from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
# Create your views here.
from .models import WeChatUser, Status, User, Reply
from blueking.component.shortcuts import get_client_by_request
from blueapps.patch.settings_open_saas import SITE_URL


def home(request):
    return render(request, "homepage.html")


@login_required
def show_user(request):
    po = WeChatUser.objects.get(user=request.user)
    return render(request, "user.html", {"user": po})


@login_required
def show_status(request):
    keyword = request.GET.get("keyword", "")
    page = request.GET.get("page", "1")

    if not keyword:
        statuses = Status.objects.all()
    else:
        statuses  =Status.objects.filter(Q(text__contains=keyword)|Q(user__user__username__contains=keyword))

    p = Paginator(statuses, 2)
    statuses = p.get_page(page)

    for status in statuses:
        status.likes = Reply.objects.filter(status=status, type="0")
        status.comments  =Reply.objects.filter(status=status, type="1")
    return render(request, "status.html", {"statuses": statuses,
                                           "user": request.user.username,
                                           "keyword": keyword,
                                           "page_range": p.page_range,
                                           "page": int(page),
                                           })


@login_required
def submit_post(request):
    user = WeChatUser.objects.get(user=request.user)
    text = request.POST.get("text")
    uploaded_file = request.FILES.get("pics")

    if uploaded_file:
        name = uploaded_file.name
        with open("./moments/static/image/{}".format(name), 'wb') as handler:
            for block in uploaded_file.chunks():
                handler.write(block)
    else:
        name = ''


    if text:
        status = Status(user=user, text=text, pics=name)
        status.save()
        return redirect("/status")

    return render(request, "my_post.html")




def register(request):
    try:
        username, password, email = [request.POST.get(key) for key in ("username", "password", "email")]

        #user = User(username=username, email=email)
        #user.set_password(password)
        #user.save()

        WeChatUser.objects.create(user=request.user,email=email)
    except Exception as err:
        result = False
        message = str(err)
    else:
        result = True
        message = "Register success"
    return JsonResponse({'result': result, 'message': message})


@login_required
def update_user(request):
    try:
        kwargs = {key:request.POST.get(key) for key in ("motto", "region", "pic","email") if request.POST.get(key)}
        WeChatUser.objects.filter(user=request.user).update(**kwargs)

        #email = request.POST.get("email")
        #if email:
        #   dj_user = User.objects.get(username=request.user.username)
        #    dj_user.email = email
         #   dj_user.save()

    except Exception as err:
        result = False
        message = str(err)
    else:
        result = True
        message = "Update success"
    return JsonResponse({'result': result, 'message': message})


@login_required
def like(request):
    user = request.user.username
    status_id = request.POST.get("status_id")

    liked = Reply.objects.filter(author=user, status=status_id, type="0")
    if liked:
        liked.delete()
    else:
        Reply.objects.create(author=user, status=Status.objects.get(id=status_id), type="0")
        client = get_client_by_request(request)
        client.cmsi.send_mail(receiver=Status.objects.get(id=status_id).user.email,
                              title="点赞通知",
                              content="{}赞了你的朋友圈状态{}".format(user,Status.objects.get(id=status_id).text))

                              
    
    return JsonResponse({"result": True})

@login_required
def comment(request):
    user = request.user.username
    status_id = request.POST.get("status_id")
    at_person = request.POST.get("at_person", "")
    text = request.POST.get("text")

    Reply.objects.create(author=user, status=Status.objects.get(id=status_id), type="1", at_person=at_person, text=text)
    return JsonResponse({"result": True})

@login_required
def delete_comment(request):
    comment_id = request.POST.get("comment_id")
    Reply.objects.filter(id=comment_id).delete()
    return JsonResponse({"result": True})

@login_required
def report(request):
    return render(request,"report.html")

def stats(request):
    statuses=Status.objects.all()
    users_list=statuses.values_list("user__user__username")
    counter=counter(user_list)
    top_ten=counter.most_common(10)
    data={"data":{"xAxis":[{
                   "type":"category",
                   "data":[user[0][0] for user in top_ten]


                        }],
                  },
          "result":True,
          "code":0
          }
    return JsonResponse(data)