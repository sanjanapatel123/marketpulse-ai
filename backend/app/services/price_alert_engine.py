from decimal import Decimal

from app.models.enums import PriceAlertCondition


def should_trigger_price_alert(
    *,
    condition: PriceAlertCondition,
    threshold: Decimal,
    current_price: Decimal,
) -> bool:
    if condition == PriceAlertCondition.PRICE_ABOVE:
        return current_price >= threshold

    if condition == PriceAlertCondition.PRICE_BELOW:
        return current_price <= threshold

    raise ValueError(
        f"Unsupported price-alert condition: {condition}"
    )