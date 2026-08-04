from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.modules.config.services.auth import get_current_active_user
from app.modules.tools.services.weather import query_weather
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/weather",
    tags=["天气查询"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/now", summary="查询实时天气")
async def get_weather_now_router(
        city: str = Query(..., min_length=1, max_length=50, description="城市名称，例如：北京"),
):
    city = city.strip()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="城市名称不能为空",
        )

    data = await query_weather(city)
    return success_response(data=data, message="天气查询成功")
