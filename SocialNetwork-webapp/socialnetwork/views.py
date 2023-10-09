from __future__ import unicode_literals
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.utils import timezone
import time # for adding sleep calls to demonstrate concurrency issues
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
# Import all classes
from socialnetwork.models import *
# Import class: CreatePost EditPost
from socialnetwork.posts_decoration import CreatePost, EditPost
# import all forms
from socialnetwork.forms import *
import json
from django.conf import settings
from datetime import datetime, timedelta

import openai
from socialnetwork.sentiment_analysis import *
from socialnetwork.emotion_recog import *

@ensure_csrf_cookie
@login_required
def global_stream(request):
    context = {}
    return render(request, 'socialnetwork/global_stream.html', context)


@login_required
# by clicking the username, one can visit the homepage of that user
def someone_profile(request):
    context = {}
    if not 'created_by' in request.GET:
        message = "Sorry, this user doesn't exist."
        context['message'] = message
        return render(request, 'socialnetwork/someone_not_exist.html', context)

    user_being_viewed = request.GET['created_by']
    # Here, we use request.user.username instead of request.user
    # Since the former is a string, the latter is an object
    if user_being_viewed == request.user.username:
        return myProfile(request)

    context['user_being_viewed'] = user_being_viewed
    this_user = Profile.objects.filter(user__username=user_being_viewed)
    if not this_user:
        context['message'] = 'Sorry, this user doesn\'t exist.'
        return render(request, 'socialnetwork/someone_not_exist.html', context)
    this_user = list(this_user)[0]
    # A is logged in, A is looking at B's profile

    its_posts = Post.objects.filter(created_by__username = this_user.user.username)
    context['user_being_viewed']  = this_user
    print(type(this_user))
    context['its_posts'] = its_posts.order_by("-creation_time")
    context['items'] = Profile.objects.filter(user=this_user.user)
    return render(request, 'socialnetwork/someone_profile.html', context)


def someone_not_exist(request):
    context = {}
    context['message'] = 'Sorry, some error occurs.'
    return render(request, 'socialnetwork/someone_not_exist.html', context)
    
def loginPage(request):
    return render(request, 'socialnetwork/login.html', {})

@transaction.atomic
def register(request):
    context = {}

    # If it is a GET method, then just display the registration form.
    # Some doubt here.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form
    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    # Logs in the new user and redirects to his/her todo list
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('home'))

@login_required
@transaction.atomic
def add_comment(request):
    if request.method != 'POST':
        raise Http404

    current_item_id = request.POST['current_post_id']
    if not request.POST['this_post'] or 'this_post' not in request.POST:
        message = 'You must enter an item to add.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    current_post = Post.objects.get(id=current_item_id)

    new_comment = Comment(
        content=request.POST['this_post'],
        created_by=request.user,
        creation_time=timezone.now(),
        post=current_post,
        created_by_username=request.user.username)
    new_comment.save()

    current_post.num_comments = len(current_post.comments.all())
    current_post.save()

    response_comments = serializers.serialize('json', Comment.objects.all())
    data = {'comments'  :   response_comments, 
            'num_comments': current_post.num_comments,
            'post_id': current_item_id}
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@transaction.atomic
def add_post(request):
    errors = []
    if 'post' not in request.POST or not request.POST['post']:
        errors.append('You must enter something.')
    else:
        new_post = Post(title=request.POST['title'],
                        content=request.POST['post'],
                        created_by=request.user,
                        creation_time=timezone.now(),
                        created_by_username=request.user.username,
                        num_relates = 0,
                        num_hugs = 0,
                        num_comments = 0)
        new_post.save()
        new_post.created_by_identity = new_post.id
        new_post.save()

    posts = Post.objects.all().order_by("-creation_time")

    p = Profile.objects.get(user=request.user)
    p.growth_points += 50
    p.save()

    context = {'posts': posts, 'errors': errors}
    return render(request, 'socialnetwork/global_stream.html', context)

@login_required
def get_list_json(request):

    response_posts = serializers.serialize('json', Post.objects.all())
    response_comments = serializers.serialize('json', Comment.objects.all())

    data = {'posts'     :   response_posts,
            'comments'  :   response_comments,
            }
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def myProfile(request):
    context = {}
    # So use request.user.profile instead of request.user
    context['posts'] = Post.objects.filter(created_by=request.user)
    context['items'] = Profile.objects.filter(user=request.user)
    
    p = Profile.objects.get(user=request.user)
    try:
        most_recent = Post.objects.filter(created_by = request.user).latest("creation_time")

        if timezone.now() - most_recent.creation_time > timedelta(days = 1):
            p.streak = 1
        elif 'streak' not in request.session:
            p.streak += 1
        p.save()
    except:
        print("no posts were found")

    request.session['streak'] = 1
    request.session.set_expiry(86400)

    return render(request, 'socialnetwork/myProfile.html', context)

