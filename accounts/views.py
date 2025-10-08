from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
# 导入我们自定义的密码修改表单
from .forms import CustomPasswordChangeForm
from django.contrib.auth.views import LoginView
from django.views import View

from .forms import (
    RegistrationForm,  
    UserUpdateForm,
    ProfileUpdateForm,
    CustomAuthenticationForm
)

class RegisterView(View):
    """
    处理用户注册的视图。
    GET 请求时，显示一个空的注册表单。
    POST 请求时，验证表单数据并创建新用户。
    """
    def get(self, request):
        # 使用正确的表单名称 RegistrationForm
        form = RegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        # 使用正确的表单名称 RegistrationForm
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账户 {username} 创建成功，请登录。')
            return redirect('accounts:login')
        return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    自定义登录视图。
    """
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, '登录成功！')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '登录失败，请检查您的用户名和密码。')
        return super().form_invalid(form)


def logout_view(request):
    """
    处理用户登出。
    """
    logout(request)
    messages.success(request, '您已成功退出登录。')
    return redirect('home')


@login_required
def profile(request):
    """
    用户个人资料页面。
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '您的个人资料已成功更新！')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    """
    修改密码页面。
    """
    if request.method == 'POST':
        # 使用我们自定义的带样式的表单
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '您的密码已成功修改！')
            return redirect('accounts:profile')
        else:
            messages.error(request, '请纠正下面的错误。')
    else:
        # 使用我们自定义的带样式的表单
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})