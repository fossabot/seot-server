from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from server.forms import AppForm
from server.models.app import App


class AppView:
    @staticmethod
    @transaction.atomic
    @login_required
    def get(request):
        app_list = []
        for app in App.objects.filter(user=request.user):
            app_list.append(app)
        return render(request, 'server/toppage.html', {'app_list': app_list})

    @staticmethod
    @transaction.atomic
    @login_required
    def upload(request):
        if request.method == 'POST':
            form = AppForm(request.POST, request.FILES)
            if form.is_valid():
                app = form.save()
                app.user = request.user
                app.setup_nodes()
                app.save()
                return HttpResponseRedirect(reverse('toppage'))
        else:
            form = AppForm(initial={'user': request.user.username})
        return render(request, 'server/form.html', {'form': form})
