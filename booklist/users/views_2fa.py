"""
Two-Factor Authentication views for the users app.
Handles email-based 2FA using django-otp.
"""

import logging

from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django_otp import login as otp_login
from django_otp.plugins.otp_email.models import EmailDevice

logger = logging.getLogger(__name__)


# Session access helpers for async views
def get_session_value(request, key, default=None):
    """Synchronous helper to get session value."""
    return request.session.get(key, default)


def set_session_values(request, **kwargs):
    """Synchronous helper to set multiple session values."""
    for key, value in kwargs.items():
        request.session[key] = value


def pop_session_value(request, key, default=None):
    """Synchronous helper to pop session value."""
    return request.session.pop(key, default)


def get_or_create_email_device(user):
    """Get or create an email device for the user."""
    try:
        device = EmailDevice.objects.get(user=user, name="primary")
    except EmailDevice.DoesNotExist:
        device = EmailDevice.objects.create(
            user=user,
            name="primary",
            email=user.email,
            confirmed=True,  # Auto-confirm for email devices
        )
    return device


@require_POST
@csrf_protect
async def send_2fa_code(request):
    """Send a 2FA code to the user's email."""
    username = request.POST.get("username")
    password = request.POST.get("password")

    if not username or not password:
        return HttpResponse(
            await sync_to_async(render_to_string)(
                "users/login_form.html",
                {"error": "Username and password are required."},
                request=request,
            )
        )

    # Import here to avoid circular imports
    from django.contrib.auth import authenticate

    aauthenticate = sync_to_async(authenticate)
    user = await aauthenticate(request, username=username, password=password)

    if user is not None:
        user_email = user.email  # type: ignore
        user_email = user.email  # type: ignore
        if not user_email:
            return HttpResponse(
                await sync_to_async(render_to_string)(
                    "users/login_form.html",
                    {"error": "No email address on file. Please contact support."},
                    request=request,
                )
            )

        # Store user ID in session for verification step
        await sync_to_async(set_session_values)(
            request, pending_user_id=user.pk, fa_required=True  # Use pk instead of id
        )

        # Get or create email device
        device = await sync_to_async(get_or_create_email_device)(user)

        try:
            # Generate and send the token
            await sync_to_async(device.generate_challenge)()

            # Return the 2FA code entry form
            html = await sync_to_async(render_to_string)(
                "users/2fa_code_form.html",
                {"email": user_email},
                request=request,
            )
            return HttpResponse(html)

        except Exception as e:
            logger.error(f"Failed to send 2FA code to {user_email}: {e}")
            return HttpResponse(
                await sync_to_async(render_to_string)(
                    "users/login_form.html",
                    {"error": "Failed to send verification code. Please try again."},
                    request=request,
                )
            )
    else:
        # Invalid credentials
        html = await sync_to_async(render_to_string)(
            "users/login_form.html",
            {"error": "Invalid username or password."},
            request=request,
        )
        return HttpResponse(html)


@require_POST
@csrf_protect
async def verify_2fa_code(request):
    """Verify the 2FA code and complete login."""
    code = request.POST.get("code", "").strip()
    pending_user_id = await sync_to_async(get_session_value)(request, "pending_user_id")

    if not pending_user_id:
        return HttpResponse(
            await sync_to_async(render_to_string)(
                "users/login_form.html",
                {"error": "Session expired. Please log in again."},
                request=request,
            )
        )

    if not code:
        return HttpResponse(
            await sync_to_async(render_to_string)(
                "users/2fa_code_form.html",
                {"error": "Please enter the verification code.", "show_resend": True},
                request=request,
            )
        )

    try:
        from django.contrib.auth.models import User

        user = await sync_to_async(User.objects.get)(pk=pending_user_id)
        device = await sync_to_async(get_or_create_email_device)(user)

        # Verify the token
        if await sync_to_async(device.verify_token)(code):
            # Token is valid - complete the login
            await sync_to_async(django_login)(request, user)
            await sync_to_async(otp_login)(request, device)

            # Clean up session
            await sync_to_async(pop_session_value)(request, "pending_user_id")
            await sync_to_async(pop_session_value)(request, "2fa_required")

            # Return updated navbar
            html = await sync_to_async(render_to_string)(
                "users/navbar_user_section.html", {"user": user}, request=request
            )

            response = HttpResponse(html)
            response["HX-Trigger"] = "loginSuccess"
            response["HX-Retarget"] = "#user-section"
            response["HX-Reswap"] = "outerHTML"
            return response
        else:
            # Invalid token
            return HttpResponse(
                await sync_to_async(render_to_string)(
                    "users/2fa_code_form.html",
                    {
                        "error": "Invalid verification code. Please try again.",
                        "show_resend": True,
                    },
                    request=request,
                )
            )

    except Exception as e:
        logger.error(f"Error during 2FA verification: {e}")
        return HttpResponse(
            await sync_to_async(render_to_string)(
                "users/login_form.html",
                {"error": "An error occurred. Please try again."},
                request=request,
            )
        )


@login_required
async def setup_2fa(request):
    """Setup page for 2FA - allows users to update their 2FA email address."""
    user = request.user

    try:
        device = await sync_to_async(EmailDevice.objects.get)(user=user, name="primary")
        has_2fa = True
        current_email = device.email
    except EmailDevice.DoesNotExist:
        # This shouldn't happen with mandatory 2FA, but handle it gracefully
        device = await sync_to_async(get_or_create_email_device)(user)
        has_2fa = True
        current_email = device.email

    context = {
        "has_2fa": has_2fa,
        "user_email": user.email,
        "current_2fa_email": current_email,
        "device": device,
    }

    if request.method == "POST":
        new_email = request.POST.get("new_email", "").strip()

        if not new_email:
            await sync_to_async(messages.error)(
                request, "Please enter a valid email address."
            )
        elif new_email == current_email:
            await sync_to_async(messages.info)(
                request, "The new email address is the same as the current one."
            )
        else:
            # Update the email device with the new email
            device.email = new_email
            await sync_to_async(device.save)()

            # Also update the user's email if they want
            if request.POST.get("update_account_email") == "on":
                user.email = new_email
                await sync_to_async(user.save)()

            await sync_to_async(messages.success)(
                request, f"Your 2FA email has been updated to {new_email}."
            )
            context["current_2fa_email"] = new_email
            context["user_email"] = user.email

    return await sync_to_async(render)(request, "users/2fa_setup.html", context)


@login_required
@require_POST
async def update_2fa_email(request):
    """Update the 2FA email address for the current user."""
    new_email = request.POST.get("new_email", "").strip()
    update_account = request.POST.get("update_account_email") == "on"

    if not new_email:
        await sync_to_async(messages.error)(
            request, "Please enter a valid email address."
        )
        return redirect("users:2fa:setup")

    try:
        device = await sync_to_async(EmailDevice.objects.get)(
            user=request.user, name="primary"
        )

        # Update the 2FA device email
        device.email = new_email
        await sync_to_async(device.save)()

        # Update user account email if requested
        if update_account:
            request.user.email = new_email
            await sync_to_async(request.user.save)()

        await sync_to_async(messages.success)(
            request, f"Your 2FA email has been updated to {new_email}."
        )

    except EmailDevice.DoesNotExist:
        await sync_to_async(messages.error)(
            request, "2FA device not found. Please contact support."
        )

    return redirect("users:2fa:setup")
