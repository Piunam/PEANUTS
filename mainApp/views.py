from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from mainApp.models import *
from mainApp.forms import*
from django.contrib import messages
from django.http import JsonResponse
from .models import Player
from .models import Question
import subprocess
import os
import tempfile
import json
from django.http import JsonResponse

@login_required
def home(request):
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        player = Player.objects.create(user=request.user, username=request.user.username)
    
    context = {
        'player': player
    }
    return render(request, 'home.html', context)


@login_required

def profile(request:HttpRequest):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'profile.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})


#registration......................

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user_type = request.POST['user_type']
        

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            print("HI")
            print(user_type)
            new_user = User(username=username, password=password, email=email, user_type=user_type)
            new_user.save()
            return redirect('thank_you')

    return render(request, 'register.html')

#community.........................................................


@login_required
def community_page(request):
    groups = Group.objects.all()
    # return render(request, 'community_page.html', {'groups': groups})
    # Fetch all jobs and achievements to display
    jobs = Job.objects.all()
    achievements = Achievement.objects.all()

    context = {
        'groups': groups,
        'jobs': jobs,
        'achievements': achievements,
    }

    return render(request, 'community_page.html', context)

@login_required
def jobs(request):
    jobs = Job.objects.all()
    context = {
        'jobs': jobs
    }

    return render(request, 'jobs.html', context)

@login_required
def groups(request):
    groups = Group.objects.all()
    context = {
        'groups': groups
    }
    return render(request, 'groups.html', context)

@login_required
def frandz(request):
    return render(request, 'frandz.html')

@login_required
def hackathons(request):
    return render(request, 'hackathons.html')

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('community_page')
    else:
        form = JobForm()
    return render(request, 'post_job.html', {'form': form})

@login_required
def post_achievement(request):
    if request.method == 'POST':
        form = AchievementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('community_page')
    else:
        form = AchievementForm()
    return render(request, 'post_achievement.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.get(username=username, password=password)

        if user:
            if user.user_type == 'hiree':
                # return redirect('hiree_home')
                return redirect('home')
            elif user.user_type == 'hirer':
                return redirect('community_page')
            
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'user_login.html')

def thank_you(request):
    return render(request, 'thank_you.html')


# def community_feed(request):
#     if request.method == 'POST':
#         form = FeedPostForm(request.POST)
#         if form.is_valid():
#             feed_post = form.save(commit=False)
#             if isinstance(request.user, User):
#                 feed_post.user = request.user
#             else:
#                 return HttpResponse("User is not authenticated", status=400)
#             feed_post.save()
#             return redirect('community_feed')
#     else:
#         form = FeedPostForm()

#     posts = FeedPost.objects.all().order_by('-timestamp')
#     context = {
#         'form': form,
#         'posts': posts,
#     }
#     return render(request, 'community_feed.html', context)

@login_required
def community_feed(request):
    # groups = Group.objects.all()
    # jobs = Job.objects.all()
    achievements = Achievement.objects.all()

    context = {
        # 'groups': groups,
        # 'jobs': jobs,
        'achievements': achievements,
    }

    return render(request, 'community_feed.html', context)




@login_required
def aboutus(request):
    return render(request, 'aboutus.html')

@login_required
def promoted(request):
    return render(request, 'Promoted.html')
@login_required
def demoted(request):
    return render(request, 'Demote.html')



@login_required
def store(request):
    return render(request, 'store.html')




first_click = None

@csrf_exempt
def submit_view(request):
    global first_click
    if first_click is None:
        first_click = request.user
        return JsonResponse({'status': 'promoted'})
    else:
        return JsonResponse({'status': 'demoted'})



@csrf_exempt
@login_required
def start_match(request):
    if request.method == 'POST':
        user = request.user
        player, created = Player.objects.get_or_create(user=user)

        # Fetch the player's rank
        player_rank = player.rank

        # Find an available room that isn't occupied and matches the player's rank
        room = Room.objects.filter(is_occupied=False).first()

        if not room:
            # Create a new room if no available room is found
            room = Room.objects.create(name=f"Room-{Room.objects.count() + 1}")
            print("New Room created :)", room.id)

        # Assign player to room
        room.current_players += 1
        player.room = room
        player.is_in_queue = True
        player.save()
        room.save()

        # Check if room is full and mark it as occupied
        if room.current_players >= room.max_capacity:
            room.is_occupied = True
            room.save()

        # Get opponent player information (if available)
        opponent = Player.objects.filter(room=room).exclude(user=user).first()

        return JsonResponse({
            'status': 'success',
            'room_id': room.id,
            'room_name': room.name,
            'opponent_username': opponent.username if opponent else None,
            'player_username': player.username
        })

    

@csrf_exempt
def check_room_status(request):
    if request.method == 'POST':
        user = request.user
        player = Player.objects.get(user=user)

        if player.room and player.room.current_players >= 2:
            opponent = Player.objects.filter(room=player.room).exclude(user=user).first()
            return JsonResponse({
                'player_username': player.username,
                'status': 'ready',
                'redirect_url': f'/question-page/?room_id={player.room.id}',
                'opponent_username': opponent.username if opponent else None,
            })
        else:
            return JsonResponse({'status': 'waiting'})


