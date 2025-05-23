from app.models import Check, PaymentType

def get_receipt_text(check: Check):
    width = 40 # total width of the receipt

    def center(text):
        return text.center(width)

    def line():
        return "=" * width

    def item_line(name, total):
        if len(name) > 20 or len(total) > 15:
            return f"{name}\n{right_align(total, width)}"
        else:
            return f"{name:<25}{right_align(total, 15)}"
    
    def format_number(number):
        return f"{number:,.2f}".replace(",", " ")

    def right_align(text, width):
        return text.rjust(width)

    lines = []

    lines.append(center(f"{check.user.name}"))
    lines.append(line())
    
    for position in check.positions:
        lines.append(f"{position.quantity:.0f} x {format_number(position.price)}")
        position_total = format_number(position.total)
        lines.append(item_line(f"{position.name}", position_total))
        lines.append("-" * width)

    lines.append(item_line("СУМА", format_number(check.total)))
    lines.append(item_line(f"{check.payment.type == PaymentType.CASHLESS and 'Картка' or 'Готівка'}", format_number(check.payment.amount)))
    lines.append(item_line("Решта", format_number(check.rest)))
    lines.append(line())

    lines.append("")
    lines.append(center(f"{check.created_at.strftime('%d.%m.%Y %H:%M')}"))
    lines.append(center("Дякуємо за покупку!"))

    return "\n".join(lines)