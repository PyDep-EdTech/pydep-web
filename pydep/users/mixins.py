from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


class AnonymousRequiredMixin:
    """Уже авторизованных уводим на профиль (или на next, если безопасен)."""

    redirect_url = 'lesson:profile'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            nxt = request.GET.get('next')
            if nxt and url_has_allowed_host_and_scheme(
                nxt, allowed_hosts={request.get_host()}
            ):
                return redirect(nxt)
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)
