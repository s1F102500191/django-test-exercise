from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from todo.models import Task
from todo import views as todo_views


class SampleTestCase(TestCase):
    def test_sample1(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(
            datetime(2026, 6, 24, 23, 59, 59)
        )

        task = Task.objects.create(
            title='task1',
            due_at=due
        )

        saved_task = Task.objects.get(pk=task.pk)

        self.assertEqual(saved_task.title, 'task1')
        self.assertFalse(saved_task.completed)
        self.assertEqual(saved_task.due_at, due)

    def test_create_task2(self):
        task = Task.objects.create(
            title='task2'
        )

        saved_task = Task.objects.get(pk=task.pk)

        self.assertEqual(saved_task.title, 'task2')
        self.assertFalse(saved_task.completed)
        self.assertIsNone(saved_task.due_at)

    def test_is_overdue_future(self):
        due = timezone.make_aware(
            datetime(2026, 6, 24, 23, 59, 59)
        )
        current = timezone.make_aware(
            datetime(2026, 6, 24, 0, 0, 0)
        )

        task = Task.objects.create(
            title='task1',
            due_at=due
        )

        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.make_aware(
            datetime(2026, 6, 24, 23, 59, 59)
        )
        current = timezone.make_aware(
            datetime(2026, 6, 25, 0, 0, 0)
        )

        task = Task.objects.create(
            title='task1',
            due_at=due
        )

        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        current = timezone.make_aware(
            datetime(2026, 6, 24, 0, 0, 0)
        )

        task = Task.objects.create(
            title='task1',
            due_at=None
        )

        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_now_true_false(self):
        # due in past -> overdue
        past = timezone.now() - timezone.timedelta(days=1)
        t1 = Task(title='past', due_at=past)
        t1.save()
        self.assertTrue(t1.is_overdue_now())

        # due in future -> not overdue
        future = timezone.now() + timezone.timedelta(days=1)
        t2 = Task(title='future', due_at=future)
        t2.save()
        self.assertFalse(t2.is_overdue_now())

    def test_priority_default_and_choices(self):
        t = Task(title='prio')
        t.save()
        self.assertEqual(t.priority, 'normal')


class TodoViewTestCase(TestCase):
    def test_index_get(self):
        response = self.client.get(
            reverse('index')
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_post(self):
        data = {
            'title': 'Test Task',
            'due_at': '2026-06-24T23:59'
        }

        response = self.client.post(
            reverse('index'),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.get()

        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(
            task.due_at,
            timezone.make_aware(
                datetime(2026, 6, 24, 23, 59)
            )
        )
        self.assertFalse(task.completed)

    def test_index_post_without_due_at(self):
        data = {
            'title': 'Task Without Due Date',
            'due_at': ''
        }

        response = self.client.post(
            reverse('index'),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.get()

        self.assertEqual(
            task.title,
            'Task Without Due Date'
        )
        self.assertIsNone(task.due_at)

    @patch(
        'todo.views.random.choice',
        return_value='宇宙人に会う準備をする'
    )
    def test_index_post_random_task(self, mock_choice):
        data = {
            'action': 'random'
        }

        response = self.client.post(
            reverse('index'),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.get()

        self.assertEqual(
            task.title,
            '宇宙人に会う準備をする'
        )
        self.assertIsNone(task.due_at)

        mock_choice.assert_called_once()

    def test_index_get_order_post(self):
        task1 = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        task2 = Task.objects.create(
            title='task2',
            due_at=timezone.make_aware(
                datetime(2026, 8, 1)
            )
        )

        response = self.client.get(
            reverse('index'),
            {'order': 'post'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/index.html')
        self.assertEqual(
            response.context['tasks'][0],
            task2
        )
        self.assertEqual(
            response.context['tasks'][1],
            task1
        )

    def test_index_get_order_due(self):
        task1 = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        task2 = Task.objects.create(
            title='task2',
            due_at=timezone.make_aware(
                datetime(2026, 8, 1)
            )
        )

        response = self.client.get(
            reverse('index'),
            {'order': 'due'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/index.html')
        self.assertEqual(
            response.context['tasks'][0],
            task1
        )
        self.assertEqual(
            response.context['tasks'][1],
            task2
        )

    def test_detail_get_success(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        response = self.client.get(
            reverse('detail', args=[task.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/detail.html')
        self.assertEqual(
            response.context['task'],
            task
        )

    def test_detail_get_fail(self):
        response = self.client.get(
            reverse('detail', args=[999])
        )

        self.assertEqual(response.status_code, 404)

    def test_update_get_success(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        response = self.client.get(
            reverse('update', args=[task.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/edit.html')
        self.assertEqual(
            response.context['task'],
            task
        )

    def test_update_post_success(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        data = {
            'title': 'Updated Task',
            'due_at': '2026-07-02T12:30'
        }

        response = self.client.post(
            reverse('update', args=[task.pk]),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('detail', args=[task.pk])
        )

        task.refresh_from_db()

        self.assertEqual(
            task.title,
            'Updated Task'
        )
        self.assertEqual(
            task.due_at,
            timezone.make_aware(
                datetime(2026, 7, 2, 12, 30)
            )
        )

    def test_update_post_without_due_at(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        data = {
            'title': 'Updated Task',
            'due_at': ''
        }

        response = self.client.post(
            reverse('update', args=[task.pk]),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('detail', args=[task.pk])
        )

        task.refresh_from_db()

        self.assertEqual(
            task.title,
            'Updated Task'
        )
        self.assertIsNone(task.due_at)

    def test_update_get_fail(self):
        response = self.client.get(
            reverse('update', args=[999])
        )

        self.assertEqual(response.status_code, 404)

    def test_update_post_fail(self):
        data = {
            'title': 'Updated Task',
            'due_at': '2026-07-02T12:30'
        }

        response = self.client.post(
            reverse('update', args=[999]),
            data
        )

        self.assertEqual(response.status_code, 404)

    def test_close_post(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        response = self.client.post(
            reverse('close', args=[task.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('index')
        )

        task.refresh_from_db()

        self.assertTrue(task.completed)

    def test_close_post_fail(self):
        response = self.client.post(
            reverse('close', args=[999])
        )

        self.assertEqual(response.status_code, 404)

    def test_close_get_not_allowed(self):
        task = Task.objects.create(
            title='task1'
        )

        response = self.client.get(
            reverse('close', args=[task.pk])
        )

        self.assertEqual(response.status_code, 405)

        task.refresh_from_db()

        self.assertFalse(task.completed)

    def test_delete_post_success(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(
                datetime(2026, 7, 1)
            )
        )

        response = self.client.post(
            reverse('delete', args=[task.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('index')
        )
        self.assertFalse(
            Task.objects.filter(pk=task.pk).exists()
        )

    def test_delete_post_fail(self):
        response = self.client.post(
            reverse('delete', args=[999])
        )

        self.assertEqual(response.status_code, 404)

    def test_create_with_priority_and_template_output(self):
        client = Client()
        data = {'title': 'Priority Task', 'due_at': '2026-06-24 23:59:59', 'priority': 'high'}
        response = client.post('/', data)

        # after POST the index view renders the list (200)
        self.assertEqual(response.status_code, 200)
        tasks = Task.objects.all()
        self.assertEqual(tasks.count(), 1)
        t = tasks.first()
        self.assertEqual(t.priority, 'high')

        # template should contain the priority class
        response2 = client.get('/')
        self.assertContains(response2, 'priority-high')

    def test_template_shows_overdue_and_completed_classes(self):
        # create overdue task
        past = timezone.now() - timezone.timedelta(days=2)
        overdue = Task(title='overdue', due_at=past)
        overdue.save()

        # create completed task
        done = Task(title='done')
        done.completed = True
        done.save()

        client = Client()
        resp = client.get('/')
        self.assertContains(resp, 'task-overdue')
        self.assertContains(resp, 'task-completed')
    def test_delete_get_not_allowed(self):
        task = Task.objects.create(
            title='task1'
        )

        response = self.client.get(
            reverse('delete', args=[task.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Task.objects.filter(pk=task.pk).exists()
        )
