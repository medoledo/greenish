import json
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from .models import Session, Slide, Participant, Badge, ActivityResult, AnonymousPost


@never_cache
def home(request):
    owned_session = request.session.get('owned_session')
    if owned_session:
        try:
            Session.objects.get(code=owned_session)
        except Session.DoesNotExist:
            del request.session['owned_session']
            owned_session = None
    return render(request, 'session/home.html', {'owned_session': owned_session})


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def create_session(request):
    owned_session_code = request.session.get('owned_session')
    if owned_session_code:
        try:
            Session.objects.get(code=owned_session_code)
            return redirect('cms_slides', code=owned_session_code)
        except Session.DoesNotExist:
            del request.session['owned_session']

    if request.method == 'POST':
        title = request.POST.get('title', 'Greenish Session')
        facilitator_name = request.user.get_full_name() or request.user.username
        session = Session.objects.create(
            title=title,
            facilitator_name=facilitator_name,
            facilitator_password='facilitator',
        )
        request.session[f'facilitator_{session.code}'] = session.id
        request.session['owned_session'] = session.code
        return redirect('cms_slides', code=session.code)
    return render(request, 'session/create.html')


@never_cache
def facilitator_login(request, code):
    session = get_object_or_404(Session, code=code)
    if request.method == 'POST':
        password = request.POST.get('facilitator_password', '')
        if password == session.facilitator_password:
            request.session[f'facilitator_{code}'] = session.id
            request.session['owned_session'] = code
            return redirect('session_facilitator', code=code)
        return render(request, 'session/facilitator_login.html', {'session': session, 'error': 'Incorrect password'})
    return render(request, 'session/facilitator_login.html', {'session': session})


def facilitator_logout(request, code):
    if f'facilitator_{code}' in request.session:
        del request.session[f'facilitator_{code}']
    if 'owned_session' in request.session:
        del request.session['owned_session']
    return redirect('session_home')


@never_cache
def facilitator_view(request, code):
    session = get_object_or_404(Session, code=code)
    if request.session.get(f'facilitator_{code}') != session.id:
        if request.user.is_authenticated and request.user.is_staff:
            request.session[f'facilitator_{code}'] = session.id
            request.session['owned_session'] = code
        else:
            return redirect('session_facilitator_login', code=code)
    slides = list(session.slides.filter(is_active=True).order_by('order'))
    participants = session.participants.all().order_by('-total_points')
    total_slides = len(slides)
    current_index = session.current_slide_index
    context = {
        'session': session,
        'slides': slides,
        'current_slide': slides[current_index] if current_index < total_slides else None,
        'current_index': current_index,
        'total_slides': total_slides,
        'participants': participants,
        'participant_count': participants.count(),
    }
    return render(request, 'session/facilitator.html', context)


@never_cache
def participant_view(request, code):
    session = get_object_or_404(Session, code=code)
    participant_id = request.session.get('participant_id')
    participant = None
    if participant_id:
        try:
            participant = Participant.objects.get(id=participant_id, session=session)
        except Participant.DoesNotExist:
            participant = None
    if not participant:
        return redirect('session_join', code=code)
    slides = list(session.slides.filter(is_active=True).order_by('order'))
    total_slides = len(slides)
    current_index = session.current_slide_index
    context = {
        'session': session,
        'slides': slides,
        'current_slide': slides[current_index] if current_index < total_slides else None,
        'current_index': current_index,
        'total_slides': total_slides,
        'participant': participant,
    }
    return render(request, 'session/participant.html', context)


@never_cache
def join_session(request, code):
    session = get_object_or_404(Session, code=code)
    if session.status == 'ended':
        return render(request, 'session/join_ended.html', {'session': session})
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        avatar = request.POST.get('avatar', '\U0001f331')
        if not name:
            return render(request, 'session/join.html', {'session': session, 'error': 'Please enter your name', 'avatar_choices': settings.AVATAR_CHOICES})
        participant, created = Participant.objects.get_or_create(
            session=session,
            name=name,
            defaults={'avatar': avatar, 'phone': phone}
        )
        if not created:
            participant.avatar = avatar
            participant.phone = phone
            participant.save()
        request.session['participant_id'] = participant.id
        request.session['session_code'] = code
        request.session.modified = True
        return redirect('session_participant', code=session.code)
    return render(request, 'session/join.html', {'session': session, 'avatar_choices': settings.AVATAR_CHOICES})


