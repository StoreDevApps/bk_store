from api.models import (Product,ProductImage)

product = Product.objects.get(codigo='')
images = product.images.all()
print(images)  # Esto debería mostrar una lista de imágenes relacionadas
