from re import search
from turtle import title
from wsgiref.simple_server import demo_app
from xml.dom import ValidationErr

import django
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView


# redirect to login page whenever the server is restarted
def redirect(request):
    return HttpResponseRedirect("/user/login")



class AuthorisedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class UserLoginView(LoginView):
    template_name = "login.html"
    success_url = "/home/all"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "signup.html"
    success_url = "/user/login"




class TaskCreateForm(ModelForm):

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "priority"]




class GenericTaskDeleteView(AuthorisedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/home/all"


class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"




class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/home/all"

    def form_valid(self, form):
        user = self.request.user
        p = form.cleaned_data["priority"]

        # basic validation
        if p<=0:
            raise ValidationError("Priority cannot be negative")

        # saving all data in variable: "data"
        data = Task.objects.filter(deleted=False, user = user)

        # setting default value for variable: adjust_priority
        adjust_priority = False

        # looping through all tasks to check if priority is already taken
        for el in data:
            if el.priority == p:
                adjust_priority = True
                break
        
        # if priority is already taken, adjust it
        if adjust_priority:
            current = p

            # looping through all tasks to find the next available priority
            for task in data.iterator():
                if task.priority == current:
                    current += 1
                else:
                    break
            
            # looping through it backwards to adjust the priority of tasks
            for i in range(current, p, -1):
                Task.objects.filter(deleted=False, priority=i-1, user=user).update(priority=i)

            # save and redirect
            form.save()
            return HttpResponseRedirect("/home/all")

        else:  # priority is unique
            form.save()
            return HttpResponseRedirect("/home/all")




class GenericTaskCreateView(CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/home/all"

    def form_valid(self, form):
        user = self.request.user
        p = form.cleaned_data["priority"]

        # basic validation
        if p<=0:
            raise ValidationError("Priority cannot be negative")

        # saving all data in variable: "data"
        data = Task.objects.filter(deleted=False, user = user)

        # setting default value for variable: adjust_priority
        adjust_priority = False

        # looping through all tasks to check if priority is already taken
        for el in data:
            if el.priority == p:
                adjust_priority = True
                break
        
        # if priority is already taken, adjust it
        if adjust_priority:
            current = p

            # looping through all tasks to find the next available priority
            for task in data.iterator():
                if task.priority == current:
                    current += 1
                else:
                    break
            
            # looping through it backwards to adjust the priority of tasks
            for i in range(current, p, -1):
                Task.objects.filter(deleted=False, priority=i-1, user=user).update(priority=i)

            # save and redirect
            form.save()
            
            self.object = form.save()
            self.object.user = self.request.user
            self.object.save()
            return HttpResponseRedirect("/home/all")

        else:  # priority is unique
            form.save()
            self.object = form.save()
            self.object.user = self.request.user
            self.object.save()
            return HttpResponseRedirect("/home/all")




# pending tasks
class GenericTaskViewPend(ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "pend.html"
    context_object_name = "tasks"

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted=False, user=self.request.user, completed=False)
        if search_term:
            tasks = Task.objects.filter(title__icontains=search_term)
        return tasks
    
    def get_context_data(self, **kwargs):
        completed = Task.objects.filter(deleted=False, user=self.request.user, completed=True).count()
        total = Task.objects.filter(deleted=False, user=self.request.user).count()
        context = super(ListView, self).get_context_data(**kwargs)
        context['completed'] = completed
        context['total'] = total
        return context

# completed tasks
class GenericTaskViewComp(ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "comp.html"
    context_object_name = "tasks"

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted=False, user=self.request.user, completed=True)
        if search_term:
            tasks = Task.objects.filter(title__icontains=search_term)
        return tasks
    
    def get_context_data(self, **kwargs):
        completed = Task.objects.filter(deleted=False, user=self.request.user, completed=True).count()
        total = Task.objects.filter(deleted=False, user=self.request.user).count()
        context = super(ListView, self).get_context_data(**kwargs)
        context['completed'] = completed
        context['total'] = total
        return context


# all
class GenericTaskViewAll(ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "all.html"
    context_object_name = "tasks"

    
    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted=False, user=self.request.user)
        if search_term:
            tasks = Task.objects.filter(title__icontains=search_term)
        return tasks
    def get_context_data(self, **kwargs):
        completed = Task.objects.filter(deleted=False, user=self.request.user, completed=True).count()
        total = Task.objects.filter(deleted=False, user=self.request.user).count()
        context = super(ListView, self).get_context_data(**kwargs)
        context['completed'] = completed
        context['total'] = total

        return context
