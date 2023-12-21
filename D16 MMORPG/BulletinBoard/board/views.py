from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import Poster, Response
from .forms import PosterForm, RespondForm, ResponsesFilterForm
from .tasks import respond_send_email, respond_accept_send_email


class Index(ListView):
    model = Poster
    template_name = 'index.html'
    context_object_name = 'posters'


class PosterItem(DetailView):
    model = Poster
    template_name = 'poster_item.html'
    context_object_name = 'poster'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Response.objects.filter(author_id=self.request.user.id).filter(poster_id=self.kwargs.get('pk')):
            context['respond'] = "Откликнулся"
        elif self.request.user == Poster.objects.get(pk=self.kwargs.get('pk')).author:
            context['respond'] = "Мое_объявление"
        return context


class CreatePoster(LoginRequiredMixin, CreateView):
    model = Poster
    template_name = 'create_poster.html'
    form_class = PosterForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm('board.add_poster'):
            return HttpResponseRedirect(reverse('account_profile'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        poster = form.save(commit=False)
        poster.author = User.objects.get(id=self.request.user.id)
        poster.save()
        return redirect(f'/poster/{poster.id}')


class EditPoster(PermissionRequiredMixin, UpdateView):
    permission_required = 'board.change_poster'
    template_name = 'edit_poster.html'
    form_class = PosterForm
    success_url = '/create/'

    def dispatch(self, request, *args, **kwargs):
        author = Poster.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Редактировать объявление может только его автор")

    def get_object(self, **kwargs):
        Id = self.kwargs.get('pk')
        return Poster.objects.get(pk=Id)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/poster/' + str(self.kwargs.get('pk')))


class DeletePoster(PermissionRequiredMixin, DeleteView):
    permission_required = 'board.delete_poster'
    template_name = 'delete_poster.html'
    queryset = Poster.objects.all()
    success_url = '/index'

    def dispatch(self, request, *args, **kwargs):
        author = Poster.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Удалить объявление может только его автор")


title = str("")


class Responses(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'responses.html'
    context_object_name = 'responses'

    def get_context_data(self, **kwargs):
        context = super(Responses, self).get_context_data(**kwargs)
        global title
        if self.kwargs.get('pk') and Poster.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Poster.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = ResponsesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            poster_id = Poster.objects.get(title=title)
            context['filter_responses'] = list(Response.objects.filter(poster_id=poster_id))
            context['response_poster_id'] = poster_id.id
        else:
            context['filter_responses'] = list(Response.objects.filter(poster_id__author_id=self.request.user))
        context['myresponses'] = list(Response.objects.filter(author_id=self.request.user))
        return context

    def poster(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/responses')
        return self.get(request, *args, **kwargs)


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.status = True
        response.save()
        respond_accept_send_email.delay(response_id=response.id)
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.delete()
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


class Respond(LoginRequiredMixin, CreateView):
    model = Response
    template_name = 'respond.html'
    form_class = RespondForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        respond = form.save(commit=False)
        respond.author = User.objects.get(id=self.request.user.id)
        respond.poster = Poster.objects.get(id=self.kwargs.get('pk'))
        respond.save()
        respond_send_email.delay(respond_id=respond.id)
        return redirect(f'/poster/{self.kwargs.get("pk")}')
