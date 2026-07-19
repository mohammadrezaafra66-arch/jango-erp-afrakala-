from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from catalog.models import Product
from pricing.models import ProductPrice

from .auth import authenticate_bot_request
from .models import BotRequestLog


def _log_request(request, bot_key, status_code: int) -> None:
    BotRequestLog.objects.create(
        bot_key=bot_key,
        path=request.path,
        method=request.method,
        status_code=status_code,
        remote_addr=request.META.get("REMOTE_ADDR", ""),
    )


@require_GET
def products_list(request):
    auth = authenticate_bot_request(request, required_scope="products:read")
    if auth.status_code != 200:
        _log_request(request, auth.bot_key, auth.status_code)
        return JsonResponse({"error": auth.error}, status=auth.status_code)

    page_number = int(request.GET.get("page", "1"))
    page_size = min(int(request.GET.get("page_size", "50")), 200)

    queryset = Product.objects.filter(is_active=True).select_related("brand", "category")
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)

    current_prices = {
        price.product_id: price
        for price in ProductPrice.objects.filter(
            product_id__in=[product.id for product in page.object_list],
            is_current=True,
        )
    }

    results = []
    for product in page.object_list:
        price = current_prices.get(product.id)
        results.append(
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "brand": product.brand.name,
                "category": product.category.name,
                "is_active": product.is_active,
                "latest_price": None
                if price is None
                else {
                    "amount": str(price.sale_price),
                    "currency": price.currency,
                    "changed_at": price.updated_at.isoformat(),
                },
            }
        )

    _log_request(request, auth.bot_key, 200)
    return JsonResponse(
        {
            "count": paginator.count,
            "page": page.number,
            "page_size": page_size,
            "results": results,
        }
    )
