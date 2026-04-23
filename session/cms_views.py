from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from .models import Session, Slide


@never_cache
def cms_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('cms_sessions')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            next_url = request.GET.get('next', '/session/cms/')
            return redirect(next_url)
        return render(request, 'session/cms_login.html', {'error': 'Invalid username or password'})
    return render(request, 'session/cms_login.html')


@never_cache
def cms_logout(request):
    auth_logout(request)
    return redirect('cms_login')


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def cms_sessions(request):
    sessions = Session.objects.all().order_by('-created_at')
    owned_code = request.session.get('owned_session')
    if owned_code:
        try:
            Session.objects.get(code=owned_code)
        except Session.DoesNotExist:
            owned_code = None
    return render(request, 'session/cms/sessions.html', {'sessions': sessions, 'owned_session': owned_code})


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def cms_session_detail(request, code):
    session = get_object_or_404(Session, code=code)
    return render(request, 'session/cms/session_detail.html', {'session': session})


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def cms_slides(request, code):
    session = get_object_or_404(Session, code=code)
    slides = session.slides.all().order_by('order')
    return render(request, 'session/cms/slides.html', {'session': session, 'slides': slides})


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def cms_slide_edit(request, code, slide_id=None):
    session = get_object_or_404(Session, code=code)
    slide = None
    if slide_id:
        slide = get_object_or_404(Slide, id=slide_id, session=session)

    if request.method == 'POST':
        data = request.POST
        slide_type = data.get('slide_type', 'info')
        activity_type = data.get('activity_type', '') or None
        title = data.get('title', '')
        content = data.get('content', '')
        shocking_fact = data.get('shocking_fact') == 'on'
        time_hint = data.get('time_hint') or None
        order = int(data.get('order', 0))

        TEMPLATE_ACTIVITY_TYPES = ['sprint', 'decompose', 'quiz', 'commitment', 'sort_stats']
        activity_config = None
        if slide_type == 'activity' and activity_type:
            if activity_type in TEMPLATE_ACTIVITY_TYPES:
                activity_config = {'template': activity_type}
            else:
                config = {}
                if activity_type == 'poll':
                    config['question'] = data.get('poll_question', '')
                    config['options'] = [opt.strip() for opt in data.get('poll_options', '').split(',') if opt.strip()]
                    correct_str = data.get('poll_correct', '')
                    config['correct'] = int(correct_str) if correct_str.isdigit() else None
                elif activity_type == 'guess':
                    config['question'] = data.get('guess_question', '')
                    config['item'] = data.get('guess_item', '')
                    config['options'] = [opt.strip() for opt in data.get('guess_options', '').split(',') if opt.strip()]
                    config['correct'] = data.get('guess_correct', '')
                elif activity_type == 'discuss':
                    config['prompt'] = data.get('discuss_prompt', '')
                    config['max_chars'] = int(data.get('discuss_max_chars', 280))
                elif activity_type == 'match':
                    config['pairs'] = []
                    pair_count = int(data.get('match_pair_count', 0))
                    for i in range(pair_count):
                        term = data.get(f'match_term_{i}', '')
                        definition = data.get(f'match_definition_{i}', '')
                        if term and definition:
                            config['pairs'].append({'term': term, 'definition': definition})
                activity_config = config if config else None

        image = request.FILES.get('image')
        if slide:
            slide.slide_type = slide_type
            slide.title = title
            slide.content = content
            slide.activity_type = activity_type
            slide.activity_config = activity_config
            slide.shocking_fact = shocking_fact
            slide.time_hint = int(time_hint) if time_hint else None
            slide.order = order
            if image:
                slide.image = image
            slide.save()
        else:
            slide = Slide.objects.create(
                session=session,
                slide_type=slide_type,
                title=title,
                content=content,
                activity_type=activity_type,
                activity_config=activity_config,
                shocking_fact=shocking_fact,
                time_hint=int(time_hint) if time_hint else None,
                order=order,
                image=image or None,
            )
        return redirect('cms_slides', code=session.code)

    activity_types = Slide.ACTIVITY_TYPE_CHOICES
    return render(request, 'session/cms/slide_edit.html', {
        'session': session,
        'slide': slide,
        'activity_types': activity_types,
    })


@require_POST
@staff_member_required(login_url='/session/cms/login/')
def cms_slide_reorder(request, code):
    session = get_object_or_404(Session, code=code)
    import json
    data = json.loads(request.body)
    order_list = data.get('order', [])
    for i, slide_id in enumerate(order_list):
        Slide.objects.filter(id=slide_id, session=session).update(order=i)
    return JsonResponse({'success': True})


@staff_member_required(login_url='/session/cms/login/')
def cms_slide_delete(request, code, slide_id):
    session = get_object_or_404(Session, code=code)
    slide = get_object_or_404(Slide, id=slide_id, session=session)
    slide.delete()
    return redirect('cms_slides', code=session.code)


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def cms_export(request, code):
    session = get_object_or_404(Session, code=code)
    import json
    from django.http import HttpResponse

    slides = session.slides.all().order_by('order')
    results = session.results.all().select_related('participant', 'slide')
    posts = session.posts.all().select_related('participant')

    data = {
        'session': {
            'code': session.code,
            'title': session.title,
            'facilitator': session.facilitator_name,
            'status': session.status,
            'created_at': str(session.created_at),
        },
        'participants': [
            {
                'name': p.name,
                'avatar': p.avatar,
                'points': p.total_points,
                'streak': p.streak,
                'badges': list(p.badges.values_list('name', flat=True)),
            }
            for p in session.participants.all()
        ],
        'slides': [
            {
                'order': s.order,
                'type': s.slide_type,
                'title': s.title,
                'activity_type': s.activity_type,
            }
            for s in slides
        ],
        'results': [
            {
                'participant': r.participant.name,
                'activity_type': r.activity_type,
                'answer': r.answer,
                'is_correct': r.is_correct,
                'points': r.points_earned,
            }
            for r in results
        ],
        'posts': [
            {
                'author': p.participant.name if p.participant else 'Anonymous',
                'content': p.content,
            }
            for p in posts
        ],
    }

    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{session.code}_export.json"'
    return response


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def cms_export_csv(request, code):
    import csv
    session = get_object_or_404(Session, code=code)
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{session.code}_results.csv"'

    writer = csv.writer(response)
    writer.writerow(['Participant', 'Activity Type', 'Answer', 'Correct', 'Points', 'Submitted At'])

    for result in session.results.all().select_related('participant').order_by('-submitted_at'):
        writer.writerow([
            result.participant.name,
            result.activity_type,
            result.answer,
            result.is_correct,
            result.points_earned,
            result.submitted_at.strftime('%Y-%m-%d %H:%M'),
        ])

    writer.writerow([])
    writer.writerow(['--- Commitments & Discussion Posts ---'])
    writer.writerow(['Author', 'Type', 'Content', 'Created At'])
    for post in session.posts.all().select_related('participant').order_by('-created_at'):
        writer.writerow([
            post.participant.name if post.participant else 'Anonymous',
            'Post',
            post.content,
            post.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response


@never_cache
@staff_member_required(login_url='/session/cms/login/')
def delete_session(request, code):
    session = get_object_or_404(Session, code=code)
    if request.method == 'POST':
        if request.session.get('owned_session') == code:
            del request.session['owned_session']
        session.delete()
        return redirect('cms_sessions')
    return redirect('cms_session_detail', code=code)