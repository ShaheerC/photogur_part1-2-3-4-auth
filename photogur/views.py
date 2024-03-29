from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from photogur.models import *
from photogur.forms import *


def pictures_root(request):
    return HttpResponseRedirect("/pictures")

def pictures_html(request):
    context = { 'pictures': Picture.objects.all() }
    response = render(request, 'pictures.html', context)
    return HttpResponse(response)

def picture_show(request, id):
    picture = Picture.objects.get(pk=id)
    context = {'picture': picture}
    return render(request, 'picture.html', context)

def picture_search(request):
    query = request.GET['query']
    search_results = Picture.objects.filter(artist=query)
    context = {'pictures': search_results, 'query': query}
    return render(request, 'search.html', context)

@login_required
def create_comment(request):
    picture_id = request.POST['picture']
    picture = Picture.objects.filter(id=picture_id)[0]
    name = request.POST['name']
    comment = request.POST['comment']
    new_comment = Comment(name=name, message=comment, picture=picture)
    new_comment.save()
    return HttpResponseRedirect(f'/pictures/{picture_id}')

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/pictures')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            user = authenticate(username=username, password=pw)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/pictures')
            else:
                form.add_error('username', 'Login failed')
    else:
        form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/pictures')

def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/pictures')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect('/pictures')
    else:
        form = UserCreationForm()
    html_response = render(request, 'signup.html', {'form': form})
    return HttpResponse(html_response)

@login_required
def new_picture(request):
    form = PictureForm()
    context = {"form": form, "message": 'Upload new picture', "action": "/pictures/create"}
    return render(request, 'pictureform.html', context)

@login_required
def create_picture(request):
    form = PictureForm(request.POST)
    if form.is_valid():
        picture = form.save(commit=False)
        picture.user = request.user
        picture.save()
        return HttpResponseRedirect("/pictures")
    else:
        context = {"form": form}
        return render(request, 'pictureform.html', context)

@login_required
def edit_picture(request, id):
    picture = get_object_or_404(Picture, pk=id, user=request.user.pk)
    if request.method == 'POST':
        form = PictureForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            artist = form.cleaned_data.get('artist')
            url = form.cleaned_data.get('url')
            picture.title = title
            picture.artist = artist
            picture.url = url
            picture.save()
            return HttpResponseRedirect('/pictures')
    form = PictureForm(request.POST)
    context = {'picture': picture, 'form': form}
    return HttpResponse(render(request, 'edit.html', context))