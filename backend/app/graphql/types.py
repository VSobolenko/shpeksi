"""Strawberry GraphQL types and async builders from Beanie documents.

Field names are kept in the exact snake_case/camelCase mix that the existing
frontends expect (the schema is created with ``auto_camel_case=False``). The
Mongo ``_id`` field is exposed as the GraphQL field ``_id`` via an explicit
``strawberry.field(name="_id")`` mapping.
"""

from __future__ import annotations

from typing import List, Optional

import strawberry

from app.models import (
    Addon,
    Category,
    Food,
    Option,
    Order,
    OrderAddon,
    OrderItem,
    OrderOption,
    OrderVariation,
    Restaurant,
    Review,
    StatusQueue,
    User,
    Variation,
)


def iso(dt) -> Optional[str]:
    return dt.isoformat() if dt else None


# --------------------------------------------------------------------------- #
# Scalars / leaf types
# --------------------------------------------------------------------------- #


@strawberry.type
class OptionType:
    id: strawberry.ID = strawberry.field(name="_id")
    title: str = ""
    description: str = ""
    price: float = 0.0


@strawberry.type
class AddonType:
    id: strawberry.ID = strawberry.field(name="_id")
    title: str = ""
    description: str = ""
    quantity_minimum: int = 0
    quantity_maximum: int = 1
    options: List[OptionType] = strawberry.field(default_factory=list)
    is_active: bool = True


@strawberry.type
class VariationType:
    id: strawberry.ID = strawberry.field(name="_id")
    title: str = ""
    price: float = 0.0
    discounted: float = 0.0
    addons: List[AddonType] = strawberry.field(default_factory=list)


@strawberry.type
class CategoryType:
    id: strawberry.ID = strawberry.field(name="_id")
    title: str = ""
    description: str = ""
    img_menu: Optional[str] = None


@strawberry.type
class FoodType:
    id: strawberry.ID = strawberry.field(name="_id")
    title: str = ""
    description: str = ""
    img_url: Optional[str] = None
    stock: Optional[int] = 0
    tag: Optional[str] = None
    variations: List[VariationType] = strawberry.field(default_factory=list)
    category: Optional[CategoryType] = None


@strawberry.type
class CouponType:
    id: strawberry.ID = strawberry.field(name="_id")
    code: str = ""
    discount: float = 0.0
    enabled: bool = True


@strawberry.type
class AddressType:
    id: strawberry.ID = strawberry.field(name="_id")
    label: Optional[str] = None
    delivery_address: str = ""
    details: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    selected: bool = False


@strawberry.type
class UserType:
    id: strawberry.ID = strawberry.field(name="_id")
    name: str = ""
    email: str = ""
    phone: str = ""
    is_active: bool = True
    notificationToken: Optional[str] = None
    is_order_notification: bool = True
    is_offer_notification: bool = True
    addresses: List[AddressType] = strawberry.field(default_factory=list)


@strawberry.type
class ConfigurationType:
    id: strawberry.ID = strawberry.field(name="_id")
    order_id_prefix: str = ""
    email: str = ""
    password: str = ""
    enable_email: bool = False
    client_id: str = ""
    client_secret: str = ""
    sandbox: bool = True
    publishable_key: str = ""
    secret_key: str = ""
    currency: str = "USD"
    currency_symbol: str = "$"


@strawberry.type
class RestaurantType:
    id: strawberry.ID = strawberry.field(name="_id")
    name: str = ""
    slug: str = ""
    is_active: bool = True


@strawberry.type
class StatusQueueType:
    pending: Optional[str] = None
    preparing: Optional[str] = None
    ready: Optional[str] = None
    completed: Optional[str] = None
    cancelled: Optional[str] = None


@strawberry.type
class ReviewType:
    id: strawberry.ID = strawberry.field(name="_id")
    rating: int = 0
    description: Optional[str] = ""
    is_active: bool = True
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    order: Optional[OrderType] = None


@strawberry.type
class OrderItemType:
    id: strawberry.ID = strawberry.field(name="_id")
    food: Optional[FoodType] = None
    variation: Optional[VariationType] = None
    addons: List[AddonType] = strawberry.field(default_factory=list)
    quantity: int = 1


@strawberry.type
class OrderType:
    id: strawberry.ID = strawberry.field(name="_id")
    order_id: str = ""
    user: Optional[UserType] = None
    items: List[OrderItemType] = strawberry.field(default_factory=list)
    order_amount: float = 0.0
    paid_amount: float = 0.0
    payment_method: str = "COD"
    payment_status: str = "PENDING"
    order_status: str = "PENDING"
    status_queue: Optional[StatusQueueType] = None
    reason: Optional[str] = None
    review: Optional[ReviewType] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


# --------------------------------------------------------------------------- #
# Auth / mutation result payloads
# --------------------------------------------------------------------------- #


@strawberry.type
class AuthPayload:
    userId: Optional[str] = None
    token: Optional[str] = None
    is_active: bool = True
    tokenExpiration: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notificationToken: Optional[str] = None


@strawberry.type
class AdminAuthPayload:
    userId: Optional[str] = None
    token: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


