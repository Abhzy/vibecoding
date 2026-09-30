"""
collision: figures out whether a falling object is within the basket.
"""


def is_caught(basket_rect, obj):
    """An object is caught only when its position is inside the basket
    rectangle both horizontally AND vertically."""
    within_x = basket_rect.left <= obj.x <= basket_rect.right
    within_y = basket_rect.top <= obj.y <= basket_rect.bottom
    return within_x and within_y
