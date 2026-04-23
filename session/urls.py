from django.urls import path
from . import views
from . import cms_views

urlpatterns = [
    path('', views.home, name='session_home'),
    path('create/', views.create_session, name='session_create'),
    path('cms/', cms_views.cms_sessions, name='cms_sessions'),
    path('cms/<str:code>/', cms_views.cms_session_detail, name='cms_session_detail'),
    path('cms/<str:code>/slides/', cms_views.cms_slides, name='cms_slides'),
    path('cms/<str:code>/slides/add/', cms_views.cms_slide_edit, name='cms_slide_add'),
    path('cms/<str:code>/slides/<int:slide_id>/edit/', cms_views.cms_slide_edit, name='cms_slide_edit'),
    path('cms/<str:code>/slides/<int:slide_id>/delete/', cms_views.cms_slide_delete, name='cms_slide_delete'),
    path('cms/<str:code>/slides/reorder/', cms_views.cms_slide_reorder, name='cms_slide_reorder'),
    path('cms/<str:code>/delete/', cms_views.delete_session, name='cms_delete_session'),
    path('cms/<str:code>/export/', cms_views.cms_export, name='cms_export'),
    path('cms/<str:code>/export/csv/', cms_views.cms_export_csv, name='cms_export_csv'),
    path('<str:code>/join/', views.join_session, name='session_join'),
    path('<str:code>/facilitator/', views.facilitator_view, name='session_facilitator'),
    path('<str:code>/', views.participant_view, name='session_participant'),
    path('<str:code>/stream/', views.sse_stream, name='session_stream'),
    path('<str:code>/action/<str:action>/', views.facilitator_action, name='session_action'),
    path('<str:code>/submit/', views.submit_activity, name='session_submit'),
    path('<str:code>/post/', views.submit_post, name='session_post'),
    path('<str:code>/posts/', views.get_posts, name='session_posts'),
    path('<str:code>/leaderboard/', views.get_leaderboard, name='session_leaderboard'),
    path('<str:code>/slide/<int:slide_id>/', views.get_slide_data, name='session_slide_data'),
    path('<str:code>/state/', views.get_session_state, name='session_state'),
]