def sse_stream(request, code):
    session = get_object_or_404(Session, code=code)

    def get_slide_data(slide):
        return {
            'id': slide.id,
            'title': slide.title,
            'content': slide.content,
            'slide_type': slide.slide_type,
            'activity_type': slide.activity_type or '',
            'activity_config': slide.activity_config,
            'shocking_fact': slide.shocking_fact,
            'image_url': slide.image.url if slide.image else None,
        }

    def event_stream():
        session.refresh_from_db()
        last_index = session.current_slide_index
        last_activity = session.activity_active
        last_status = session.status
        last_result_count = ActivityResult.objects.filter(session=session).count()
        last_show_answers = cache.get(f'show_answers_{code}', 0)
        last_participant_count = session.participants.count()
        while True:
            session.refresh_from_db()
            current_index = session.current_slide_index
            activity_active = session.activity_active
            current_status = session.status
            current_result_count = ActivityResult.objects.filter(session=session).count()
            current_show_answers = cache.get(f'show_answers_{code}', 0)
            current_participant_count = session.participants.count()

            slides = list(session.slides.filter(is_active=True).order_by('order'))
            total_slides = len(slides)
            current_slide = slides[current_index] if current_index < total_slides else None

            if current_index != last_index:
                data = json.dumps({
                    'slide_index': current_index,
                    'total_slides': total_slides,
                    'slide': get_slide_data(current_slide) if current_slide else None,
                })
                yield f"event: slide_change\ndata: {data}\n\n"
                last_index = current_index

            if activity_active != last_activity:
                data = json.dumps({'activity_active': activity_active})
                yield f"event: activity_toggle\ndata: {data}\n\n"
                last_activity = activity_active

            if current_status != last_status:
                data = json.dumps({'status': current_status})
                yield f"event: session_status\ndata: {data}\n\n"
                last_status = current_status

            if current_result_count != last_result_count:
                data = json.dumps({'result_count': current_result_count})
                yield f"event: activity_result\ndata: {data}\n\n"
                last_result_count = current_result_count

            if current_show_answers != last_show_answers:
                data = json.dumps({'timestamp': current_show_answers})
                yield f"event: show_answers\ndata: {data}\n\n"
                last_show_answers = current_show_answers

            if current_participant_count != last_participant_count:
                participants_list = []
                for p in session.participants.all().order_by('-total_points'):
                    participants_list.append({
                        'id': p.id,
                        'name': p.name,
                        'avatar': p.avatar,
                        'phone': p.phone,
                        'total_points': p.total_points,
                        'streak': p.streak,
                        'joined_at': p.joined_at.isoformat() if p.joined_at else None,
                    })
                data = json.dumps({
                    'count': current_participant_count,
                    'participants': participants_list,
                })
                yield f"event: participant_change\ndata: {data}\n\n"
                last_participant_count = current_participant_count

            yield ": hb\n\n"
            time.sleep(0.3)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@require_POST
def facilitator_action(request, code, action):
    session = get_object_or_404(Session, code=code)
    total_slides = session.slides.filter(is_active=True).count()

    if action == 'next':
        if session.current_slide_index < total_slides - 1:
            session.current_slide_index += 1
            session.save()
            cache.delete(f'show_answers_{code}')
    elif action == 'prev':
        if session.current_slide_index > 0:
            session.current_slide_index -= 1
            session.save()
            cache.delete(f'show_answers_{code}')
    elif action == 'goto':
        index = int(request.POST.get('index', 0))
        if 0 <= index < total_slides:
            session.current_slide_index = index
            session.save()
            cache.delete(f'show_answers_{code}')
    elif action == 'start_activity':
        session.activity_active = True
        session.save()
    elif action == 'stop_activity':
        session.activity_active = False
        session.save()
        cache.delete(f'show_answers_{code}')
    elif action == 'end_session':
        session.status = 'ended'
        session.activity_active = False
        session.save()
    elif action == 'start_session':
        session.status = 'active'
        session.save()
    elif action == 'restart_session':
        session.status = 'active'
        session.current_slide_index = 0
        session.activity_active = False
        session.save()
        ActivityResult.objects.filter(session=session).delete()
        AnonymousPost.objects.filter(session=session).delete()
        session.participants.all().delete()
        cache.delete(f'show_answers_{code}')
    elif action == 'show_answers':
        cache.set(f'show_answers_{code}', time.time(), timeout=300)

    return JsonResponse({
        'success': True,
        'slide_index': session.current_slide_index,
        'activity_active': session.activity_active,
        'status': session.status,
    })


