from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')


"""
Funcion que se encarga de implementar el formulario y manejarlo
Manejo de errores y si el registro es correcto te redirecciona a la vista de tareas
Se crea la cookie con una expiracion de un año
"""
def signup(request):
    if request.method == 'GET':
        return render(request, "signup.html",{
        'form': UserCreationForm,
    }) 
    else:
        #print(f'{request.POST['username']} - {request.POST["password1"]}')
        #Si las contraseñas coinciden creamos el usuario
        if request.POST['password1'] == request.POST["password2"]:
            try:
                #Registramos el usuario
                user = User.objects.create_user(username = request.POST['username'], password=request.POST["password1"])    
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                 return render(request, "signup.html",{
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                 })
        return render(request, "signup.html",{
                    'form': UserCreationForm,
                    'error': 'Las contraseñas no coinciden'
                 })
    
@login_required
def tasks(request):
    #Hacemos un filtro de tal manera que nos la tarea sobre el usuario que esta realizando la peticion y tambien que si la fecha realización es false.
    #tasks = Task.objects.filter(user=request.user, datecompleted__isnull = False)
    #Filtro para mostrar aquellas tareas que no estan completadas
    tasks = Task.objects.filter(user = request.user, datecompleted__isnull = True)
    tasksCompleted = Task.objects.filter(user = request.user, datecompleted__isnull = False)
    #tasks = Task.objects.all()
    return render(request, 'tasks.html',{
        "tasks":tasks,
        "tasksCompleted":tasksCompleted
    })

@login_required
def task_details(request, task_id):
    if request.method=="GET":
        task = get_object_or_404(Task, pk=task_id)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html',{
            "task":task,
            "form": form,
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html',{
            "task":task,
            "form": form,
            "error": "Error modificando la tarea"
        }) 

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user = request.user)
    if request.method == "POST":
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
    
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id = task_id, user = request.user)
    if request.method=="POST":
        task.delete()
        return redirect('tasks')
    
def exit(request):
    #Tenemos que gestionar que se realizar el logout eliminando la cookie creada
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            "form": AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST["password"])
        if user is None:
            return render(request, 'signin.html', {
                "form": AuthenticationForm,
                "error": "Usuario o contraseñas incorrectos"
            })
        else:
            login(request, user)
            response = redirect('tasks')
            response.set_cookie('cookieUser',request.POST['username'] , max_age=10)
            
            return response
    
@login_required
def createTask(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            "form": TaskForm()
        })
    else:
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasks')
            except ValueError:
                return render(request, 'create_task.html', {
                    "form": form,
                    "error": "Error en la inserción de datos"
                })
        else:
            return render(request, 'create_task.html', {
                "form": form,
                "error": "Datos inválidos"
            })
            
