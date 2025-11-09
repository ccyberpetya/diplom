from typing import Type
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User

new_user_registered = Signal()
new_order = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    from backend.models import User  # Импорт внутри функции
    try:
        msg = EmailMultiAlternatives(
            subject=f"Password Reset Token for {reset_password_token.user}",
            body=reset_password_token.key,
            from_email=settings.EMAIL_HOST_USER,
            to=[reset_password_token.user.email]
        )
        msg.send()
        print(f"[EMAIL SENT] Password reset to {reset_password_token.user.email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

@receiver(post_save)
def new_user_registered_signal(sender, instance, created, **kwargs):
    from backend.models import User, ConfirmEmailToken  # Импорт внутри функции
    if sender == User and created and not instance.is_active:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
        try:
            msg = EmailMultiAlternatives(
                subject=f"Confirm Email for {instance.email}",
                body=f"Your confirmation token: {token.key}",
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email]
            )
            msg.send()
            print(f"[EMAIL SENT] Confirmation to {instance.email}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    from backend.models import User  # Импорт внутри функции
    user = User.objects.get(id=user_id)
    try:
        msg = EmailMultiAlternatives(
            subject="Order Created Successfully",
            body='Your order has been created successfully',
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        msg.send()
        print(f"[EMAIL SENT] Order notification to {user.email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")