@require_POST
def kick_participant(request, code, participant_id):
    session = get_object_or_404(Session, code=code)
    if request.session.get(f'facilitator_{code}') != session.id:
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    participant = get_object_or_404(Participant, id=participant_id, session=session)
    participant.delete()
    return JsonResponse({'success': True})


@require_POST
@csrf_exempt
def submit_activity(request, code):
    session = get_object_or_404(Session, code=code)
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    participant = get_object_or_404(Participant, id=participant_id, session=session)
    data = json.loads(request.body)
    slide_id = data.get('slide_id')
    activity_type = data.get('activity_type')
    answer = data.get('answer', '')
    is_correct = data.get('is_correct', None)
    points_earned = data.get('points_earned', 0)

    if is_correct and not points_earned:
        points_earned = 10
    if is_correct:
        participant.streak += 1
        if participant.streak >= 3:
            points_earned += 5
    else:
        participant.streak = 0

    participant.max_streak = max(participant.max_streak, participant.streak)
    participant.total_points += points_earned
    participant.save()

    slide = get_object_or_404(Slide, id=slide_id)
    result = ActivityResult.objects.create(
        session=session,
        participant=participant,
        slide=slide,
        activity_type=activity_type,
        answer=str(answer),
        is_correct=is_correct,
        points_earned=points_earned,
    )
    check_and_award_badges(participant, activity_type)

    return JsonResponse({
        'success': True,
        'points_earned': points_earned,
        'total_points': participant.total_points,
        'streak': participant.streak,
        'badges': list(participant.badges.values_list('icon', flat=True)),
    })


@require_POST
@csrf_exempt
def submit_post(request, code):
    session = get_object_or_404(Session, code=code)
    participant_id = request.session.get('participant_id')
    participant = None
    if participant_id:
        try:
            participant = Participant.objects.get(id=participant_id, session=session)
        except Participant.DoesNotExist:
            pass
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    slide_id = data.get('slide_id')
    if not content:
        return JsonResponse({'success': False, 'error': 'Empty content'}, status=400)
    slide = None
    if slide_id:
        slide = Slide.objects.filter(id=slide_id).first()
    post = AnonymousPost.objects.create(
        session=session,
        slide=slide,
        participant=participant,
        content=content,
        is_public=True,
    )
    if participant:
        activity_type = slide.activity_type if slide and slide.activity_type else 'discuss'
        result = ActivityResult.objects.create(
            session=session,
            participant=participant,
            slide=slide,
            activity_type=activity_type,
            answer=content,
            is_correct=True,
            points_earned=5,
        )
        participant.total_points += 5
        participant.save()
        check_and_award_badges(participant, activity_type)
    return JsonResponse({
        'success': True,
        'post_id': post.id,
        'content': post.content,
        'avatar': participant.avatar if participant else '\U0001f331',
    })


@require_GET
@never_cache
def get_posts(request, code):
    session = get_object_or_404(Session, code=code)
    slide_id = request.GET.get('slide_id')
    posts = session.posts.select_related('participant').filter(is_public=True)
    if slide_id:
        posts = posts.filter(slide_id=slide_id)
    posts_list = [{
        'id': p.id,
        'content': p.content,
        'avatar': p.participant.avatar if p.participant else '\U0001f331',
        'name': p.participant.name if p.participant else 'Anonymous',
        'created_at': p.created_at.strftime('%H:%M'),
    } for p in posts.order_by('-created_at')[:50]]
    return JsonResponse({'posts': posts_list})


