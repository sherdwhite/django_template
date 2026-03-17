"""
Email verification views for user registration.
Handles sending and verifying email codes during the registration process.
"""

import logging
import secrets

from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django_otp import login as otp_login
from django_otp.plugins.otp_email.models import EmailDevice

logger = logging.getLogger(__name__)


def generate_verification_code():
    """Generate a 6-digit verification code."""
    return f"{secrets.randbelow(900000) + 100000:06d}"


def get_or_create_email_device_for_verification(user):
    """Get or create an email device for email verification during registration."""
    try:
        device = EmailDevice.objects.get(user=user, name="primary")
    except EmailDevice.DoesNotExist:
        device = EmailDevice.objects.create(
            user=user,
            name="primary",
            email=user.email,
            confirmed=False,  # Will be confirmed after email verification
        )
    return device


# Session access helpers for async views
def get_session_value(request, key, default=None):
    """Synchronous helper to get session value."""
    return request.session.get(key, default)


def set_session_value(request, key, value):
    """Synchronous helper to set session value."""
    request.session[key] = value


def pop_session_value(request, key, default=None):
    """Synchronous helper to pop session value."""
    return request.session.pop(key, default)


@require_POST
@csrf_protect
async def send_verification_email(request):
    """Send email verification code during registration."""
    user_id = await sync_to_async(get_session_value)(
        request, "pending_verification_user_id"
    )

    if not user_id:
        await sync_to_async(messages.error)(
            request, "Registration session expired. Please register again."
        )
        return redirect("users:register")

    try:
        user = await sync_to_async(User.objects.get)(id=user_id)

        # Get or create email device for this user
        device = await sync_to_async(get_or_create_email_device_for_verification)(user)

        # Generate and send verification code
        await sync_to_async(device.generate_challenge)()

        # Render the verification form
        context = {
            "email": user.email,
            "user_id": user_id,  # Use the user_id from session instead of user.id
        }

        return await sync_to_async(render)(
            request, "users/email_verification.html", context
        )

    except User.DoesNotExist:
        await sync_to_async(messages.error)(
            request, "Invalid registration session. Please register again."
        )
        return redirect("users:register")
    except Exception as e:
        logger.error(f"Failed to send verification email to user {user_id}: {e}")
        await sync_to_async(messages.error)(
            request, "Failed to send verification email. Please try again."
        )
        return redirect("users:register")


@require_POST
@csrf_protect
async def verify_email_code(request):
    """Verify the email code and activate the user account."""
    code = request.POST.get("code", "").strip()
    user_id = await sync_to_async(get_session_value)(
        request, "pending_verification_user_id"
    )

    if not user_id:
        await sync_to_async(messages.error)(
            request, "Registration session expired. Please register again."
        )
        return redirect("users:register")

    if not code:
        await sync_to_async(messages.error)(
            request, "Please enter the verification code."
        )
        pending_email = await sync_to_async(get_session_value)(
            request, "pending_verification_email", ""
        )
        context = {"email": pending_email, "user_id": user_id}
        return await sync_to_async(render)(
            request, "users/email_verification.html", context
        )

    try:
        user = await sync_to_async(User.objects.get)(id=user_id)
        device = await sync_to_async(get_or_create_email_device_for_verification)(user)

        # Verify the token
        if await sync_to_async(device.verify_token)(code):
            # Token is valid - activate the user and complete registration
            user.is_active = True
            await sync_to_async(user.save)()

            # Mark the email device as confirmed
            device.confirmed = True
            await sync_to_async(device.save)()

            # Log the user in
            await sync_to_async(django_login)(request, user)
            await sync_to_async(otp_login)(request, device)

            # Clean up session
            await sync_to_async(pop_session_value)(
                request, "pending_verification_user_id"
            )
            await sync_to_async(pop_session_value)(
                request, "pending_verification_email"
            )

            await sync_to_async(messages.success)(
                request,
                f"Welcome! Your account has been verified and 2FA is now enabled.",
            )
            return redirect("index")
        else:
            # Invalid token
            await sync_to_async(messages.error)(
                request, "Invalid verification code. Please try again."
            )
            context = {"email": user.email, "user_id": user_id, "show_resend": True}
            return await sync_to_async(render)(
                request, "users/email_verification.html", context
            )

    except User.DoesNotExist:
        await sync_to_async(messages.error)(
            request, "Invalid registration session. Please register again."
        )
        return redirect("users:register")
    except Exception as e:
        logger.error(f"Error during email verification for user {user_id}: {e}")
        await sync_to_async(messages.error)(
            request, "An error occurred during verification. Please try again."
        )
        pending_email = await sync_to_async(get_session_value)(
            request, "pending_verification_email", ""
        )
        context = {"email": pending_email, "user_id": user_id, "show_resend": True}
        return await sync_to_async(render)(
            request, "users/email_verification.html", context
        )


@require_POST
@csrf_protect
async def resend_verification_code(request):
    """Resend the verification email code."""
    return await send_verification_email(request)
