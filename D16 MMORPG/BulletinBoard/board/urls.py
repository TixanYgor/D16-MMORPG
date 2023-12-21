from django.urls import path
from django.shortcuts import redirect

from .views import Index, CreatePoster, PosterItem, EditPoster, DeletePoster, Responses, Respond, response_accept, \
  response_delete


urlpatterns = [
  path('index', Index.as_view(), name='index'),
  path('poster/<int:pk>', PosterItem.as_view()),
  path('create_ad', CreatePoster.as_view(), name='create_ad'),
  path('poster/<int:pk>/edit', EditPoster.as_view(), name='edit'),
  path('poster/<int:pk>/delete', DeletePoster.as_view(), name='delete'),
  path('responses', Responses.as_view(), name='responses'),
  path('responses/<int:pk>', Responses.as_view(), name='responses'),
  path('respond/<int:pk>', Respond.as_view(), name='respond'),
  path('response/accept/<int:pk>', response_accept),
  path('response/delete/<int:pk>', response_delete),
  path('', lambda request: redirect('index', permanent=False)),
]
