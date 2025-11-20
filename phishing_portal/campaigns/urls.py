from django.urls import path
from . import views, views_export

app_name = "campaigns"

urlpatterns = [
    path("templates/", views.template_list, name="template_list"),
    path("templates/new/", views.template_create, name="template_create"),
    path("", views.campaign_list, name="campaign_list"),
    path("new/", views.campaign_create, name="campaign_create"),
    path("<int:pk>/", views.campaign_detail, name="campaign_detail"),
    path("<int:pk>/upload-recipients/", views.upload_recipients, name="upload_recipients"),
    path("<int:pk>/send/", views.send_campaign, name="send_campaign"),
    path("<int:pk>/export-recipients/", views_export.export_campaign_recipients, name="export_recipients"),
    path("<int:pk>/export-events/", views_export.export_campaign_events, name="export_events"),
    path("t/<uuid:tracking_id>/open/", views.track_open, name="track_open"),
    path("t/<uuid:tracking_id>/click/", views.track_click, name="track_click"),
    path("t/<uuid:tracking_id>/report/", views.track_report, name="track_report"),
    path("l/<uuid:tracking_id>/", views.landing_page, name="landing_page"),
    path("inbox/", views.inbox, name="inbox"),
    path("inbox/<int:pk>/", views.inbox_detail, name="inbox_detail"),
    # Blog routes for all roles
    path("<str:role>/blog/", views.blog_list, name="blog_list"),
    path("<str:role>/blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    # Viewer notes
    path("viewer/notes/", views.viewer_notes_board, name="viewer_notes_board"),
    path("viewer/notes/<int:note_id>/toggle/", views.viewer_note_toggle, name="viewer_note_toggle"),
]

