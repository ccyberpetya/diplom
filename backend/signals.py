from typing import Type
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User

new_user_registered = Signal()
new_order = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    ВРЕМЕННО ОТКЛЮЧЕНО: Отправляем письмо с токеном для сброса пароля
    """
    print(f"[DEBUG] Password reset token for {reset_password_token.user}: {reset_password_token.key}")
    # send_email.delay(
    #     subject=f"Password Reset Token for {reset_password_token.user}",
    #     message=reset_password_token.key,
    #     from_email=settings.EMAIL_HOST_USER,
    #     recipient_list=[reset_password_token.user.email]
    # )


@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
    ВРЕМЕННО ОТКЛЮЧЕНО: Отправляем письмо с подтверждением почты
    """
    if created and not instance.is_active:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
        print(f"[DEBUG] Confirm email token for {instance.email}: {token.key}")

        # send_email.delay(
        #     subject=f"Password Reset Token for {instance.email}",
        #     message=token.key,
        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[instance.email]
        # )


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    ВРЕМЕННО ОТКЛЮЧЕНО: Отправляем письмо при изменении статуса заказа
    """
    user = User.objects.get(id=user_id)
    print(f"[DEBUG] New order for user: {user.email}")

    # send_email.delay(
    #     subject="Обновление статуса заказа",
    #     message='Заказ сформирован',
    #     from_email=settings.EMAIL_HOST_USER,
    #     recipient_list=[user.email]
    # )