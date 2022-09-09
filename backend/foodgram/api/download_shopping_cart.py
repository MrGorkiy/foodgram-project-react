import io

from django.db.models import Sum
from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipe.models import ShoppingCart

FILENAME = "shoppingcart.pdf"


def download_shopping_cart(user):
    """Качаем список покупок."""
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont("DejaVuSerif", "DejaVuSerif.ttf", "UTF-8"))
    x_position, y_position = 50, 800
    shopping_cart = (
        ShoppingCart.objects.filter(user=user)
        .values(
            "recipe__ingredients__name",
            "recipe__ingredients__measurement_unit",
        )
        .annotate(amount=Sum("recipe__recipe__amount"))
        .order_by()
    )
    page.setFont("DejaVuSerif", 14)
    if shopping_cart:
        indent = 20
        page.drawString(x_position, y_position, "Cписок покупок:")
        for index, recipe in enumerate(shopping_cart, start=1):
            page.drawString(
                x_position,
                y_position - indent,
                f'{index}. {recipe["recipe__ingredients__name"]} - '
                f'{recipe["amount"]} '
                f'{recipe["recipe__ingredients__measurement_unit"]}.',
            )
            y_position -= 15
            if y_position <= 50:
                page.showPage()
                y_position = 800
        page.save()
        buffer.seek(0)
    else:
        page.setFont("DejaVuSerif", 24)
        page.drawString(x_position, y_position, "Cписок покупок пуст!")
        page.save()
        buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=FILENAME)
