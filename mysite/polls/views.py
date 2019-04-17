from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import PollForm,CommentForm, ChangePasswordForm, RegisterForm
from .models import Poll, Question, Answer, Comment, Profile

from django.contrib.auth.models import User

def my_login(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            next_url = request.POST.get('next_url')
            if(next_url):
                return  redirect(next_url)
            else:
                return  redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Wrong username or password!!!'
    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url

    return render(request, template_name='polls/login.html', context=context)

def my_logout(request):
    logout(request)
    return redirect('login')

def index(request):
    # poll_list = Poll.objects.all()
    poll_list = Poll.objects.filter(del_flag=False)
    print(poll_list.query)
    print(request.user)
    for poll in poll_list:
        question_count = Question.objects.filter(poll_id=poll.id).count()
        poll.question_count = question_count

    context = {
        'page_title': 'My polls',
        'poll_list': poll_list
    }

    return render(request, template_name='polls/index.html', context=context)

@login_required
@permission_required('polls.view_poll')
def detail(request, poll_id):

    poll = Poll.objects.get(pk=poll_id)

    for question in poll.question_set.all():
        name = 'choice' + str(question.id)
        choice_id = request.GET.get(name)

        if choice_id:
            try:
                ans = Answer.objects.get(question_id=question.id)
                ans.choice_id = choice_id
                ans.save()

            except Answer.DoesNotExist:
                Answer.objects.create(
                    choice_id=choice_id,
                    question_id=question.id
                )

        print(choice_id)
    print(request.GET)
    return  render(request, 'polls/question.html', {'poll': poll})


def create(request):

    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = Poll.objects.create(
                title=form.cleaned_data.get('title'),
                start_date=form.cleaned_data.get('start_date'),
                end_date=form.cleaned_data.get('end_date'),
            )

            for i in range(1, form.cleaned_data.get('no_questions')+1):
                Question.objects.create(
                    text='0000' + str(i),
                    type='01',
                    poll=poll
                )
        # title = request.POST.get('title')
        # question_list = request.POST.getlist('questions[]')
    else:
        form = PollForm()

    context = {'form': form}
    return render(request, 'polls/create.html', context=context)

def comment(request, poll_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                title=form.cleaned_data.get('title'),
                body=form.cleaned_data.get('body'),
                email=form.cleaned_data.get('email'),
                tel=form.cleaned_data.get('tel'),
                poll_id = poll_id
            )

    else:
        form = CommentForm()
    context = {'form': form}
    return render(request,'polls/create-comment.html', context=context)


@login_required
def changePassword(request):

    context={}

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        username = request.user.username
        old_password = request.POST.get('old_password')
        user = authenticate(request, username=username, password=old_password)

        print("old password %s" %old_password)

        if user and form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()

            print("New password %s" %new_password)
            return redirect('/polls/index')
        else:
            context['error'] = 'Wrong password!!!'
    else:
        form = ChangePasswordForm()

    context['form'] = form
    return render(request,'polls/change_password.html', context=context)


def my_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password'),
                email=form.cleaned_data.get('email')
            )
            profile = Profile.objects.create(
                user_id=user.id,
                line_id=form.cleaned_data.get('line_id'),
                facebook=form.cleaned_data.get('facebook'),
                gender=form.cleaned_data.get('gender'),
                birthdate=form.cleaned_data.get('birthdate'),
            )
    else:
        form = RegisterForm()
    context = {'form': form}

    return render(request,'polls/register.html', context=context)