@strawberry.type
class AdminStaffType:
    id: strawberry.ID = strawberry.field(name="_id")
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.type
class ResetPasswordResult:
    result: Optional[str] = None


@strawberry.type
class UploadTokenResult:
    id: strawberry.ID = strawberry.field(name="_id")
    push_token: Optional[str] = None


@strawberry.type
class ReviewOrderResult:
    id: strawberry.ID = strawberry.field(name="_id")
    order_id: str = ""
    review: Optional[ReviewType] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    is_active: bool = True


@strawberry.type
class UpdateStatusResult:
    id: strawberry.ID = strawberry.field(name="_id")
    status: bool = False
    reason: Optional[str] = None


# --------------------------------------------------------------------------- #
# Dashboard analytics payloads
# --------------------------------------------------------------------------- #


@strawberry.type
class DashboardTotal:
    total_orders: int = 0
    total_users: int = 0
    total_sales: float = 0.0
    total_ratings: int = 0
    avg_ratings: float = 0.0


@strawberry.type
class DailySale:
    day: str = ""
    amount: float = 0.0


@strawberry.type
class DailyOrder:
    day: str = ""
    count: int = 0


@strawberry.type
class DailyOrderData:
    day: str = ""
    count: int = 0
    amount: float = 0.0


@strawberry.type
class DashboardSales:
    orders: List[DailySale] = strawberry.field(default_factory=list)


@strawberry.type
class DashboardOrders:
    orders: List[DailyOrder] = strawberry.field(default_factory=list)


@strawberry.type
class DashboardData:
    total_orders: int = 0
    total_users: int = 0
    total_sales: float = 0.0
    orders: List[DailyOrderData] = strawberry.field(default_factory=list)


# --------------------------------------------------------------------------- #
# Subscription payloads
# --------------------------------------------------------------------------- #


@strawberry.type
class OrderEvent:
    order: Optional[OrderType] = None
    origin: str = ""


@strawberry.type
class OrderStatusEvent:
    userId: str = ""
    origin: str = ""
    order: Optional[OrderType] = None


# --------------------------------------------------------------------------- #
# Input types
# --------------------------------------------------------------------------- #


@strawberry.input
class CategoryInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    title: str = ""
    description: str = ""
    img_menu: Optional[str] = None


@strawberry.input
class VariationInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    title: str = ""
    price: float = 0.0
    discounted: float = 0.0
    addons: List[strawberry.ID] = strawberry.field(default_factory=list)


@strawberry.input
class FoodInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    title: str = ""
    description: str = ""
    img_url: Optional[str] = None
    stock: Optional[int] = 0
    tag: Optional[str] = None
    variations: List[VariationInput] = strawberry.field(default_factory=list)
    category: Optional[strawberry.ID] = None


@strawberry.input
class OptionInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    title: str = ""
    description: str = ""
    price: float = 0.0


@strawberry.input
class AddonInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    title: str = ""
    description: str = ""
    quantity_minimum: int = 0
    quantity_maximum: int = 1
    options: List[strawberry.ID] = strawberry.field(default_factory=list)
    is_active: bool = True


@strawberry.input
class CouponInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    code: str = ""
    discount: float = 0.0
    enabled: bool = True


@strawberry.input
class UserInput:
    facebookId: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    notificationToken: Optional[str] = None
    appleId: Optional[str] = None


@strawberry.input
class UpdateUserInput:
    name: str = ""
    phone: str = ""
    is_active: bool = True


@strawberry.input
class AddressInput:
    id: Optional[strawberry.ID] = strawberry.field(default=None, name="_id")
    label: Optional[str] = None
    delivery_address: str = ""
    details: Optional[str] = ""
    longitude: Optional[float] = None
    latitude: Optional[float] = None


@strawberry.input
class ReviewInput:
    orderId: str = ""
    rating: int = 0
    description: Optional[str] = None


@strawberry.input
class AddonOrderInput:
    id: strawberry.ID = strawberry.field(name="_id")
    options: List[strawberry.ID] = strawberry.field(default_factory=list)


@strawberry.input
class OrderInput:
    food: strawberry.ID
    quantity: int = 1
    variation: Optional[strawberry.ID] = None
    addons: List[AddonOrderInput] = strawberry.field(default_factory=list)


@strawberry.input
class OrderConfigurationInput:
    order_id_prefix: str = ""


@strawberry.input
class EmailConfigurationInput:
    email: str = ""
    password: str = ""
    enable_email: bool = False


@strawberry.input
class PaypalConfigurationInput:
    client_id: str = ""
    client_secret: str = ""
    sandbox: bool = True


@strawberry.input
class StripeConfigurationInput:
    publishable_key: str = ""
    secret_key: str = ""


@strawberry.input
class CurrencyConfigurationInput:
    currency: str = ""
    currency_symbol: str = ""


# --------------------------------------------------------------------------- #
# Builders: Beanie document -> GraphQL type (resolving nested references)
# --------------------------------------------------------------------------- #


