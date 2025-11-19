# polls/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from .models import Question, Choice, Vote, Profile
from .forms import RegisterForm, ProfileUpdateForm


User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # ← пароль захеширован, Profile обновлён
            login(request, user)
            return redirect('polls:index')
        # else: ошибки будут в form.errors (отобразятся в шаблоне)
    else:
        form = RegisterForm()
    return render(request, 'polls/register.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'polls/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # ← Profile.save() вызывается автоматически
            return redirect('polls:profile_view')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'polls/profile_edit.html', {'form': form})


@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # hard delete (можно заменить на user.is_active = False)
        logout(request)
        return redirect('polls:index')
    return render(request, 'polls/profile_delete.html')


# --- Опросы ---
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        now = timezone.now()
        return Question.objects.filter(
            expires_at__gt=now
        ).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


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
            'error_message': 'Вы не выбрали вариант ответа.'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        Vote.objects.create(user=request.user, question=question)
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))