# poll_list = [
#         {
#             'id': 1,
#             'title': 'การสอนวิชา Web Programming',
#             'questions': [
#                 {
#                     'text': 'อาจารย์บัณฑิตสอนน่าเบื่อไหม',
#                     'choices': [
#                         {'text': 'น่าเบื่อมาก', 'value': 1},
#                         {'text': 'ค่อนข้างน่าเบื่อ', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างสนุก', 'value': 4},
#                         {'text': 'สนุกมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'นักศึกษาเรียนรู้เรื่องหรือไม่',
#                     'choices': [
#                         {'text': 'ไม่รู้เรื่องเลย', 'value': 1},
#                         {'text': 'รู้เรื่องนิดหน่อย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'เรียนรู้เรื่อง', 'value': 4},
#                         {'text': 'เรียนเข้าใจมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'เครื่องคอมพิวเตอร์ใช้งานดีหรือไม่',
#                     'choices': [
#                         {'text': 'เครื่องช้ามาก', 'value': 1},
#                         {'text': 'เครื่องค่อนข้างช้า', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'เครื่องเร็ว', 'value': 4},
#                         {'text': 'เครื่องเร็วมากๆ', 'value': 5}
#                     ]
#                 },

#             ]
#         },
#         {
#             'id': 2,
#             'title': 'ความยากข้อสอบ mid-term',
#             'questions': [
#                 {
#                     'text': 'ข้อ 1',
#                     'choices': [
#                         {'text': 'ง่ายมากๆ', 'value': 1},
#                         {'text': 'ค่อนข้างง่าย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างยาก', 'value': 4},
#                         {'text': 'ยากมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'ข้อ 2',
#                     'choices': [
#                         {'text': 'ง่ายมากๆ', 'value': 1},
#                         {'text': 'ค่อนข้างง่าย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างยาก', 'value': 4},
#                         {'text': 'ยากมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'ข้อ 3',
#                     'choices': [
#                         {'text': 'ง่ายมากๆ', 'value': 1},
#                         {'text': 'ค่อนข้างง่าย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างยาก', 'value': 4},
#                         {'text': 'ยากมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'ข้อ 4',
#                     'choices': [
#                         {'text': 'ง่ายมากๆ', 'value': 1},
#                         {'text': 'ค่อนข้างง่าย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างยาก', 'value': 4},
#                         {'text': 'ยากมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'ข้อ 5',
#                     'choices': [
#                         {'text': 'ง่ายมากๆ', 'value': 1},
#                         {'text': 'ค่อนข้างง่าย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างยาก', 'value': 4},
#                         {'text': 'ยากมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'ข้อ 6',
#                     'choices': [
#                         {'text': 'ง่ายมากๆ', 'value': 1},
#                         {'text': 'ค่อนข้างง่าย', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างยาก', 'value': 4},
#                         {'text': 'ยากมากๆ', 'value': 5}
#                     ]
#                 },

#             ]
#         },

#         {
#             'id': 3,
#             'title': 'อาหารที่ชอบ',
#             'questions': [
#                 {
#                     'text': 'พิซซ่า',
#                     'choices': [
#                         {'text': 'ไม่ชอบเลย', 'value': 1},
#                         {'text': 'ค่อนข้างไม่ชอบ', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างชอบ', 'value': 4},
#                         {'text': 'ชอบมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'ไก่ทอด',
#                     'choices': [
#                         {'text': 'ไม่ชอบเลย', 'value': 1},
#                         {'text': 'ค่อนข้างไม่ชอบ', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างชอบ', 'value': 4},
#                         {'text': 'ชอบมากๆ', 'value': 5}
#                     ]
#                 },
#                 {
#                     'text': 'แฮมเบอร์เกอร์',
#                     'choices': [
#                         {'text': 'ไม่ชอบเลย', 'value': 1},
#                         {'text': 'ค่อนข้างไม่ชอบ', 'value': 2},
#                         {'text': 'เฉยๆ', 'value': 3},
#                         {'text': 'ค่อนข้างชอบ', 'value': 4},
#                         {'text': 'ชอบมากๆ', 'value': 5}
#                     ]
#                 },

#             ]
#         },
#     ]


# # Create your views here.
# def index(request):
#     context = {
#         'page_title': 'Welcome to the party',
#         'poll_list': poll_list
#     }

#     return render(request, template_name='polls/index.html', context=context)

# def detail(request, poll_id):
#     context = {
#         'poll_id' : poll_id,
#         'poll_list' : poll_list[poll_id-1]
#     }
#     return render(request, template_name='polls/question.html', context=context)