@login_required
def question_page(request):
    room_id = request.GET.get('room_id')
    
    # Ensure that room_id is provided
    if not room_id:
        return redirect('home')  # Redirect to home or an error page if no room_id is provided
    
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found'}, status=404)
    
    player, created = Player.objects.get_or_create(user=request.user)
    
    context = {
        'room_id': room.id,
        'player': player
    }
    return render(request, 'game/question_page.html', context)
# views.py
def get_question(request, question_id):
    questions = {
     "easy": [
            {
                "title": "Two Sum",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\nYou can return the answer in any order.",
                "difficulty": "Easy",
                "examples": [
                    "Input: nums = [2,7,11,15], target = 9\nOutput: [0, 1]\nExplanation: Because nums[0] + nums[1] == 9, we return [0, 1].",
                    "Input: nums = [3,2,4], target = 6\nOutput: [1, 2]",
                    "Input: nums = [3,3], target = 6\nOutput: [0, 1]"
                ],
                "time_limit": 20 * 60  # 20 minutes
            }
        ],
        "medium": [
            {
                "title": "Add Two Numbers",
                "description": "You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.\nYou may assume the two numbers do not contain any leading zero, except the number 0 itself.",
                "difficulty": "Medium",
                "examples": [
                    "Input: l1 = [2,4,3], l2 = [5,6,4]\nOutput: [7,0,8]\nExplanation: 342 + 465 = 807."
                ],
                "time_limit": 40 * 60  # 40 minutes
            }
        ],
    "hard": [
        {
            "title": "Median of Two Sorted Arrays",
            "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
            "difficulty": "Hard",
            "examples": [
                "Input: nums1 = [1,3], nums2 = [2]\nOutput: 2.00000\nExplanation: merged array = [1,2,3] and median is 2."
            ],
            "time_limit": 60 * 60  # 60 minutes
        }
       
    ]
}


    question = questions.get(question_id, None)
    if question:
        return JsonResponse(question)
    else:
        return JsonResponse({'error': 'Question not found'}, status=404)


