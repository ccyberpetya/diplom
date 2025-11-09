from celery import Celery
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task
def send_email(subject, message, from_email, recipient_list):
    """
    Асинхронная задача для отправки email
    """
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list
        )
        msg.send()
        return f"Email sent to {recipient_list}"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@app.task
def do_import(shop_id, url, user_id):
    """
    Асинхронная задача для импорта данных
    """
    try:
        from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
        from requests import get
        from yaml import load as load_yaml, Loader

        stream = get(url).content
        data = load_yaml(stream, Loader=Loader)

        shop = Shop.objects.get(id=shop_id)

        # Очищаем старые данные
        ProductInfo.objects.filter(shop_id=shop.id).delete()

        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(
                id=category['id'],
                name=category['name']
            )
            category_object.shops.add(shop.id)
            category_object.save()

        for item in data['goods']:
            product, _ = Product.objects.get_or_create(
                name=item['name'],
                category_id=item['category']
            )

            product_info = ProductInfo.objects.create(
                product_id=product.id,
                external_id=item['id'],
                model=item['model'],
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity'],
                shop_id=shop.id
            )

            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=parameter_object.id,
                    value=value
                )

        return f"Import completed for shop {shop.name}"

    except Exception as e:
        return f"Error during import: {str(e)}"