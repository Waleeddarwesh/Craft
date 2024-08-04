from rest_framework import serializers
from . models  import  *
from rest_framework.exceptions import AuthenticationFailed

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProImage
        fields = ["id","image"]

class ImageUploadSerializer(serializers.Serializer):
    upload = serializers.ImageField()

class ProductColorserializer(serializers.ModelSerializer):
    class Meta:
        model = ProColors
        fields = ["id", "Color"]

class ProductSizeserializer(serializers.ModelSerializer):
    class Meta:
        model = ProSizes
        fields = ["id", "Size"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    Colors = ProductColorserializer(many=True, read_only=True)
    uploaded_Colors = serializers.ListField(
        child=serializers.CharField(max_length=20),
        write_only=True
    )

    Sizes = ProductSizeserializer(many=True, read_only=True)
    uploaded_Sizes = serializers.ListField(
        child=serializers.CharField(max_length=20),
        write_only=True
    )

    class Meta:
        model = Product
        fields = ["id", 
                  "ProductName", 
                  "ProductDescription", 
                  "QuantityPerUnit", 
                  "Supplier", 
                  "UnitPrice", 
                  "UnitWeight", 
                  "Stock",
                  "OutOfStock", 
                  "DiscountAvailable", 
                  "Discount", 
                  "DiscountPercentage",
                  "Category",
                  "images", 
                  "uploaded_images", 
                  "Colors", 
                  "uploaded_Colors",
                  "Sizes",
                  "uploaded_Sizes",  
                  "Rating",]
        
        read_only_fields = ['Supplier']


    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated or not user.is_supplier:
            raise AuthenticationFailed("User is not a supplier.")
        validated_data['Supplier'] = user.supplier 
        uploaded_images = validated_data.pop('uploaded_images', [])
        uploaded_Colors = validated_data.pop('uploaded_Colors', [])
        uploaded_Sizes = validated_data.pop('uploaded_Sizes',[]) 
        

    # Create the product instance
        product = Product.objects.create(**validated_data)

        # Create product images
        for image in uploaded_images:
            ProImage.objects.create(product=product, image=image)

        # Create product colors
        for color in uploaded_Colors:
            colors = color.split(',')  # Split sizes by comma
            for color in colors:
                ProColors.objects.create(product=product, Color=color.strip())

        # Create product sizes
        for size in uploaded_Sizes:
            sizes = size.split(',')  # Split sizes by comma
            for size in sizes:
                ProSizes.objects.create(product=product, Size=size.strip())

        return product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['CategoryID','Title','Picture']

class CatProSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['CatPro']

class MatCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatCategory
        fields = ['MatID','Title','Picture']

class MatCatProSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['MatCatPro']

class CollectionItemSerializer(serializers.ModelSerializer):
    product = ProductImageSerializer()

    class Meta:
        model = CollectionItem
        fields = ['id', 'product']

class CollectionSerializer(serializers.ModelSerializer):
    items = CollectionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'items']

class CollectionCreateUpdateSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        collection = Collection.objects.create(**validated_data)
        for item in items_data:
            CollectionItem.objects.create(collection=collection, product=item)
        return collection

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        instance.items.all().delete()
        for item in items_data:
            CollectionItem.objects.create(collection=instance, product=item)
        
        return instance 


    
