"""
services/admin/admin_dashboard_service.py
-------------------------------------------
Service tổng hợp dữ liệu cho Admin Dashboard.

Chiến lược:
  - Mỗi section có cache riêng trên Redis (TTL ngắn 30-60s).
  - API GET trả về data từ cache nếu còn hạn, query DB nếu hết hạn.
  - Khi có event (dịch xong, feedback mới...) → invalidate cache + bắn SSE.
"""
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import Depends
from sqlalchemy import func, select, case, and_, cast, Date, Integer, Float
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import User, Translation, TranslationFeedback, Language
from ...services.sse_manager import sse_manager

# Redis cache keys & TTL (seconds)
CACHE_PREFIX = "admin:dashboard"
CACHE_TTL_SHORT = 30     # overview, recent lists
CACHE_TTL_MEDIUM = 60    # hourly chart
CACHE_TTL_LONG = 300     # weekly chart, direction stats

# Admin SSE channel
ADMIN_SSE_CHANNEL = "admin-dashboard"


class AdminDashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = sse_manager.redis_client

    # ==================================================================
    # FULL DASHBOARD — 1 API call lấy tất cả
    # ==================================================================
    async def get_full_dashboard(self) -> dict:
        """Tổng hợp tất cả section trong 1 response."""
        overview = await self.get_overview()
        weekly = await self.get_weekly_chart()
        hourly = await self.get_hourly_chart()
        rating = await self.get_rating_distribution()
        direction = await self.get_direction_stats()
        recent_users = await self.get_recent_active_users()
        recent_fbs = await self.get_recent_feedbacks()

        return {
            "overview": overview,
            "weekly_chart": weekly,
            "hourly_chart": hourly,
            "rating_distribution": rating,
            "direction_stats": direction,
            "recent_users": recent_users,
            "recent_feedbacks": recent_fbs,
        }

    # ==================================================================
    # 1. OVERVIEW CARDS
    # ==================================================================
    async def get_overview(self) -> dict:
        cached = await self._get_cache("overview")
        if cached:
            return cached

        now = datetime.now(timezone.utc)
        today = now.date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)

        # Total users
        total_users = await self._scalar(select(func.count(User.id)))
        users_last_week = await self._scalar(
            select(func.count(User.id)).where(User.created_at < datetime.combine(last_week, datetime.min.time(), tzinfo=timezone.utc))
        )
        users_change = self._pct_change(total_users, users_last_week)

        # New registrations
        new_today = await self._scalar(
            select(func.count(User.id)).where(cast(User.created_at, Date) == today)
        )
        new_yesterday = await self._scalar(
            select(func.count(User.id)).where(cast(User.created_at, Date) == yesterday)
        )
        reg_change = new_today - new_yesterday

        # Translations today
        trans_today = await self._scalar(
            select(func.count(Translation.id)).where(cast(Translation.created_at, Date) == today)
        )
        trans_yesterday = await self._scalar(
            select(func.count(Translation.id)).where(cast(Translation.created_at, Date) == yesterday)
        )
        trans_change = self._pct_change(trans_today, trans_yesterday)

        # New feedbacks today
        fb_today = await self._scalar(
            select(func.count(TranslationFeedback.id)).where(
                cast(TranslationFeedback.created_at, Date) == today
            )
        )
        avg_rating_result = await self._scalar(
            select(func.avg(TranslationFeedback.rating).cast(Float))
        )
        avg_rating = round(avg_rating_result, 1) if avg_rating_result else 0

        result = {
            "total_users": {
                "value": total_users,
                "change": users_change,
                "change_label": "so với tuần trước",
            },
            "new_registrations": {
                "value": new_today,
                "change": reg_change,
                "change_label": "so với hôm qua",
            },
            "translations_today": {
                "value": trans_today,
                "change": trans_change,
                "change_label": "so với hôm qua",
            },
            "new_feedbacks": {
                "value": fb_today,
                "change": 0,
                "change_label": "",
                "extra": f"avg ★ {avg_rating} / 5",
            },
        }
        await self._set_cache("overview", result, CACHE_TTL_SHORT)
        return result

    # ==================================================================
    # 2. WEEKLY CHART — Lượt dịch 7 ngày qua
    # ==================================================================
    async def get_weekly_chart(self) -> dict:
        cached = await self._get_cache("weekly_chart")
        if cached:
            return cached

        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=6)

        stmt = (
            select(
                cast(Translation.created_at, Date).label("date"),
                func.count(Translation.id).label("count"),
            )
            .where(cast(Translation.created_at, Date) >= start_date)
            .group_by(cast(Translation.created_at, Date))
            .order_by(cast(Translation.created_at, Date))
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        # Fill missing dates with 0
        date_map = {str(row.date): row.count for row in rows}
        data = []
        for i in range(7):
            d = start_date + timedelta(days=i)
            data.append({"date": str(d), "count": date_map.get(str(d), 0)})

        chart = {"data": data}
        await self._set_cache("weekly_chart", chart, CACHE_TTL_LONG)
        return chart

    # ==================================================================
    # 3. HOURLY CHART — Lượt dịch theo giờ hôm nay
    # ==================================================================
    async def get_hourly_chart(self) -> dict:
        cached = await self._get_cache("hourly_chart")
        if cached:
            return cached

        today = datetime.now(timezone.utc).date()

        stmt = (
            select(
                func.extract("hour", Translation.created_at).cast(Integer).label("hour"),
                func.count(
                    case((Translation.type == "text", Translation.id))
                ).label("text_count"),
                func.count(
                    case((Translation.type != "text", Translation.id))
                ).label("file_count"),
            )
            .where(cast(Translation.created_at, Date) == today)
            .group_by(func.extract("hour", Translation.created_at).cast(Integer))
            .order_by("hour")
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        hour_map = {row.hour: {"text_count": row.text_count, "file_count": row.file_count} for row in rows}

        data = []
        for h in range(24):
            entry = hour_map.get(h, {"text_count": 0, "file_count": 0})
            data.append({"hour": h, **entry})

        # Tìm peak hours
        peak_morning = peak_evening = None
        morning_counts = [(h, data[h]["text_count"] + data[h]["file_count"]) for h in range(6, 13)]
        evening_counts = [(h, data[h]["text_count"] + data[h]["file_count"]) for h in range(18, 24)]

        if morning_counts:
            max_m = max(morning_counts, key=lambda x: x[1])
            if max_m[1] > 0:
                peak_morning = f"{max_m[0]}-{max_m[0]+2}h"

        if evening_counts:
            max_e = max(evening_counts, key=lambda x: x[1])
            if max_e[1] > 0:
                peak_evening = f"{max_e[0]}-{max_e[0]+2}h"

        chart = {"data": data, "peak_morning": peak_morning, "peak_evening": peak_evening}
        await self._set_cache("hourly_chart", chart, CACHE_TTL_MEDIUM)
        return chart

    # ==================================================================
    # 4. RATING DISTRIBUTION — Phân bổ đánh giá sao
    # ==================================================================
    async def get_rating_distribution(self) -> dict:
        cached = await self._get_cache("rating_dist")
        if cached:
            return cached

        total = await self._scalar(select(func.count(TranslationFeedback.id)))
        avg_r = await self._scalar(select(func.avg(TranslationFeedback.rating).cast(Float)))

        distribution = {}
        for star in range(1, 6):
            count = await self._scalar(
                select(func.count(TranslationFeedback.id)).where(
                    TranslationFeedback.rating == star
                )
            )
            distribution[star] = count

        result = {
            "total_feedbacks": total,
            "avg_rating": round(avg_r, 1) if avg_r else 0,
            "distribution": distribution,
        }
        await self._set_cache("rating_dist", result, CACHE_TTL_LONG)
        return result

    # ==================================================================
    # 5. DIRECTION STATS — Chiều dịch EN ↔ VI
    # ==================================================================
    async def get_direction_stats(self) -> dict:
        cached = await self._get_cache("direction_stats")
        if cached:
            return cached

        # Lấy language id cho en và vi
        en_lang = await self.db.execute(select(Language).where(Language.language_code == "en"))
        vi_lang = await self.db.execute(select(Language).where(Language.language_code == "vi"))
        en = en_lang.scalar_one_or_none()
        vi = vi_lang.scalar_one_or_none()

        en_to_vi = vi_to_en = 0
        en_to_vi_avg = vi_to_en_avg = None

        if en and vi:
            en_to_vi = await self._scalar(
                select(func.count(Translation.id)).where(
                    and_(Translation.source_lang_id == en.id, Translation.target_lang_id == vi.id)
                )
            )
            vi_to_en = await self._scalar(
                select(func.count(Translation.id)).where(
                    and_(Translation.source_lang_id == vi.id, Translation.target_lang_id == en.id)
                )
            )

            # Avg rating theo chiều dịch
            en_to_vi_avg_r = await self._scalar(
                select(func.avg(TranslationFeedback.rating).cast(Float))
                .select_from(TranslationFeedback)
                .join(Translation, TranslationFeedback.translation_id == Translation.id)
                .where(
                    and_(Translation.source_lang_id == en.id, Translation.target_lang_id == vi.id)
                )
            )
            vi_to_en_avg_r = await self._scalar(
                select(func.avg(TranslationFeedback.rating).cast(Float))
                .select_from(TranslationFeedback)
                .join(Translation, TranslationFeedback.translation_id == Translation.id)
                .where(
                    and_(Translation.source_lang_id == vi.id, Translation.target_lang_id == en.id)
                )
            )
            en_to_vi_avg = round(en_to_vi_avg_r, 1) if en_to_vi_avg_r else None
            vi_to_en_avg = round(vi_to_en_avg_r, 1) if vi_to_en_avg_r else None

        total = en_to_vi + vi_to_en
        result = {
            "en_to_vi_count": en_to_vi,
            "vi_to_en_count": vi_to_en,
            "en_to_vi_pct": round(en_to_vi / total * 100, 1) if total > 0 else 0,
            "vi_to_en_pct": round(vi_to_en / total * 100, 1) if total > 0 else 0,
            "en_to_vi_avg_rating": en_to_vi_avg,
            "vi_to_en_avg_rating": vi_to_en_avg,
        }
        await self._set_cache("direction_stats", result, CACHE_TTL_LONG)
        return result

    # ==================================================================
    # 6. RECENT ACTIVE USERS
    # ==================================================================
    async def get_recent_active_users(self) -> list:
        cached = await self._get_cache("recent_users")
        if cached:
            return cached

        now = datetime.now(timezone.utc)
        today = now.date()

        stmt = (
            select(
                User.id,
                User.full_name,
                User.email,
                User.tier,
                User.is_active,
                func.count(Translation.id).label("translation_count"),
                func.max(Translation.created_at).label("last_active"),
            )
            .outerjoin(Translation, User.id == Translation.user_id)
            .group_by(User.id, User.full_name, User.email, User.tier, User.is_active)
            .order_by(func.max(Translation.created_at).desc().nullslast())
            .limit(8)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        users = []
        for row in rows:
            last_active_str = None
            if row.last_active:
                delta = today - row.last_active.date()
                if delta.days == 0:
                    last_active_str = "hôm nay"
                elif delta.days == 1:
                    last_active_str = "hôm qua"
                else:
                    last_active_str = f"{delta.days} ngày trước"

            users.append({
                "id": str(row.id),
                "full_name": row.full_name,
                "email": row.email,
                "tier": row.tier,
                "is_active": row.is_active,
                "translation_count": row.translation_count,
                "last_active": last_active_str,
            })

        await self._set_cache("recent_users", users, CACHE_TTL_SHORT)
        return users

    # ==================================================================
    # 7. RECENT FEEDBACKS
    # ==================================================================
    async def get_recent_feedbacks(self) -> list:
        cached = await self._get_cache("recent_feedbacks")
        if cached:
            return cached

        now = datetime.now(timezone.utc)

        stmt = (
            select(
                TranslationFeedback.id,
                TranslationFeedback.rating,
                TranslationFeedback.feedback_note,
                TranslationFeedback.corrected_content,
                TranslationFeedback.created_at,
                User.full_name.label("user_name"),
                Language.language_code.label("source_code"),
            )
            .join(User, TranslationFeedback.user_id == User.id)
            .join(Translation, TranslationFeedback.translation_id == Translation.id)
            .outerjoin(Language, Translation.source_lang_id == Language.id)
            .order_by(TranslationFeedback.created_at.desc())
            .limit(5)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        # Cần target lang code nữa — query riêng
        feedbacks = []
        for row in rows:
            # Lấy target lang
            t_result = await self.db.execute(
                select(Language.language_code)
                .select_from(Translation)
                .join(Language, Translation.target_lang_id == Language.id)
                .where(Translation.id == (
                    select(TranslationFeedback.translation_id)
                    .where(TranslationFeedback.id == row.id)
                    .scalar_subquery()
                ))
            )
            target_code = t_result.scalar_one_or_none() or "?"

            source_code = (row.source_code or "?").upper()
            target_code_upper = target_code.upper()
            direction = f"{source_code}→{target_code_upper}"

            # Time ago
            delta = now - row.created_at.replace(tzinfo=timezone.utc) if row.created_at.tzinfo is None else now - row.created_at
            time_ago = self._format_time_ago(delta)

            feedbacks.append({
                "id": str(row.id),
                "rating": row.rating,
                "feedback_note": row.feedback_note,
                "corrected_content": row.corrected_content,
                "user_name": row.user_name,
                "direction": direction,
                "created_at": row.created_at.isoformat(),
                "time_ago": time_ago,
            })

        await self._set_cache("recent_feedbacks", feedbacks, CACHE_TTL_SHORT)
        return feedbacks

    # ==================================================================
    # CACHE INVALIDATION — gọi khi có event mới
    # ==================================================================
    async def invalidate_on_translation(self):
        """Xóa cache liên quan khi có bản dịch mới."""
        keys = ["overview", "weekly_chart", "hourly_chart", "direction_stats", "recent_users"]
        for k in keys:
            await self.redis.delete(f"{CACHE_PREFIX}:{k}")

    async def invalidate_on_feedback(self):
        """Xóa cache liên quan khi có feedback mới."""
        keys = ["overview", "rating_dist", "recent_feedbacks"]
        for k in keys:
            await self.redis.delete(f"{CACHE_PREFIX}:{k}")

    async def invalidate_on_new_user(self):
        """Xóa cache liên quan khi có user mới."""
        keys = ["overview", "recent_users"]
        for k in keys:
            await self.redis.delete(f"{CACHE_PREFIX}:{k}")

    # ==================================================================
    # SSE PUSH — thông báo admin dashboard
    # ==================================================================
    @staticmethod
    async def notify_admin(event_type: str, message: str, data: dict = None):
        """
        Publish event vào kênh SSE admin.
        Tất cả admin đang mở dashboard sẽ nhận được.
        """
        await sse_manager.publish_message(
            client_id=ADMIN_SSE_CHANNEL,
            message={
                "event_type": event_type,
                "message": message,
                "data": data or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    # ==================================================================
    # HELPERS NỘI BỘ
    # ==================================================================
    async def _scalar(self, stmt) -> int | float:
        """Thực thi query và trả về scalar value, mặc định 0."""
        result = await self.db.execute(stmt)
        value = result.scalar_one_or_none()
        return value if value is not None else 0

    async def _get_cache(self, key: str) -> dict | list | None:
        raw = await self.redis.get(f"{CACHE_PREFIX}:{key}")
        if raw:
            return json.loads(raw)
        return None

    async def _set_cache(self, key: str, data, ttl: int):
        await self.redis.set(
            f"{CACHE_PREFIX}:{key}",
            json.dumps(data, ensure_ascii=False, default=str),
            ex=ttl,
        )

    @staticmethod
    def _pct_change(current: int, previous: int) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round((current - previous) / previous * 100, 1)

    @staticmethod
    def _format_time_ago(delta: timedelta) -> str:
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "vừa xong"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} phút trước"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} giờ trước"
        days = hours // 24
        return f"{days} ngày trước"


# Dependency Injection
def get_admin_dashboard_service(db: AsyncSession = Depends(get_db)) -> AdminDashboardService:
    return AdminDashboardService(db)
