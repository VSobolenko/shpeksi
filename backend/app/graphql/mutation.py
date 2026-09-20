"""GraphQL Mutation resolvers (auth, catalog, config, orders, notifications)."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import strawberry
from beanie import PydanticObjectId
from jose import JWTError

from app.config import settings
from app.graphql.context import require_admin, require_user
from app.graphql.pubsub import pubsub
from app.graphql.types import (
    AddonInput,
    AddonType,
    AddressInput,
    AdminAuthPayload,
    AuthPayload,
    CategoryInput,
    CategoryType,
    ConfigurationType,
    CouponInput,
    CouponType,
    CurrencyConfigurationInput,
    EmailConfigurationInput,
    FoodInput,
    FoodType,
    OptionInput,
    OptionType,
    OrderConfigurationInput,
    OrderInput,
    OrderType,
    PaypalConfigurationInput,
    ResetPasswordResult,
    ReviewInput,
    ReviewOrderResult,
    StripeConfigurationInput,
    ReviewType,
    UpdateStatusResult,
    UpdateUserInput,
    UploadTokenResult,
    UserInput,
    UserType,
    build_addon,
    build_category,
    build_configuration,
    build_food,
    build_option,
    build_order,
    build_user,
)
from app.models import (
    Addon,
    Address,
    Category,
    Configuration,
    Coupon,
    Food,
    Option,
    Order,
    Review,
    User,
    Variation,
)
from app.services.auth import (
    create_access_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.email import send_email
from app.services.notifications import send_push, send_push_many
from app.services.orders import ORDER_STATUSES, iso, place_order, utc_now

_STATUS_QUEUE_FIELD = {
    "PENDING": "pending",
    "ACCEPTED": "preparing",
    "READY": "ready",
    "COMPLETED": "completed",
    "CANCELLED": "cancelled",
}


def _variation_from_input(v) -> Variation:
    return Variation(
        id=PydanticObjectId(str(v.id)) if v.id else PydanticObjectId(),
        title=v.title or "",
        price=v.price or 0.0,
        discounted=v.discounted or 0.0,
        addons=[PydanticObjectId(str(a)) for a in (v.addons or [])],
    )


def _apply_status(order: Order, status: str) -> None:
    order.order_status = status
    field = _STATUS_QUEUE_FIELD.get(status)
    if field and order.status_queue:
        setattr(order.status_queue, field, iso(utc_now()))
    order.updatedAt = utc_now()


async def _get_or_create_config() -> Configuration:
    """Return the singleton Configuration document, creating it if absent."""
    config = await Configuration.find_one({})
    if config is None:
        config = Configuration()
        await config.insert()
    return config


@strawberry.type
class Mutation:
    # --- Auth ------------------------------------------------------------- #

    @strawberry.mutation
    async def adminLogin(self, email: str, password: str) -> AdminAuthPayload:
        if email == settings.admin_email and password == settings.admin_password:
            token = create_access_token(subject="admin", role="admin")
            return AdminAuthPayload(userId="admin", token=token, name="Admin", email=email)
        raise Exception("Invalid credentials")

    @strawberry.mutation
    async def login(
        self,
        type: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        facebookId: Optional[str] = None,
        appleId: Optional[str] = None,
        name: Optional[str] = None,
        notificationToken: Optional[str] = None,
    ) -> AuthPayload:
        user = None
        login_type = (type or "").lower()
        if login_type == "default":
            user = await User.find_one(User.email == email)
            if not user or not verify_password(password or "", user.password):
                raise Exception("Invalid credentials")
        elif login_type == "apple":
            user = await User.find_one(User.appleId == appleId) if appleId else None
            if not user:
                user = User(name=name or "", email=email or "", appleId=appleId, is_active=True)
                await user.insert()
        elif login_type in ("facebook", "google"):
            lookup = User.facebookId == facebookId if login_type == "facebook" and facebookId else User.email == email
            user = await User.find_one(lookup)
            if not user:
                user = User(
                    name=name or "",
                    email=email or "",
                    facebookId=facebookId,
                    is_active=True,
                )
                await user.insert()
        else:
            raise Exception("Invalid login type")

        if not user.is_active:
            raise Exception("Account is disabled")

        if notificationToken:
            user.notificationToken = notificationToken
            await user.save()

        token = create_access_token(subject=str(user.id), role="customer")
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        return AuthPayload(
            userId=str(user.id),
            token=token,
            is_active=user.is_active,
            tokenExpiration=expires.isoformat(),
            name=user.name,
            email=user.email,
            phone=user.phone,
            notificationToken=user.notificationToken,
        )

    @strawberry.mutation
    async def createUser(self, userInput: UserInput) -> AuthPayload:
        if userInput.email:
            existing = await User.find_one(User.email == userInput.email)
            if existing:
                raise Exception("Email already exists")
        user = User(
            name=userInput.name or "",
            email=userInput.email or "",
            phone=userInput.phone or "",
            password=hash_password(userInput.password) if userInput.password else None,
            facebookId=userInput.facebookId,
            appleId=userInput.appleId,
            notificationToken=userInput.notificationToken,
            is_active=True,
        )
        await user.insert()
        token = create_access_token(subject=str(user.id), role="customer")
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        return AuthPayload(
            userId=str(user.id),
            token=token,
            tokenExpiration=expires.isoformat(),
            name=user.name,
            email=user.email,
            phone=user.phone,
            notificationToken=user.notificationToken,
            is_active=True,
        )

    @strawberry.mutation
    async def updateUser(self, info: strawberry.Info, updateUserInput: UpdateUserInput) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        user.name = updateUserInput.name
        user.phone = updateUserInput.phone
        user.is_active = updateUserInput.is_active
        await user.save()
        return build_user(user)

    @strawberry.mutation
    async def updateNotificationStatus(
        self, info: strawberry.Info, offerNotification: bool, orderNotification: bool
    ) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        user.is_offer_notification = offerNotification
        user.is_order_notification = orderNotification
        await user.save()
        return build_user(user)

    @strawberry.mutation
    async def pushToken(self, info: strawberry.Info, token: str) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        user.notificationToken = token
        await user.save()
        return build_user(user)

    @strawberry.mutation
    async def changePassword(self, info: strawberry.Info, oldPassword: str, newPassword: str) -> bool:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user or not verify_password(oldPassword, user.password):
            raise Exception("Invalid current password")
        user.password = hash_password(newPassword)
        await user.save()
        return True

    @strawberry.mutation
    async def forgotPassword(self, email: str) -> ResetPasswordResult:
        user = await User.find_one(User.email == email)
        if user:
            token = create_reset_token(str(user.id))
            reset_url = f"{settings.cors_origin_list[0] if settings.cors_origin_list else ''}/reset?token={token}"
            asyncio.create_task(
                send_email(email, "Reset your password", f"Use this link to reset: {reset_url}")
            )
        return ResetPasswordResult(result="sent")

    @strawberry.mutation
    async def resetPassword(self, password: str, token: str) -> ResetPasswordResult:
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
        except JWTError:
            raise Exception("Invalid or expired token")
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        user.password = hash_password(password)
        await user.save()
        return ResetPasswordResult(result="reset")

    # --- Addresses -------------------------------------------------------- #

    @strawberry.mutation
    async def createAddress(self, info: strawberry.Info, addressInput: AddressInput) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        user.addresses.append(
            Address(
                label=addressInput.label,
                delivery_address=addressInput.delivery_address or "",
                details=addressInput.details,
                latitude=addressInput.latitude,
                longitude=addressInput.longitude,
                selected=not user.addresses,
            )
        )
        await user.save()
        return build_user(user)

    @strawberry.mutation
    async def editAddress(self, info: strawberry.Info, addressInput: AddressInput) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        for address in user.addresses:
            if str(address.id) == str(addressInput.id):
                address.label = addressInput.label
                address.delivery_address = addressInput.delivery_address or ""
                address.details = addressInput.details
                address.latitude = addressInput.latitude
                address.longitude = addressInput.longitude
                break
        await user.save()
        return build_user(user)

    @strawberry.mutation
    async def deleteAddress(self, info: strawberry.Info, id: str) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        user.addresses = [a for a in user.addresses if str(a.id) != str(id)]
        await user.save()
        return build_user(user)

    @strawberry.mutation
    async def selectAddress(self, info: strawberry.Info, id: str) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        for address in user.addresses:
            address.selected = str(address.id) == str(id)
        await user.save()
        return build_user(user)

    # --- Orders ----------------------------------------------------------- #

    @strawberry.mutation
    async def placeOrder(
        self,
        info: strawberry.Info,
        orderInput: List[OrderInput],
        paymentMethod: str,
        couponCode: Optional[str] = None,
    ) -> OrderType:
        user_id = require_user(info)
        raw_items = [
            {
                "food": str(item.food),
                "quantity": item.quantity,
                "variation": str(item.variation) if item.variation else None,
                "addons": [
                    {"_id": str(addon.id), "options": [str(o) for o in addon.options]}
                    for addon in (item.addons or [])
                ],
            }
            for item in orderInput
        ]
        order = await place_order(user_id, raw_items, paymentMethod, couponCode)
        await pubsub.publish("place_order", str(order.id))

        user = await User.get(user_id)
        if user:
            asyncio.create_task(
                send_email(
                    user.email,
                    f"Order {order.order_id} confirmed",
                    f"Your order {order.order_id} has been placed.",
                )
            )
        return await build_order(order)

    @strawberry.mutation
    async def reviewOrder(self, info: strawberry.Info, reviewInput: ReviewInput) -> ReviewOrderResult:
        user_id = require_user(info)
        order = await Order.get(reviewInput.orderId)
        if not order or str(order.user) != str(user_id):
            raise Exception("Order not found")
        now = utc_now()
        if order.review:
            order.review.rating = reviewInput.rating
            order.review.description = reviewInput.description
            order.review.updatedAt = now
        else:
            order.review = Review(
                rating=reviewInput.rating,
                description=reviewInput.description,
                createdAt=now,
                updatedAt=now,
            )
        order.updatedAt = now
        await order.save()
        review = order.review
        return ReviewOrderResult(
            id=str(order.id),
            order_id=order.order_id,
            review=ReviewType(
                id=str(review.id),
                rating=review.rating,
                description=review.description,
                is_active=review.is_active,
                createdAt=iso(review.createdAt),
                updatedAt=iso(review.updatedAt),
            ),
            createdAt=iso(review.createdAt),
            updatedAt=iso(review.updatedAt),
            is_active=review.is_active,
        )

    @strawberry.mutation
    async def updateOrderStatus(
        self, info: strawberry.Info, id: str, status: str, reason: Optional[str] = None
    ) -> OrderType:
        require_admin(info)
        order = await Order.get(id)
        if not order:
            raise Exception("Order not found")
        if status not in ORDER_STATUSES:
            raise Exception("Invalid order status")
        _apply_status(order, status)
        if reason:
            order.reason = reason
        await order.save()

        if order.user:
            await pubsub.publish(f"order_status:{order.user}", str(order.id))
            user = await User.get(order.user)
            if user and user.is_order_notification and user.notificationToken:
                send_push(
                    user.notificationToken,
                    f"Order {order.order_id}",
                    f"Your order is now {status}",
                )
        return await build_order(order)

    @strawberry.mutation
    async def updatePaymentStatus(self, info: strawberry.Info, id: str, status: str) -> OrderType:
        require_admin(info)
        order = await Order.get(id)
        if not order:
            raise Exception("Order not found")
        order.payment_status = status
        if status == "PAID":
            order.paid_amount = order.order_amount
        order.updatedAt = utc_now()
        await order.save()
        return await build_order(order)

    @strawberry.mutation
    async def updateStatus(
        self, info: strawberry.Info, id: str, status: bool, reason: Optional[str] = None
    ) -> UpdateStatusResult:
        require_admin(info)
        user = await User.get(id)
        if not user:
            raise Exception("User not found")
        user.is_active = status
        await user.save()
        return UpdateStatusResult(id=str(user.id), status=status, reason=reason)

    # --- Catalog ---------------------------------------------------------- #

    @strawberry.mutation
    async def createFood(self, info: strawberry.Info, foodInput: FoodInput) -> FoodType:
        require_admin(info)
        food = Food(
            title=foodInput.title or "",
            description=foodInput.description or "",
            img_url=foodInput.img_url,
            stock=foodInput.stock,
            tag=foodInput.tag,
            category=PydanticObjectId(str(foodInput.category)) if foodInput.category else None,
            variations=[_variation_from_input(v) for v in (foodInput.variations or [])],
        )
        await food.insert()
        return await build_food(food)

    @strawberry.mutation
    async def editFood(self, info: strawberry.Info, foodInput: FoodInput) -> FoodType:
        require_admin(info)
        food = await Food.get(PydanticObjectId(str(foodInput.id))) if foodInput.id else None
        if not food:
            raise Exception("Food not found")
        food.title = foodInput.title or ""
        food.description = foodInput.description or ""
        food.img_url = foodInput.img_url
        food.stock = foodInput.stock
        food.tag = foodInput.tag
        food.category = PydanticObjectId(str(foodInput.category)) if foodInput.category else None
        food.variations = [_variation_from_input(v) for v in (foodInput.variations or [])]
        await food.save()
        return await build_food(food)

    @strawberry.mutation
    async def deleteFood(self, info: strawberry.Info, id: str) -> FoodType:
        require_admin(info)
        food = await Food.get(id)
        if food:
            await food.delete()
            return FoodType(id=str(food.id), title=food.title)
        raise Exception("Food not found")

    @strawberry.mutation
    async def createCategory(self, info: strawberry.Info, category: CategoryInput) -> CategoryType:
        require_admin(info)
        cat = Category(
            title=category.title or "",
            description=category.description or "",
            img_menu=category.img_menu,
        )
        await cat.insert()
        return await build_category(cat)

    @strawberry.mutation
    async def editCategory(self, info: strawberry.Info, category: CategoryInput) -> CategoryType:
        require_admin(info)
        cat = await Category.get(PydanticObjectId(str(category.id))) if category.id else None
        if not cat:
            raise Exception("Category not found")
        cat.title = category.title or ""
        cat.description = category.description or ""
        cat.img_menu = category.img_menu
        await cat.save()
        return await build_category(cat)

    @strawberry.mutation
    async def deleteCategory(self, info: strawberry.Info, id: str) -> CategoryType:
        require_admin(info)
        cat = await Category.get(id)
        if cat:
            await cat.delete()
            return CategoryType(id=str(cat.id), title=cat.title)
        raise Exception("Category not found")

    @strawberry.mutation
    async def createOptions(
        self, info: strawberry.Info, optionInput: Optional[List[OptionInput]] = None
    ) -> List[OptionType]:
        require_admin(info)
        result = []
        for oi in (optionInput or []):
            option = Option(title=oi.title or "", description=oi.description or "", price=oi.price or 0.0)
            await option.insert()
            result.append(build_option(option))
        return result

    @strawberry.mutation
    async def editOption(self, info: strawberry.Info, optionInput: OptionInput) -> OptionType:
        require_admin(info)
        option = await Option.get(PydanticObjectId(str(optionInput.id))) if optionInput.id else None
        if not option:
            raise Exception("Option not found")
        option.title = optionInput.title or ""
        option.description = optionInput.description or ""
        option.price = optionInput.price or 0.0
        await option.save()
        return build_option(option)

    @strawberry.mutation
    async def deleteOption(self, info: strawberry.Info, id: str) -> bool:
        require_admin(info)
        option = await Option.get(id)
        if option:
            await option.delete()
        return True

    @strawberry.mutation
    async def createAddons(
        self, info: strawberry.Info, addonInput: Optional[List[AddonInput]] = None
    ) -> List[AddonType]:
        require_admin(info)
        result = []
        for ai in (addonInput or []):
            addon = Addon(
                title=ai.title or "",
                description=ai.description or "",
                quantity_minimum=ai.quantity_minimum,
                quantity_maximum=ai.quantity_maximum,
                options=[PydanticObjectId(str(o)) for o in (ai.options or [])],
                is_active=ai.is_active,
            )
            await addon.insert()
            result.append(await build_addon(addon))
        return result

    @strawberry.mutation
    async def editAddon(self, info: strawberry.Info, addonInput: AddonInput) -> AddonType:
        require_admin(info)
        addon = await Addon.get(PydanticObjectId(str(addonInput.id))) if addonInput.id else None
        if not addon:
            raise Exception("Addon not found")
        addon.title = addonInput.title or ""
        addon.description = addonInput.description or ""
        addon.quantity_minimum = addonInput.quantity_minimum
        addon.quantity_maximum = addonInput.quantity_maximum
        addon.options = [PydanticObjectId(str(o)) for o in (addonInput.options or [])]
        addon.is_active = addonInput.is_active
        await addon.save()
        return await build_addon(addon)

    @strawberry.mutation
    async def deleteAddon(self, info: strawberry.Info, id: str) -> bool:
        require_admin(info)
        addon = await Addon.get(id)
        if addon:
            await addon.delete()
        return True

    @strawberry.mutation
    async def createCoupon(self, info: strawberry.Info, couponInput: CouponInput) -> CouponType:
        require_admin(info)
        coupon = Coupon(code=couponInput.code or "", discount=couponInput.discount, enabled=couponInput.enabled)
        await coupon.insert()
        return CouponType(id=str(coupon.id), code=coupon.code, discount=coupon.discount, enabled=coupon.enabled)

    @strawberry.mutation
    async def editCoupon(self, info: strawberry.Info, couponInput: CouponInput) -> CouponType:
        require_admin(info)
        coupon = await Coupon.get(PydanticObjectId(str(couponInput.id))) if couponInput.id else None
        if not coupon:
            raise Exception("Coupon not found")
        coupon.code = couponInput.code or ""
        coupon.discount = couponInput.discount
        coupon.enabled = couponInput.enabled
        await coupon.save()
        return CouponType(id=str(coupon.id), code=coupon.code, discount=coupon.discount, enabled=coupon.enabled)

    @strawberry.mutation
    async def deleteCoupon(self, info: strawberry.Info, id: str) -> bool:
        require_admin(info)
        coupon = await Coupon.get(id)
        if coupon:
            await coupon.delete()
        return True

    @strawberry.mutation
    async def coupon(self, coupon: str) -> CouponType:
        """Lookup a coupon by code (used by the mobile checkout voucher flow)."""
        doc = await Coupon.find_one(Coupon.code == coupon)
        if not doc:
            raise Exception("Invalid coupon")
        return CouponType(
            id=str(doc.id), code=doc.code, discount=doc.discount, enabled=doc.enabled
        )

    # --- Configuration ---------------------------------------------------- #

    @strawberry.mutation
    async def saveOrderConfiguration(
        self, info: strawberry.Info, configurationInput: OrderConfigurationInput
    ) -> ConfigurationType:
        require_admin(info)
        config = await _get_or_create_config()
        config.order_id_prefix = configurationInput.order_id_prefix
        await config.save()
        return build_configuration(config)

    @strawberry.mutation
    async def saveEmailConfiguration(
        self, info: strawberry.Info, configurationInput: EmailConfigurationInput
    ) -> ConfigurationType:
        require_admin(info)
        config = await _get_or_create_config()
        config.email = configurationInput.email
        config.password = configurationInput.password
        config.enable_email = configurationInput.enable_email
        await config.save()
        return build_configuration(config)

    @strawberry.mutation
    async def savePaypalConfiguration(
        self, info: strawberry.Info, configurationInput: PaypalConfigurationInput
    ) -> ConfigurationType:
        require_admin(info)
        config = await _get_or_create_config()
        config.client_id = configurationInput.client_id
        config.client_secret = configurationInput.client_secret
        config.sandbox = configurationInput.sandbox
        await config.save()
        return build_configuration(config)

    @strawberry.mutation
    async def saveStripeConfiguration(
        self, info: strawberry.Info, configurationInput: StripeConfigurationInput
    ) -> ConfigurationType:
        require_admin(info)
        config = await _get_or_create_config()
        config.publishable_key = configurationInput.publishable_key
        config.secret_key = configurationInput.secret_key
        await config.save()
        return build_configuration(config)

    @strawberry.mutation
    async def saveCurrencyConfiguration(
        self, info: strawberry.Info, configurationInput: CurrencyConfigurationInput
    ) -> ConfigurationType:
        require_admin(info)
        config = await _get_or_create_config()
        config.currency = configurationInput.currency
        config.currency_symbol = configurationInput.currency_symbol
        await config.save()
        return build_configuration(config)

    # --- Notifications ---------------------------------------------------- #

    @strawberry.mutation
    async def sendNotificationUser(
        self, info: strawberry.Info, notificationTitle: Optional[str] = None, notificationBody: Optional[str] = None
    ) -> bool:
        require_admin(info)
        users = await User.find_all().to_list()
        tokens = [u.notificationToken for u in users if u.notificationToken]
        send_push_many(tokens, notificationTitle or "Pikupo", notificationBody or "")
        return True

    @strawberry.mutation
    async def uploadToken(self, info: strawberry.Info, pushToken: str) -> UploadTokenResult:
        require_admin(info)
        config = await _get_or_create_config()
        config.push_token = pushToken
        await config.save()
        return UploadTokenResult(id=str(config.id), push_token=config.push_token)
