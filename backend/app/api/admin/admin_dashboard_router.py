"""
api/admin/admin_dashboard_router.py
--------------------------------------
Router cho Admin Dashboard.

Endpoints:
  GET /admin/dashboard          — Full dashboard (1 API call lấy hết)
  GET /admin/dashboard/overview — Chỉ 4 thẻ tổng quan
  GET /admin/dashboard/charts/weekly   — Biểu đồ 7 ngày
  GET /admin/dashboard/charts/hourly   — Biểu đồ theo giờ
  GET /admin/dashboard/ratings         — Phân bổ đánh giá
  GET /admin/dashboard/directions      — Thống kê chiều dịch
  GET /admin/dashboard/recent-users    — User hoạt động gần đây
  GET /admin/dashboard/recent-feedbacks — Feedback gần đây

Tất cả endpoint yêu cầu quyền admin.
"""
from fastapi import APIRouter, Depends

from ...middleware.auth import require_admin
from ...schemas.admin.admin_dashboard_schema import (
    DashboardOverviewResponse,
    DirectionStatsResponse,
    FullDashboardResponse,
    HourlyChartResponse,
    RatingDistributionResponse,
    WeeklyChartResponse,
)
from ...services.admin.admin_dashboard_service import (
    AdminDashboardService,
    get_admin_dashboard_service,
)

router = APIRouter(prefix="/admin/dashboard", tags=["Admin - Dashboard"])


# ---------------------------------------------------------
# FULL DASHBOARD — Frontend gọi 1 lần duy nhất
# ---------------------------------------------------------
@router.get("", response_model=FullDashboardResponse)
async def get_full_dashboard(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """
    Lấy toàn bộ dữ liệu dashboard trong 1 request.
    Data được cache trên Redis — response cực nhanh.
    """
    return await service.get_full_dashboard()


# ---------------------------------------------------------
# INDIVIDUAL SECTIONS — Frontend gọi riêng từng phần
# ---------------------------------------------------------

@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_overview(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """4 thẻ tổng quan: tổng user, đăng ký mới, lượt dịch, đánh giá."""
    return await service.get_overview()


@router.get("/charts/weekly", response_model=WeeklyChartResponse)
async def get_weekly_chart(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """Biểu đồ lượt dịch 7 ngày qua."""
    return await service.get_weekly_chart()


@router.get("/charts/hourly", response_model=HourlyChartResponse)
async def get_hourly_chart(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """Biểu đồ lượt dịch theo giờ hôm nay (chia text/file)."""
    return await service.get_hourly_chart()


@router.get("/ratings", response_model=RatingDistributionResponse)
async def get_rating_distribution(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """Phân bổ đánh giá 1-5 sao + rating trung bình."""
    return await service.get_rating_distribution()


@router.get("/directions", response_model=DirectionStatsResponse)
async def get_direction_stats(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """Thống kê chiều dịch EN→VI vs VI→EN + rating trung bình mỗi chiều."""
    return await service.get_direction_stats()


@router.get("/recent-users")
async def get_recent_active_users(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """Danh sách user hoạt động gần đây (top 8)."""
    return await service.get_recent_active_users()


@router.get("/recent-feedbacks")
async def get_recent_feedbacks(
    service: AdminDashboardService = Depends(get_admin_dashboard_service),
    _=Depends(require_admin),
):
    """Feedback gần đây nhất (top 5) kèm tên user và chiều dịch."""
    return await service.get_recent_feedbacks()
