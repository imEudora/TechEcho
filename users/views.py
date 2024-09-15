import uuid

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render, reverse
from django.utils.http import url_has_allowed_host_and_scheme

from users.forms import UserPhotoForm, UserProfileForm, UsersForm

from .helper import send_forget_password_mail
from .models import PasswordReset, User


def register(request):
    if request.method == "POST":
        form = UsersForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session["new_user"] = True
            messages.success(request, "註冊成功並已自動登入！")
            return redirect("index")
        else:
            if "username" in form.errors:
                messages.error(request, "帳號錯誤")
            if "email" in form.errors:
                messages.error(request, "信箱已註冊過，或格式不正確")
            if "password1" in form.errors:
                messages.error(request, "密碼錯誤")
            if "password2" in form.errors:
                messages.error(request, "密碼不一致")

    else:
        form = UsersForm()
    return render(request, "layouts/register.html", {"form": form})


def log_in(request):
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("index")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        next_url = reverse("index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "登入成功")
            return redirect(next_url)
        else:
            if "username" in form.errors:
                messages.error(request, "帳號錯誤")
            if "password1" in form.errors:
                messages.error(request, "密碼錯誤")
            if "username" and "password1" in form.errors:
                messages.error(request, "登入失敗，帳號密碼錯誤或尚未註冊")
    else:
        form = AuthenticationForm()
    return render(request, "layouts/login.html", {"form": form, "next": next_url})


def log_out(request):
    logout(request)
    messages.success(request, "登出成功")
    return redirect("index")


def forget_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username).first()

        if not user:
            messages.error(request, "找不到此帳號。")
            return redirect("users:forget_password")

        password_reset, created = PasswordReset.objects.get_or_create(user=user)
        password_reset.forget_password_token = uuid.uuid4()
        password_reset.save()

        send_forget_password_mail(user.email, profile.forget_password_token)
        messages.success(request, "重設密碼的郵件已發送。")
    else:
        messages.error(request, "找不到此帳號。")

        return redirect("users:forget_password")

    return render(request, "layouts/forget_password.html")


def change_password(request, token):
    try:
        password_reset = PasswordReset.objects.get(forget_password_token=token)
    except PasswordReset.DoesNotExist:
        messages.error(request, "無效")
        return redirect("users:login")

    user = password_reset.user

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            user.save()

            password_reset.forget_password_token = None
            password_reset.save()

            messages.success(request, "密碼已成功更改，請使用新密碼登入。")
            return redirect("users:login")
        else:
            messages.error(request, "密碼不匹配或為空。")
            return redirect("users:change_password", token=token)

    context = {"token": token, "user_id": user.id}
    return render(request, "layouts/change_password.html", context)


@login_required
def profile(request):
    # context = {"user": request.user}
    form = UserPhotoForm(instance=request.user)
    return render(request, "layouts/profile.html", {"form": form})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "您的個人資料已成功更新。")
            return redirect("users:profile")
        else:
            messages.error(request, "請更正以下錯誤。")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "layouts/profile_edit.html", {"form": form})


@login_required
def upload_profile_picture(request):
    if request.method == "POST":
        form = UserPhotoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            try:
                form.save()  # 儲存用戶表單（包括圖片上傳到S3）
                return redirect("users:profile")
            except (BotoCoreError, ClientError) as e:
                # 打印S3的錯誤信息到伺服器日誌
                logging.error(f"S3 上傳失敗: {e}")
                return render(
                    request,
                    "layouts/upload_picture.html",
                    {"form": form, "error": "上傳照片失敗，請稍後再試。"},
                )
    else:
        form = UserPhotoForm(instance=request.user)

    return render(
        request, "layouts/upload_picture.html", {"form": form, "user": request.user}
    )
