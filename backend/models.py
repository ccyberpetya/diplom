from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator
from easy_thumbnails.fields import ThumbnailerImageField
from django.core.files.storage import FileSystemStorage

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


# Create your models here.


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей с поддержкой аватаров и социальной авторизации
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    # Поле для аватара с поддержкой миниатюр
    avatar = ThumbnailerImageField(
        upload_to='avatars/%Y/%m/%d/',
        storage=FileSystemStorage(),
        blank=True,
        null=True,
        resize_source=dict(size=(300, 300), crop='smart'),
        help_text='Загрузите изображение для аватара (рекомендуется 300x300px)',
        verbose_name='Аватар'
    )

    # Поля для социальной авторизации
    social_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID социальной сети',
        help_text='Уникальный идентификатор пользователя в социальной сети'
    )
    social_provider = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Провайдер',
        help_text='Название социальной сети (vk, github и т.д.)'
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)

    def get_avatar_url(self):
        """
        Получить URL аватара пользователя
        """
        if self.avatar:
            return self.avatar.url
        return '/static/default-avatar.png'

    def get_avatar_thumbnail(self, size=(100, 100)):
        """
        Получить URL миниатюры аватара указанного размера

        Args:
            size (tuple): Размер миниатюры (ширина, высота)

        Returns:
            str: URL миниатюры
        """
        if self.avatar:
            from easy_thumbnails.files import get_thumbnailer
            thumbnailer = get_thumbnailer(self.avatar)
            return thumbnailer.get_thumbnail({
                'size': size,
                'crop': True,
                'quality': 90
            }).url
        return '/static/default-avatar.png'


class Shop(models.Model):
    """
    Модель магазина/поставщика
    """
    objects = models.manager.Manager()
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель категории товаров
    """
    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(
        Shop,
        verbose_name='Магазины',
        related_name='categories',
        blank=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель продукта/товара
    """
    objects = models.manager.Manager()
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Модель информации о продукте в конкретном магазине
    """
    objects = models.manager.Manager()
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'{self.product.name} - {self.shop.name}'


class Parameter(models.Model):
    """
    Модель параметра/характеристики товара
    """
    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Модель связи параметра с конкретным продуктом
    """
    objects = models.manager.Manager()
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name='Параметр',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.parameter.name}: {self.value}'


class Contact(models.Model):
    """
    Модель контактной информации пользователя
    """
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='contacts',
        blank=True,
        on_delete=models.CASCADE
    )

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    """
    Модель заказа пользователя
    """
    objects = models.manager.Manager()
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='orders',
        blank=True,
        on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(
        Contact,
        verbose_name='Контакт',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-dt',)

    def __str__(self):
        return f'Заказ #{self.id} от {self.dt.strftime("%d.%m.%Y %H:%M")}'


class OrderItem(models.Model):
    """
    Модель позиции в заказе
    """
    objects = models.manager.Manager()
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ]

    def __str__(self):
        return f'{self.product_info.product.name} x {self.quantity}'


class ConfirmEmailToken(models.Model):
    """
    Модель токена для подтверждения email
    """
    objects = models.manager.Manager()

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return f"Токен подтверждения для {self.user.email}"