@require_GET
@never_cache
def get_leaderboard(request, code):
    session = get_object_or_404(Session, code=code)
    participants = session.participants.prefetch_related('badges').order_by('-total_points')[:20]
    leaderboard = [{
        'id': p.id,
        'name': p.name,
        'avatar': p.avatar,
        'points': p.total_points,
        'streak': p.streak,
        'badges': list(p.badges.values_list('icon', flat=True)),
        'phone': p.phone,
        'joined_at': p.joined_at.isoformat() if p.joined_at else None,
    } for p in participants]
    return JsonResponse({'leaderboard': leaderboard})


@require_GET
@never_cache
def get_activity_stats(request, code):
    session = get_object_or_404(Session, code=code)
    current_index = session.current_slide_index
    slides = list(session.slides.filter(is_active=True).order_by('order'))
    current_slide = slides[current_index] if current_index < len(slides) else None
    total_participants = session.participants.count()

    stats = {
        'total': total_participants,
        'submitted': 0,
        'correct': None,
        'avg_points': 0,
        'posts': [],
        'submitted_users': [],
        'not_submitted_users': [],
    }

    if current_slide:
        results = ActivityResult.objects.filter(session=session, slide=current_slide).select_related('participant')
        stats['submitted'] = results.count()
        correct_count = results.filter(is_correct=True).count()
        stats['correct'] = correct_count if correct_count > 0 else 0
        if results.exists():
            from django.db.models import Avg
            stats['avg_points'] = round(results.aggregate(Avg('points_earned'))['points_earned__avg'] or 0)

        # Get submitted and not-submitted users
        submitted_ids = set(results.values_list('participant_id', flat=True))
        all_participants = session.participants.all().order_by('-total_points')
        stats['submitted_users'] = [
            {'id': p.id, 'name': p.name, 'avatar': p.avatar, 'points': p.total_points}
            for p in all_participants if p.id in submitted_ids
        ]
        stats['not_submitted_users'] = [
            {'id': p.id, 'name': p.name, 'avatar': p.avatar, 'points': p.total_points}
            for p in all_participants if p.id not in submitted_ids
        ]

        if current_slide.activity_type in ('commitment', 'discuss', 'commit'):
            posts = session.posts.filter(slide=current_slide, is_public=True).order_by('-created_at')[:50]
            stats['posts'] = [{
                'name': p.participant.name if p.participant else 'Anonymous',
                'avatar': p.participant.avatar if p.participant else '🌱',
                'content': p.content,
            } for p in posts]

    return JsonResponse(stats)


@require_GET
@never_cache
def get_slide_data(request, code, slide_id):
    session = get_object_or_404(Session, code=code)
    slide = get_object_or_404(Slide, id=slide_id, session=session)
    data = {
        'id': slide.id,
        'title': slide.title,
        'content': slide.content,
        'slide_type': slide.slide_type,
        'activity_type': slide.activity_type,
        'activity_config': slide.activity_config,
        'shocking_fact': slide.shocking_fact,
        'image': slide.image.url if slide.image else None,
    }
    return JsonResponse(data)


@require_GET
@never_cache
def get_activity_answers(request, code):
    session = get_object_or_404(Session, code=code)
    current_index = session.current_slide_index
    slides = list(session.slides.filter(is_active=True).order_by('order'))
    current_slide = slides[current_index] if current_index < len(slides) else None
    results = []
    if current_slide:
        activity_results = ActivityResult.objects.filter(
            session=session, slide=current_slide
        ).select_related('participant').order_by('-submitted_at')
        for r in activity_results:
            answer_display = r.answer
            try:
                parsed = json.loads(r.answer)
                if isinstance(parsed, dict):
                    answer_display = ', '.join(f'{k}: {v}' for k, v in parsed.items())
                elif isinstance(parsed, list):
                    answer_display = ', '.join(str(v) for v in parsed)
            except (json.JSONDecodeError, TypeError):
                pass
            results.append({
                'participant_name': r.participant.name if r.participant else 'Unknown',
                'participant_avatar': r.participant.avatar if r.participant else '🌱',
                'activity_type': r.activity_type,
                'answer': answer_display,
                'raw_answer': r.answer,
                'is_correct': r.is_correct,
                'points_earned': r.points_earned,
                'submitted_at': r.submitted_at.strftime('%H:%M:%S') if r.submitted_at else '',
            })
    return JsonResponse({'answers': results, 'slide_title': current_slide.title if current_slide else '', 'activity_type': current_slide.activity_type if current_slide else ''})


