from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from todo.models import Task


def parse_due_at(value):
    if not value:
        return None

    due_at = parse_datetime(value)

    if due_at is None:
        return None

    if timezone.is_naive(due_at):
        due_at = timezone.make_aware(due_at)

    return due_at


def index(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        due_at = parse_due_at(request.POST.get('due_at'))

        Task.objects.create(
            title=title,
            due_at=due_at
        )

        return redirect('index')

    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        task.title = request.POST.get('title', '').strip()
        task.due_at = parse_due_at(request.POST.get('due_at'))
        task.save()

        return redirect('detail', task_id=task.id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)


@require_POST
def close(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.completed = True
    task.save()

    return redirect('index')


@require_POST
def delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()

    return redirect('index')