@csrf_exempt
def submit_answer(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
        
        user = request.user
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Player does not exist'}, status=404)
        
        # Assume the answer was correct (this needs actual answer validation)
        answer_correct = True  # Replace with actual validation

        if answer_correct:

            # Promotion logic
            current_rank = player.rank
            if current_rank != 'Bronze - 4':  # Example highest rank
                next_rank = get_next_rank(current_rank)
                player.rank = next_rank
                player.save()

                # Find the opponent player
                opponent = Player.objects.filter(room=player.room).exclude(user=user).first()
                if opponent:
                    # Demotion logic
                    opponent_rank = opponent.rank
                    if opponent_rank != 'Bronze - 1':  # Example base rank
                        new_rank = get_previous_rank(opponent_rank)
                        opponent.rank = new_rank
                        opponent.save()
                        print(player,new_rank)
        
            return JsonResponse({'status': 'success', 'message': 'Submitted successfully. Rank updated.'})
           
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect answer.'})
        


@csrf_exempt
def compile_code(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        code = data.get('code')
        lang = data.get('lang')
        input_data = data.get('input', '')

        if lang == 'python':
            file_extension = '.py'
            command = ['python3']
        elif lang == 'javascript':
            file_extension = '.js'
            command = ['node']
        elif lang == 'java':
            file_extension = '.java'
            command = ['javac']
        elif lang == 'cpp':
            file_extension = '.cpp'
            command = ['g++', '-o', 'output']
        else:
            return JsonResponse({'output': 'Unsupported language'}, status=400)

        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as source_file:
            source_file.write(code.encode('utf-8'))
            source_file_path = source_file.name

        try:
            if lang == 'cpp':
                compile_process = subprocess.run(command + [source_file_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return JsonResponse({'output': compile_process.stderr}, status=400)
                execute_process = subprocess.run(['./output'], input=input_data, capture_output=True, text=True)
            elif lang == 'java':
                compile_process = subprocess.run(command + [source_file_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return JsonResponse({'output': compile_process.stderr}, status=400)
                execute_process = subprocess.run(['java', source_file_path.replace(file_extension, '')], input=input_data, capture_output=True, text=True)
            else:
                execute_process = subprocess.run(command + [source_file_path], input=input_data, capture_output=True, text=True)

            output = execute_process.stdout
            error = execute_process.stderr
            result = output if output else error
            return JsonResponse({'output': result.strip()})

        finally:
            os.remove(source_file_path)
            if lang == 'cpp':
                os.remove('output')
            elif lang == 'java':
                os.remove(source_file_path.replace(file_extension, '.class'))

    return JsonResponse({'output': 'Invalid request method'}, status=405)

from django.shortcuts import render

def quick_play(request):
    return render(request, 'quick_play.html')

def save_custom_timer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        custom_time = data.get('custom_time')
        # Save custom_time to the database or session if needed
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def submit_code(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        user_code = request.POST.get('user_code')

        question = get_object_or_404(Question, pk=question_id)

        # Assuming you're compiling the code using subprocess
        # This is just an example for Python code, adapt as necessary for other languages
        try:
            # Execute the user's code
            exec_output = subprocess.check_output(['python3', '-c', user_code], stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e:
            exec_output = e.output.decode('utf-8')

        # Compare output with the expected output
        if exec_output.strip() == question.expected_output.strip():
            return JsonResponse({'status': 'success', 'message': 'Success, answer is accepted!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Not matched'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@csrf_exempt
def handle_match_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        player_id = data.get('player_id')
        result = data.get('result')  # 'success' or 'failure'

        try:
            player = Player.objects.get(id=player_id)
            
            if result == 'success':
                player.rank = get_next_rank(player.rank)
                message = "Congratulations! You have been promoted to the next rank."
            elif result == 'failure':
                player.rank = get_previous_rank(player.rank)
                message = "You have been demoted to the previous rank. Better luck next time."

            player.save()
            return JsonResponse({'message': message, 'new_rank': player.rank})

        except Player.DoesNotExist:
            return JsonResponse({'error': 'Player not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_next_rank(current_rank):
    ranks = ['Bronze - 1', 'Bronze - 2', 'Bronze - 3', 'Bronze - 4', 
             'Silver - 1', 'Silver - 2', 'Silver - 3', 'Silver - 4', 
             'Gold - 1', 'Gold - 2', 'Gold - 3', 'Gold - 4', 
             'Platinum - 1', 'Platinum - 2', 'Platinum - 3', 'Platinum - 4', 
             'Diamond - 1', 'Diamond - 2', 'Diamond - 3', 'Diamond - 4', 
             'Master - 1', 'Master - 2', 'Master - 3', 'Master - 4', 
             'Grandmaster - 1', 'Grandmaster - 2', 'Grandmaster - 3', 'Grandmaster - 4', 
             'Champion']
    
    if current_rank in ranks:
        idx = ranks.index(current_rank)
        if idx < len(ranks) - 1:
            return ranks[idx + 1]
    return current_rank

def get_previous_rank(current_rank):
    ranks = ['Bronze - 1', 'Bronze - 2', 'Bronze - 3', 'Bronze - 4', 
             'Silver - 1', 'Silver - 2', 'Silver - 3', 'Silver - 4', 
             'Gold - 1', 'Gold - 2', 'Gold - 3', 'Gold - 4', 
             'Platinum - 1', 'Platinum - 2', 'Platinum - 3', 'Platinum - 4', 
             'Diamond - 1', 'Diamond - 2', 'Diamond - 3', 'Diamond - 4', 
             'Master - 1', 'Master - 2', 'Master - 3', 'Master - 4', 
             'Grandmaster - 1', 'Grandmaster - 2', 'Grandmaster - 3', 'Grandmaster - 4', 
             'Champion']
    
    if current_rank in ranks:
        idx = ranks.index(current_rank)
        if idx > 0:
            return ranks[idx - 1]
    return current_rank

# Global variable to keep track of who clicked first
first_click = None

@csrf_exempt
def submit_view(request):
    global first_click
    if first_click is None:
        first_click = request.user
        return JsonResponse({'status': 'promoted'})
    else:
        return JsonResponse({'status': 'demoted'})

@csrf_exempt
@login_required
def quick_play(request):
    if request.method == 'POST':
        user = request.user
        player, created = Player.objects.get_or_create(user=user)

        # Fetch the player's rank
        player_rank = player.rank

        # Find an available room that isn't occupied
        room = Room.objects.filter(is_occupied=False).first()

        if not room:
            # Create a new room if no available room is found
            room = Room.objects.create(name=f"Room-{Room.objects.count() + 1}")
            print("New Room created :)", room.id)

        # Assign player to room
        room.current_players += 1
        player.room = room
        player.is_in_queue = True
        player.save()
        room.save()

        # Mark the room as occupied for quick play
        room.is_occupied = True
        room.save()

        # For quick play, we don't need to wait for another player
        # Treat it as a match against an AI or a solo match
        opponent_username = "AI Opponent"  # Placeholder for the opponent

        return JsonResponse({
            'status': 'success',
            'room_id': room.id,
            'room_name': room.name,
            'opponent_username': opponent_username,
            'player_username': player.username,
            'redirect_url': f'/quick-play-question-page/?room_id={player.room.id}'
        })
    

@login_required
def quick_play_question_page(request):
    room_id = request.GET.get('room_id')
    
    # Ensure that room_id is provided
    if not room_id:
        return redirect('home')  # Redirect to home or an error page if no room_id is provided
    
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found'}, status=404)
    
    player, created = Player.objects.get_or_create(user=request.user)
    
    context = {
        'room_id': room.id,
        'player': player
    }
    return render(request, 'game/quick_play_question_page.html', context)
