"""GraphQL Query resolvers (catalog, users, orders, config, dashboard)."""

from datetime import datetime
from typing import List, Optional

import strawberry
from beanie import PydanticObjectId
from beanie.operators import In

from app.graphql.context import require_admin, require_user
from app.graphql.types import (
    AddonType,
    CategoryType,
    ConfigurationType,
    CouponType,
    DashboardData,
    DashboardOrders,
    DashboardSales,
    DashboardTotal,
    DailyOrder,
    DailyOrderData,
    DailySale,
    FoodType,
    OptionType,
    OrderType,
    ReviewType,
    UserType,
    build_addon,
    build_category,
    build_configuration,
    build_food,
    build_option,
    build_order,
    build_user,
    iso,
)
from app.models import Addon, Category, Configuration, Coupon, Food, Option, Order, User
from app.services.orders import ORDER_STATUSES, PAYMENT_STATUSES


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _food_price_range(food: Food) -> list[float]:
    return [v.price for v in food.variations]


@strawberry.type
class Query:
    # --- Catalog ---------------------------------------------------------- #

    @strawberry.field
    async def categories(self) -> List[CategoryType]:
        categories = await Category.find_all().to_list()
        return [await build_category(c) for c in categories]

    @strawberry.field
    async def allCategories(self, page: Optional[int] = None) -> List[CategoryType]:
        categories = await Category.find_all().to_list()
        return [await build_category(c) for c in categories]

    @strawberry.field
    async def foods(self, page: Optional[int] = None) -> List[FoodType]:
        foods = await Food.find_all().to_list()
        return [await build_food(f) for f in foods]

    @strawberry.field
    async def foodByCategory(
        self,
        category: str,
        onSale: Optional[bool] = None,
        inStock: Optional[bool] = None,
        min: Optional[float] = None,
        max: Optional[float] = None,
        search: Optional[str] = None,
    ) -> List[FoodType]:
        foods = await Food.find(Food.category == PydanticObjectId(category)).to_list()
        result: list[FoodType] = []
        for food in foods:
            prices = _food_price_range(food)
            if inStock and not (food.stock and food.stock > 0):
                continue
            if onSale and not any(v.discounted > 0 for v in food.variations):
                continue
            if min is not None and not any(p >= min for p in prices):
                continue
            if max is not None and not any(p <= max for p in prices):
                continue
            if search and search.lower() not in (food.title or "").lower():
                continue
            result.append(await build_food(food))
        return result

    @strawberry.field
    async def foodByIds(self, ids: List[str]) -> List[FoodType]:
        foods = await Food.find(In(Food.id, [PydanticObjectId(i) for i in ids])).to_list()
        return [await build_food(f) for f in foods]

    @strawberry.field
    async def addons(self) -> List[AddonType]:
        addons = await Addon.find_all().to_list()
        return [await build_addon(a) for a in addons]

    @strawberry.field
    async def allAddons(self, page: Optional[int] = None) -> List[AddonType]:
        addons = await Addon.find_all().to_list()
        return [await build_addon(a) for a in addons]

    @strawberry.field
    async def options(self) -> List[OptionType]:
        options = await Option.find_all().to_list()
        return [build_option(o) for o in options]

    @strawberry.field
    async def allOptions(self, page: Optional[int] = None) -> List[OptionType]:
        options = await Option.find_all().to_list()
        return [build_option(o) for o in options]

    @strawberry.field
    async def coupons(self) -> List[CouponType]:
        coupons = await Coupon.find_all().to_list()
        return [
            CouponType(id=str(c.id), code=c.code, discount=c.discount, enabled=c.enabled)
            for c in coupons
        ]

    @strawberry.field
    async def configuration(self) -> ConfigurationType:
        config = await Configuration.find_one({})
        if not config:
            config = await Configuration().insert()
        return build_configuration(config)

    # --- Auth / profile --------------------------------------------------- #

    @strawberry.field
    async def profile(self, info: strawberry.Info) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        return build_user(user)

    # --- Orders ----------------------------------------------------------- #

    @strawberry.field
    async def order(self, info: strawberry.Info, id: str) -> OrderType:
        user_id = require_user(info)
        order = await Order.get(id)
        if not order or str(order.user) != str(user_id):
            raise Exception("Order not found")
        return await build_order(order)

    @strawberry.field
    async def orders(self, info: strawberry.Info, offset: Optional[int] = 0) -> List[OrderType]:
        user_id = require_user(info)
        orders = (
            await Order.find(Order.user == PydanticObjectId(user_id))
            .sort("-createdAt")
            .skip(offset or 0)
            .limit(10)
            .to_list()
        )
        return [await build_order(o) for o in orders]

    @strawberry.field
    async def allOrders(
        self, info: strawberry.Info, page: Optional[int] = None, rows: Optional[int] = None, search: Optional[str] = None
    ) -> List[OrderType]:
        require_admin(info)
        query = Order.find_all()
        orders = await query.sort("-createdAt").to_list()
        if search:
            term = search.lower()
            filtered = []
            for o in orders:
                if term in (o.order_id or "").lower():
                    filtered.append(o)
                    continue
                user = await User.get(o.user) if o.user else None
                if user and term in (user.name or "").lower():
                    filtered.append(o)
            orders = filtered
        limit = rows or len(orders)
        return [await build_order(o) for o in orders[:limit]]

    @strawberry.field
    async def orderCount(self, info: strawberry.Info) -> int:
        require_admin(info)
        return await Order.find_all().count()

    @strawberry.field
    async def users(self, info: strawberry.Info, page: Optional[int] = None) -> List[UserType]:
        require_admin(info)
        users = await User.find_all().to_list()
        return [build_user(u) for u in users]

    @strawberry.field
    async def allReviews(self, info: strawberry.Info, offset: Optional[int] = 0) -> List[ReviewType]:
        require_admin(info)
        orders = await Order.find(Order.review != None).sort("-updatedAt").to_list()  # noqa: E711
        reviews: list[ReviewType] = []
        for order in orders:
            order_obj = await build_order(order, include_review=False)
            review = order.review
            reviews.append(
                ReviewType(
                    id=str(review.id),
                    rating=review.rating,
                    description=review.description,
                    is_active=review.is_active,
                    createdAt=iso(review.createdAt),
                    updatedAt=iso(review.updatedAt),
                    order=order_obj,
                )
            )
        return reviews[(offset or 0):]

    # --- Status enums ----------------------------------------------------- #

    @strawberry.field
    def getOrderStatuses(self, info: strawberry.Info) -> List[str]:
        require_admin(info)
        return list(ORDER_STATUSES)

    @strawberry.field
    def getPaymentStatuses(self, info: strawberry.Info) -> List[str]:
        require_admin(info)
        return list(PAYMENT_STATUSES)

    # --- Dashboard -------------------------------------------------------- #

    async def _orders_in_range(self, starting_date: Optional[str], ending_date: Optional[str]):
        query = Order.find_all()
        orders = await query.to_list()
        start = _parse_date(starting_date)
        end = _parse_date(ending_date)
        if start:
            orders = [o for o in orders if o.createdAt and o.createdAt >= start]
        if end:
            orders = [o for o in orders if o.createdAt and o.createdAt <= end]
        return orders

    @strawberry.field
    async def getDashboardTotal(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardTotal:
        require_admin(info)
        orders = await self._orders_in_range(starting_date, ending_date)
        total_orders = len(orders)
        total_sales = round(sum(o.order_amount for o in orders if o.payment_status == "PAID"), 2)
        ratings = [o.review.rating for o in orders if o.review]
        total_ratings = len(ratings)
        avg_ratings = round(sum(ratings) / total_ratings, 2) if total_ratings else 0.0
        total_users = await User.find_all().count()
        return DashboardTotal(
            total_orders=total_orders,
            total_users=total_users,
            total_sales=total_sales,
            total_ratings=total_ratings,
            avg_ratings=avg_ratings,
        )

    async def _daily(self, orders: List[Order], with_amount: bool):
        buckets: dict = {}
        for o in orders:
            day = o.createdAt.date().isoformat() if o.createdAt else "unknown"
            entry = buckets.setdefault(day, {"count": 0, "amount": 0.0})
            entry["count"] += 1
            entry["amount"] += o.order_amount if o.payment_status == "PAID" else 0.0
        if with_amount:
            return [
                DailyOrderData(day=d, count=v["count"], amount=round(v["amount"], 2))
                for d, v in sorted(buckets.items())
            ]
        return [DailyOrder(day=d, count=v["count"]) for d, v in sorted(buckets.items())]

    @strawberry.field
    async def getDashboardSales(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardSales:
        require_admin(info)
        orders = await self._orders_in_range(starting_date, ending_date)
        daily = await self._daily(orders, with_amount=True)
        return DashboardSales(
            orders=[DailySale(day=d.day, amount=d.amount) for d in daily]
        )

    @strawberry.field
    async def getDashboardOrders(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardOrders:
        require_admin(info)
        orders = await self._orders_in_range(starting_date, ending_date)
        return DashboardOrders(orders=await self._daily(orders, with_amount=False))

    @strawberry.field
    async def getDashboardData(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardData:
        require_admin(info)
        orders = await self._orders_in_range(starting_date, ending_date)
        total_sales = round(sum(o.order_amount for o in orders if o.payment_status == "PAID"), 2)
        return DashboardData(
            total_orders=len(orders),
            total_users=await User.find_all().count(),
            total_sales=total_sales,
            orders=await self._daily(orders, with_amount=True),
        )