@login_required
@transaction.atomic
def relate(request):
    if request.method != 'POST':
        raise Http404
    
    if not request.POST['current_post_id'] or 'current_post_id' not in request.POST:
        message = 'error.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    current_item_id = request.POST['current_post_id']
    current_post = Post.objects.get(id=current_item_id)

    try:
        test_relate = current_post.relates.all().get(user=request.user)
        test_relate.delete()
    except:
        new_relate = Relate(post=current_post, user=request.user)
        new_relate.save()
        
    current_post.num_relates = len(current_post.relates.all())
    current_post.save()

    data = {'num_relates': current_post.num_relates,
            'post_id': current_item_id}

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@transaction.atomic
def hug(request):
    if request.method != 'POST':
        raise Http404
    
    if not request.POST['current_post_id'] or 'current_post_id' not in request.POST:
        message = 'error.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    current_item_id = request.POST['current_post_id']
    current_post = Post.objects.get(id=current_item_id)

    try:
        test_hug = current_post.hugs.all().get(user=request.user)
        test_hug.delete()
    except:
        new_hug = Hug(post=current_post, user=request.user)
        new_hug.save()
        
    current_post.num_hugs = len(current_post.hugs.all())
    current_post.save()

    data = {'num_relates': current_post.num_hugs,
            'post_id': current_item_id}

    return HttpResponse(json.dumps(data), content_type='application/json')

@ensure_csrf_cookie
@login_required
def start_chat(request):   
    context = {}
    if 'conversation_history' in request.session:
        del request.session['conversation_history']
        print("cleared conversation history")
    if 'promptAnswers' in request.session:
        del request.session['promptAnswers']
        print("cleared prompt answers")

    conversation_history = []
    promptAnswers = []
    system_msg = "friendly, approachable, and supportive"
    conversation_history.append({"role":"system", "content":system_msg})

    openai.api_key = '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'

    initial_query = 'Hello please guide me in making a journal entry and ask me questions to help me think. Lets start with you exactly repeating the following phrase and nothing else:"Would you like to make a journal entry?""'
    initial_answer = 'Would you like to make a journal entry?'

    promptAnswers.append(f"Person A: {initial_answer}\n")

    conversation_history.append({"role":"user","content":initial_query})
    conversation_history.append({"role": "assistant", "content": initial_answer})

    request.session['conversation_history'] = conversation_history
    request.session['promptAnswers'] = promptAnswers

    return render(request, 'socialnetwork/chatbot.html', context)


@login_required
@transaction.atomic
def chat(request):
    if request.method != 'POST':
        raise Http404

    query = request.POST['message']
    if not request.POST['message'] or 'message' not in request.POST:
        message = 'You must enter an item to add.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    # Fetch the conversation history from the session
    conversation_history = request.session.get('conversation_history', [])
    promptAnswers = request.session.get('promptAnswers', [])

    # Initialize the OpenAI client with your API key
    openai.api_key = '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'

    if query == "finish":
        chatLogs = "\n".join(promptAnswers)
        journalPrompt = "Generate a journal entry from the point of view of Person B without mentioning Person A given the following chat logs."
        conversation_history.append({"role": "assistant","content":journalPrompt + chatLogs })
    else:
        # Add the new query to the conversation history
        score = get_sentiment(query)
        emotion = classify_emotion(query)
        #if the emotion and sentiment do not match
        if(   ((emotion =='anger' or emotion == 'sadness') and score >= .2)
        or ((emotion =='joy' or emotion == 'love') and score <= -.2)):
            #disregard the ai
            #something more complex here
            score = 0
            emotion = ''
        else:   
            #do something with the data
            sentence = f"Please keep in mind that I am feeling {emotion}"
            query += sentence
            print(sentence)
        conversation_history.append({"role": "user", "content": query})
            
    print("sending response")

    # Call the API with the ChatCompletion endpoint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # adjust the model as per your requirements
        messages=conversation_history
    )
    print("got response")
        
    # Extract the answer
    answer = response['choices'][0]['message']['content']

    # Add the model's answer to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})
    promptAnswers.append(f"Person B:{query}\n Person A: {answer}\n")

    request.session['conversation_history'] = conversation_history
    request.session['promptAnswers'] = promptAnswers

    data = {"answer": answer}

    return HttpResponse(json.dumps(data), content_type='application/json')

