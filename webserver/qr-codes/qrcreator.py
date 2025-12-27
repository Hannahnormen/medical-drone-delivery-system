import qrcode

order_numbers = ["1", "2", "3", "4", "5"]

for order_number in order_numbers:
    img = qrcode.make(order_number)
    img.save(f"qr_order_{order_number}.png")
    print(f"QR-kod skapad för ordernummer: {order_number}")