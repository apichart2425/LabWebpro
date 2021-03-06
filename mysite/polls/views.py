from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.forms import formset_factory

import json

from .forms import PollForm,CommentForm, ChangePasswordForm, RegisterForm, PollModelForm, QuestionForm, ChoiceModelForm
from .models import Poll, Question, Answer, Comment, Profile,Choice

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

@login_required
@permission_required('polls.add_poll')
def create(request):
    context = {}
    QuestionFormSet = formset_factory(QuestionForm , extra=2)

    # this comment old code
    if request.method == 'POST':
        # form = PollForm(request.POST)

        form = PollModelForm(request.POST)
        formset = QuestionFormSet(request.POST)

        if form.is_valid():
            poll = form.save()
            if formset.is_valid():
                for question_form in formset:
                    Question.objects.create(
                        text = question_form.cleaned_data.get('text'),
                        type = question_form.cleaned_data.get('type'),
                        poll = poll
                    )
                
                context['success'] = "Poll %s is create successfully" % poll.title


            # poll = Poll.objects.create(
            #     title=form.cleaned_data.get('title'),
            #     start_date=form.cleaned_data.get('start_date'),
            #     end_date=form.cleaned_data.get('end_date'),
            # )

            # for i in range(1, form.cleaned_data.get('no_questions')+1):
            #     Question.objects.create(
            #         text='0000' + str(i),
            #         type='01',
            #         poll=poll
            #     )
        # title = request.POST.get('title')
        # question_list = request.POST.getlist('questions[]')
    else:
        form = PollModelForm()
        formset = QuestionFormSet()
        # form = PollForm()

    context['form'] = form
    context['formset'] = formset
    return render(request, 'polls/create.html', context=context)

@login_required
@permission_required('polls.change_poll')
def update(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)

    # week 5 model form
    if request.method == 'POST':
        print("POST ---------> %s" %request.POST)

        form = PollModelForm(request.POST, instance=poll)
        formset = QuestionFormSet(request.POST)

        if form.is_valid():
            form.save()
            if formset.is_valid():
                print(len(formset))
                for question_form in formset:
                    print("1")
                    if question_form.cleaned_data.get('question_id'):
                        print('2')
                        question = Question.objects.get(id=question_form.cleaned_data.get('question_id'))
                        if question:
                            question.text = question_form.cleaned_data.get('text')
                            question.type = question_form.cleaned_data.get('type')
                            question.save()
                    else:
                        print('3')
                        if question_form.cleaned_data.get('text'):
                            Question.objects.create(
                            text=question_form.cleaned_data.get('text'),
                            type=question_form.cleaned_data.get('type'),
                            poll=poll
                            )
                return redirect('update_poll', poll_id=poll.id)

    else:
        form = PollModelForm(instance=poll)
        data = []
        for question in poll.question_set.all():
            data.append(
                {
                    'text': question.text,
                    'type': question.type,
                    'question_id': question.id
                }
            )


        formset = QuestionFormSet(initial=data)

    context = {'form': form, 'formset': formset ,'poll': poll}
    return render(request, 'polls/update.html', context=context)

@login_required
@permission_required('polls.change_poll')
def delete_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.choice_set.all().delete()
    question.delete()
    return redirect('update_poll', poll_id=question.poll.id)

@login_required
@permission_required('polls.change_poll')
def add_choice(request, question_id):
    question = Question.objects.get(id=question_id)

    context = {'question': question}

    return render(request, 'choices/add.html', context=context)

def add_choice_api(request, question_id):
    if request.method == 'POST':
        choice_list = json.loads(request.body)
        error_list = []

        for choice in choice_list:
            data = {
                'text': choice['text'],
                'value': choice['value'],
                'question': question_id
            }
            form = ChoiceModelForm(data)
            if form.is_valid():
                form.save()
            else:
                error_list.append(form.errors.as_text())

        if len(error_list) == 0:
            return  JsonResponse({'message': 'success'}, status=200)
        else:
            return  JsonResponse({'message': error_list}, status=400)

    return JsonResponse({'message': 'This API dose not accept GET Request.'}, status =405)


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
