from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import User, Post, FriendRequest, Message
from .forms import PostForm

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    posts = Post.objects.all().order_by('-timestamp')
    return render(request, 'network/index.html', {'posts': posts})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
    return render(request, 'network/login.html')

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        password_confirmation = request.POST["password_confirmation"]

        if password != password_confirmation:
            return render(request, "network/register.html", {
                "message": "كلمات المرور غير متطابقة."
            })

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "اسم المستخدم مستخدم بالفعل."
            })

        login(request, user)
        return redirect("index")

    return render(request, "network/register.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'network/index.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return redirect('index')

@login_required
def users_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'network/users.html', {'users': users})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('users')

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.to_user.friends.add(friend_request.from_user)
    friend_request.from_user.friends.add(friend_request.to_user)
    friend_request.delete()
    return redirect('friend_requests')

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('friend_requests')

@login_required
def friend_requests(request):
    requests = FriendRequest.objects.filter(receiver=request.user)
    return render(request, "network/friend_requests.html", {"requests": requests})

@login_required
def send_message(request, user_id):
    if request.method == "POST":
        receiver = get_object_or_404(User, id=user_id)
        body = request.POST.get("body")
        if body:
            Message.objects.create(sender=request.user, receiver=receiver, body=body)
        return redirect('messages', user_id=user_id)
    return redirect('users')

@login_required
def messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(sender=request.user, receiver=other_user) | Message.objects.filter(sender=other_user, receiver=request.user)
    messages = messages.order_by('timestamp')
    return render(request, 'network/messages.html', {'messages': messages, 'other_user': other_user, 'room_name': f'{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}'})

@login_required
def message_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'network/message_list.html', {'users': users})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileUpdateForm

from django.shortcuts import render, get_object_or_404
from .models import Profile, User

from django.shortcuts import render, get_object_or_404
from .models import Profile, User

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    return render(request, "network/profile.html", {"profile": profile, "user": user})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserUpdateForm

@login_required
def edit_profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', username=request.user.username)  # إعادة التوجيه إلى صفحة البروفايل
    
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'network/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})



from django.shortcuts import render

def splash(request):
    return render(request, 'splash.html')

def users(request):
    return render(request, 'network/users.html')

from django.shortcuts import render
from .models import Video

def videos(request):
    videos = Video.objects.all()
    return render(request, 'network/videos.html', {'videos': videos})

from django.shortcuts import render, redirect
from .models import Video
from .forms import VideoUploadForm

def videos(request):
    videos = Video.objects.all()

    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('videos')  # إعادة توجيه المستخدم بعد رفع الفيديو

    else:
        form = VideoUploadForm()

    return render(request, 'network/videos.html', {'videos': videos, 'form': form})
