from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import EmailRequiredUserCreationForm

# Create async versions of auth functions
aauthenticate = sync_to_async(authenticate)
alogin = sync_to_async(login)
alogout = sync_to_async(logout)


# Session access helpers for async views
def set_session_values(request, **kwargs):
    """Synchronous helper to set multiple session values."""
    for key, value in kwargs.items():
        request.session[key] = value


async def login_view(request):
    """Handle login form submission via HTMX - now includes 2FA flow"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = await aauthenticate(request, username=username, password=password)
        if user is not None:
            # Check if user account is active (email verified)
            if not user.is_active:
                html = await sync_to_async(render_to_string)(
                    "users/login_form.html",
                    {
                        "error": "Please verify your email address before logging in. Check your email for the verification code."
                    },
                    request=request,
                )
                return HttpResponse(html)

            # Check if user has 2FA enabled (all users should have it after registration)
            from django_otp.plugins.otp_email.models import EmailDevice

            try:
                device = await sync_to_async(EmailDevice.objects.get)(
                    user=user, name="primary"
                )
                # 2FA is enabled, redirect to 2FA flow
                from .views_2fa import send_2fa_code

                return await send_2fa_code(request)
            except EmailDevice.DoesNotExist:
                # This shouldn't happen with new registration flow, but handle legacy users
                await alogin(request, user)
                # Return updated navbar partial - target the entire user section
                html = await sync_to_async(render_to_string)(
                    "users/navbar_user_section.html", {"user": user}, request=request
                )

                # Use HTMX to trigger a page refresh after successful login
                response = HttpResponse(html)
                response["HX-Trigger"] = "loginSuccess"
                response["HX-Retarget"] = "#user-section"
                response["HX-Reswap"] = "outerHTML"
                return response
        else:
            # Return just the form content with error message
            html = await sync_to_async(render_to_string)(
                "users/login_form.html",
                {"error": "Invalid username or password."},
                request=request,
            )
            return HttpResponse(html)

    return HttpResponse("")


async def logout_view(request):
    """Handle logout"""
    await alogout(request)
    # Return updated navbar partial - user should now be anonymous
    html = await sync_to_async(render_to_string)(
        "users/navbar_user_section.html",
        {"user": request.user},  # After logout, this will be AnonymousUser
        request=request,
    )

    response = HttpResponse(html)
    response["HX-Trigger"] = "logoutSuccess"
    return response


async def register_view(request):
    """Handle user registration with mandatory email verification"""
    if request.method == "POST":
        form = EmailRequiredUserCreationForm(request.POST)
        if await sync_to_async(form.is_valid)():
            # Save user as inactive
            user = await sync_to_async(form.save)(commit=True)

            # Store user info in session for email verification
            await sync_to_async(set_session_values)(
                request,
                pending_verification_user_id=user.pk,  # Use pk instead of id
                pending_verification_email=user.email,
            )

            # Redirect to email verification step
            from .views_email_verification import send_verification_email

            return await send_verification_email(request)
    else:
        form = EmailRequiredUserCreationForm()

    return await sync_to_async(render)(request, "users/register.html", {"form": form})


async def login_form_partial(request):
    """Return just the login form partial for HTMX"""
    return await sync_to_async(render)(request, "users/login_form.html")
