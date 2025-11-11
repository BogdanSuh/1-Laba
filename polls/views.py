from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.files.storage import FileSystemStorage

from .models import Question, Choice, Vote
from .forms import RegisterForm


# Главная страница со списком активных вопросов
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(
            expires_at__gt=timezone.now()
        ) | Question.objects.filter(expires_at__isnull=True)


# Страница с вопросом
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


# Страница с результатами
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# Голосование
@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.is_active():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Опрос завершён.'
        })

    if Vote.objects.filter(user=request.user, question=question).exists():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Вы уже голосовали в этом опросе.'
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Вы не сделали выбор.'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        Vote.objects.create(user=request.user, question=question)
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


# Регистрация
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            avatar = request.FILES['avatar']
            fs = FileSystemStorage(location='media/avatars/')
            fs.save(f"{user.username}.jpg", avatar)

            login(request, user)
            return redirect('polls:index')
    else:
        form = RegisterForm()
    return render(request, 'polls/register.html', {'form': form})