def build_option(option: Option) -> OptionType:
    return OptionType(
        id=str(option.id),
        title=option.title,
        description=option.description or "",
        price=option.price,
    )


async def build_addon(addon: Addon) -> AddonType:
    options: list[OptionType] = []
    for option_id in addon.options:
        option = await Option.get(option_id)
        if option:
            options.append(build_option(option))
    return AddonType(
        id=str(addon.id),
        title=addon.title,
        description=addon.description or "",
        quantity_minimum=addon.quantity_minimum,
        quantity_maximum=addon.quantity_maximum,
        options=options,
        is_active=addon.is_active,
    )


async def build_category(category: Category) -> CategoryType:
    return CategoryType(
        id=str(category.id),
        title=category.title,
        description=category.description or "",
        img_menu=category.img_menu,
    )


async def build_variation(variation: Variation) -> VariationType:
    addons: list[AddonType] = []
    for addon_id in variation.addons:
        addon = await Addon.get(addon_id)
        if addon:
            addons.append(await build_addon(addon))
    return VariationType(
        id=str(variation.id),
        title=variation.title,
        price=variation.price,
        discounted=variation.discounted,
        addons=addons,
    )


async def build_food(food: Food) -> FoodType:
    variations = [await build_variation(v) for v in food.variations]
    category = None
    if food.category:
        cat = await Category.get(food.category)
        if cat:
            category = await build_category(cat)
    return FoodType(
        id=str(food.id),
        title=food.title,
        description=food.description or "",
        img_url=food.img_url,
        stock=food.stock,
        tag=food.tag,
        variations=variations,
        category=category,
    )


def build_address(address) -> AddressType:
    return AddressType(
        id=str(address.id),
        label=address.label,
        delivery_address=address.delivery_address or "",
        details=address.details,
        latitude=address.latitude,
        longitude=address.longitude,
        selected=address.selected,
    )


def build_user(user: User) -> UserType:
    return UserType(
        id=str(user.id),
        name=user.name or "",
        email=user.email or "",
        phone=user.phone or "",
        is_active=user.is_active,
        notificationToken=user.notificationToken,
        is_order_notification=user.is_order_notification,
        is_offer_notification=user.is_offer_notification,
        addresses=[build_address(address) for address in user.addresses],
    )


def build_restaurant(restaurant: Restaurant) -> RestaurantType:
    return RestaurantType(
        id=str(restaurant.id),
        name=restaurant.name or "",
        slug=restaurant.slug or "",
        is_active=restaurant.is_active,
    )


def build_configuration(config: "Configuration") -> ConfigurationType:
    return ConfigurationType(
        id=str(config.id),
        order_id_prefix=config.order_id_prefix,
        email=config.email,
        password=config.password,
        enable_email=config.enable_email,
        client_id=config.client_id,
        client_secret=config.client_secret,
        sandbox=config.sandbox,
        publishable_key=config.publishable_key,
        secret_key=config.secret_key,
        currency=config.currency,
        currency_symbol=config.currency_symbol,
    )


def _order_addon_type(addon: OrderAddon) -> AddonType:
    return AddonType(
        id=str(addon.id),
        title=addon.title,
        description=addon.description or "",
        quantity_minimum=addon.quantity_minimum,
        quantity_maximum=addon.quantity_maximum,
        options=[
            OptionType(
                id=str(option.id),
                title=option.title,
                description=option.description or "",
                price=option.price,
            )
            for option in addon.options
        ],
    )


async def build_order_item(item: OrderItem) -> OrderItemType:
    food = None
    if item.food:
        food_doc = await Food.get(item.food)
        if food_doc:
            food = await build_food(food_doc)

    variation = None
    if item.variation:
        variation = VariationType(
            id=str(item.variation.id),
            title=item.variation.title,
            price=item.variation.price,
            discounted=item.variation.discounted,
        )

    return OrderItemType(
        id=str(item.id),
        food=food,
        variation=variation,
        addons=[_order_addon_type(addon) for addon in item.addons],
        quantity=item.quantity,
    )


def _review_type(review: Review) -> ReviewType:
    return ReviewType(
        id=str(review.id),
        rating=review.rating,
        description=review.description,
        is_active=review.is_active,
        createdAt=iso(review.createdAt),
        updatedAt=iso(review.updatedAt),
    )


async def build_order(order: Order, include_review: bool = True) -> OrderType:
    user = None
    if order.user:
        user_doc = await User.get(order.user)
        if user_doc:
            user = build_user(user_doc)

    items = [await build_order_item(item) for item in order.items]

    review = None
    if include_review and order.review:
        review = _review_type(order.review)

    status_queue = None
    if order.status_queue:
        status_queue = StatusQueueType(**order.status_queue.model_dump())

    return OrderType(
        id=str(order.id),
        order_id=order.order_id,
        user=user,
        items=items,
        order_amount=order.order_amount,
        paid_amount=order.paid_amount,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        order_status=order.order_status,
        status_queue=status_queue,
        reason=order.reason,
        review=review,
        createdAt=iso(order.createdAt),
        updatedAt=iso(order.updatedAt),
    )
