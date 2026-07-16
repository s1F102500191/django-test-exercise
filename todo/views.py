from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


# Create your views here.
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if not title:
            title = "ランダムなタスク"

        # 安全な due_at の処理: parse_datetime が None を返す可能性に対応
        due_at = None
        due_at_raw = request.POST.get('due_at')
        if due_at_raw:
            parsed = parse_datetime(due_at_raw)
            if parsed:
                # parsed がタイムゾーン情報を持たなければ補う
                if parsed.tzinfo is None:
                    due_at = make_aware(parsed)
                else:
                    due_at = parsed

        priority = request.POST.get('priority', 'normal')

        task = Task(title=title, due_at=due_at, priority=priority)
        task.save()

    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task
    }
    return render(request, 'todo/detail.html', context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task.delete()
    return redirect('index')

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method == 'POST':
        task.title = request.POST['title']
        # 安全に due_at を更新（無効な日付文字列は None とする）
        due_at = None
        due_at_raw = request.POST.get('due_at')
        if due_at_raw:
            parsed = parse_datetime(due_at_raw)
            if parsed:
                if parsed.tzinfo is None:
                    due_at = make_aware(parsed)
                else:
                    due_at = parsed
        task.due_at = due_at
        task.priority = request.POST.get('priority', 'normal')
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)

def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)