@require_GET
@never_cache
def check_participant(request, code):
    session = get_object_or_404(Session, code=code)
    participant_id = request.session.get('participant_id')
    is_valid = False
    if participant_id:
        try:
            Participant.objects.get(id=participant_id, session=session)
            is_valid = True
        except Participant.DoesNotExist:
            pass
    return JsonResponse({'valid': is_valid, 'status': session.status})


@require_GET
@never_cache
def get_session_state(request, code):
    session = get_object_or_404(Session, code=code)
    slides = list(session.slides.filter(is_active=True).order_by('order'))
    current_index = session.current_slide_index
    current_slide = slides[current_index] if current_index < len(slides) else None
    return JsonResponse({
        'slide_index': current_index,
        'total_slides': len(slides),
        'activity_active': session.activity_active,
        'status': session.status,
        'current_slide': {
            'id': current_slide.id,
            'title': current_slide.title,
            'content': current_slide.content,
            'slide_type': current_slide.slide_type,
            'activity_type': current_slide.activity_type,
            'activity_config': current_slide.activity_config,
            'shocking_fact': current_slide.shocking_fact,
            'image': current_slide.image.url if current_slide.image else None,
        } if current_slide else None,
        'participant_count': session.participants.count(),
    })


ACTIVITY_BADGES = {
    'sprint': {'name': 'Sorting Star', 'icon': '♻️', 'desc': 'Completed waste sorting sprint!'},
    'decompose': {'name': 'Time Keeper', 'icon': '⏳', 'desc': 'Mastered decomposition times!'},
    'quiz': {'name': 'Planet Protector', 'icon': '🌍', 'desc': 'Aced the plastic quiz!'},
    'sort_stats': {'name': 'Fact Checker', 'icon': '📊', 'desc': 'Sorted the stats like a pro!'},
    'commitment': {'name': 'Green Warrior', 'icon': '💚', 'desc': 'Made a green commitment!'},
    'discuss': {'name': 'Wave Maker', 'icon': '🌊', 'desc': 'Participated in discussion!'},
    'commit': {'name': 'Commitment Keeper', 'icon': '💪', 'desc': 'Made a commitment!'},
}


def check_and_award_badges(participant, activity_type=None):
    badges_to_award = []
    total_points = participant.total_points
    total_results = participant.results.count()
    correct_results = participant.results.filter(is_correct=True).count()
    discuss_count = participant.results.filter(activity_type__in=('discuss', 'commit')).count()

    if correct_results >= 1:
        badge, _ = Badge.objects.get_or_create(
            name='First Bloom',
            trigger_type='count',
            trigger_value=1,
            defaults={'description': 'First correct answer', 'icon': '🌱'}
        )
        badges_to_award.append(badge)
    if participant.max_streak >= 3 or participant.streak >= 3:
        badge, _ = Badge.objects.get_or_create(
            name='On Fire',
            trigger_type='streak',
            trigger_value=3,
            defaults={'description': '3 correct answers in a row', 'icon': '🔥'}
        )
        badges_to_award.append(badge)
    if correct_results >= 5:
        badge, _ = Badge.objects.get_or_create(
            name='Sorting Pro',
            trigger_type='count',
            trigger_value=5,
            defaults={'description': '5 correct answers', 'icon': '🏆'}
        )
        badges_to_award.append(badge)
    if discuss_count >= 1:
        badge, _ = Badge.objects.get_or_create(
            name='Community Voice',
            trigger_type='activity',
            trigger_value=1,
            defaults={'description': 'Shared in community discussion', 'icon': '💬'}
        )
        badges_to_award.append(badge)

    # Activity-specific badge
    if activity_type and activity_type in ACTIVITY_BADGES:
        info = ACTIVITY_BADGES[activity_type]
        badge, _ = Badge.objects.get_or_create(
            name=info['name'],
            trigger_type='activity',
            trigger_value=1,
            defaults={'description': info['desc'], 'icon': info['icon']}
        )
        badges_to_award.append(badge)

    for badge in badges_to_award:
        participant.badges.add(badge)