import stripe
import os
from lms.models import Course

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def create_stripe_product(course: Course) -> str:
    """
    Создает продукт в Stripe для указанного курса.
    Если продукт с таким именем уже существует, возвращает его ID.
    """
    try:
        existing_products = stripe.Product.list(limit=100, active=True)
        for product in existing_products.data:
            if product.name == course.name:
                if not hasattr(course, 'stripe_product_id') or not course.stripe_product_id:
                    course.stripe_product_id = product.id
                    course.save()
                    pass
                return product.id

        product = stripe.Product.create(
            name=course.name,
            description=course.description[:500] if course.description else None,
            metadata={
                'course_id': course.pk,
                'course_name': course.name
            }
        )

        course.stripe_product_id = product.id
        course.save()

        return product.id
    except stripe.error.StripeError as e:
        print(f"Stripe error creating product: {e}")
        raise


def create_stripe_price(course: Course, amount: int, currency: str = 'usd') -> str:
    """
    Создает цену (Price) для продукта Stripe.
    amount - сумма в копейках/центах (например, 1000 = $10.00)
    """
    try:
        product_id = create_stripe_product(course)

        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount,
            currency=currency,
            metadata={
                'course_id': course.pk,
            }
        )
        return price.id
    except stripe.error.StripeError as e:
        print(f"Stripe error creating price: {e}")
        raise


def create_stripe_checkout_session(course: Course, user_email: str, amount: int, success_url: str,
                                   cancel_url: str) -> str:
    try:
        price_id = create_stripe_price(course, amount)

        checkout_session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            metadata={
                'course_id': course.pk,
                'user_email': user_email,
            },
            customer_email=user_email,
            client_reference_id=str(course.pk),
        )

        return checkout_session.url
    except stripe.error.StripeError as e:
        print(f"Stripe error creating checkout session: {e}")
        raise


