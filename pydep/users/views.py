from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView

from .forms import SignInForm
from .forms import SignUpForm
from .mixins import AnonymousRequiredMixin


def safe_next(request, candidate):
    """Вернуть безопасный URL для редиректа после входа, иначе None."""
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return None


def SignIn(request):
    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or ''
    )
    target = safe_next(request, next_url)

    if request.user.is_authenticated:
        return redirect(target or 'lesson:profile')

    if request.method == 'POST':
        form = SignInForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(target or 'lesson:profile')
    else:
        form = SignInForm()
    return render(
        request, 'users/signin.html', {'form': form, 'next': next_url}
    )


class SignUp(AnonymousRequiredMixin, CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('users:signin')
    template_name = 'users/signup.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['next'] = self.request.GET.get('next', '')
        return ctx

    def get_success_url(self):
        # После регистрации ведём на страницу входа, сохраняя next.
        next_url = (
            self.request.GET.get('next')
            or self.request.POST.get('next')
        )
        url = str(self.success_url)
        if next_url:
            url = f"{url}?next={next_url}"
        return url
