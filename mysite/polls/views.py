from django.http import HttpResponse
from django.shortcuts import render
from polls.models import Poll
from polls.models import Question
from polls.models import Answer

# Create your views here.
def index(request):

    poll_list = Poll.objects.all()

    print(poll_list.query)

    for poll in poll_list:
        question_count = Question.objects.filter(poll_id=poll.id).count()
        poll.question_count = question_count

    context ={
        'page_title': 'Wellcom to my poll page',
        'poll_list':poll_list,
    }

    return render(request, template_name='polls/index.html', context=context)

def detail(request , poll_id):
    poll = Poll.objects.get(pk=poll_id)
    poll_list = Poll.objects.all()
    context = {
        'poll': poll,
    }

    if request.method == 'GET':
        qd = request.GET
    print(qd)

    for poll_question in poll.question_set.all():
        x = poll_question
        print(x)


    return render(request, template_name='polls/detail.html', context=context)

# def save_answer(answer, ):
#     choice.objects.get(choice.question_id)
#     question.objects.get()
#     return null