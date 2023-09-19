from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


# TODO refactor tests of product
# TODO create a faker class (for use in tests and use in fill data)
# TODO write other tests from django project
class ProductTestBase(BaseTestCase):
    product_endpoint = '/products/'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        # Initialize the test database and session before the test class starts
        DatabaseManager.create_test_database()

        # TODO set admin token for all test, because just admins can CRUD a product
        # TODO test with non admin users for read a product or read a list of products
        # self.set_admin_authorization()

    @classmethod
    def teardown_class(cls):
        # Drop the test database after all tests in the class have finished
        DatabaseManager.drop_all_tables()


class TestCreateProduct(ProductTestBase):
    """
    Test create a product on the multi scenario
    """

    def test_access_permission(self):
        """
        Test permissions as non-admin user for CRUD methods of create product
        """
        # TODO admin permission can access to all CRUD of a product also list of products
        # TODO non admin users only can use read a product or read a list of products
        ...

    def test_create_simple_product(self):
        """
        Test create a simple-product by the all available inputs (assuming valid data).
        Test response body for simple product.

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """

        payload = {
            'product_name': 'Test Product',
            'description': '<p>test description</p>',
            'status': 'active',
            'price': 25,
            'stock': 3
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] == '<p>test description</p>'
        assert expected['status'] == 'active'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        assert expected['options'] is None
        assert expected['media'] is None

        # Check if "variants" is a list
        assert isinstance(expected['variants'], list)

        # There should be one variant in the list
        assert len(expected['variants']) == 1

        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == 25
        assert variant['stock'] == 3
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_create_variable_product(self):
        """
        Test create a variable-product by the all available inputs (assuming valid data).
        Test response body for variable-product.

        * every time we create a product, the media should be None, because the media after creating a product will be
          attached to it.
        """

        payload = {
            "product_name": "Test Product",
            "description": "<p>test description</p>",
            "status": "active",
            "price": 25,
            "stock": 3,
            "options": [
                {
                    "option_name": "color",
                    "items": ["red", "green"]
                },
                {
                    "option_name": "material",
                    "items": ["Cotton", "Nylon"]
                },
                {
                    "option_name": "size",
                    "items": ["M", "S"]
                }
            ]
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- get response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] == '<p>test description</p>'
        assert expected['status'] == 'active'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert isinstance(variant["product_id"], int)
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    def test_create_simple_product_required(self):
        """
        Test create a simple-product just with required fields in product payload
        """
        payload = {
            'product_name': 'Test Product'
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] is None
        assert expected['status'] == 'draft'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        assert expected['options'] is None
        assert expected['media'] is None

        # Check if "variants" is a list
        assert isinstance(expected['variants'], list)

        # There should be one variant in the list
        assert len(expected['variants']) == 1

        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == 0
        assert variant['stock'] == 0
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_create_variable_product_required(self):
        """
        Test create a variable-product just with required fields in product payload
        """

        payload = {
            "product_name": "Test Product",
            "options": [
                {
                    "option_name": "color",
                    "items": ["red"]
                }
            ]
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- get response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] is None
        assert expected['status'] == 'draft'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 1
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert option["option_name"] == 'color'
            assert isinstance(option['items'], list)
            assert len(option['items']) == 1
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert item["item_name"] == 'red'

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert isinstance(variant["product_id"], int)
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert variant['option2'] is None
            assert variant['option3'] is None
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None


class TestRetrieveProduct(ProductTestBase):
    """
    Test retrieve products on the multi scenario
    """

    def test_retrieve_simple_product(self):
        """
        # TODO Test retrieve a simple product:
        - with price and stock.
        - with one variant.
        - with media.
        """

        # create a product
        # create media
        # retrieve the product
        # check response data

    def test_retrieve_simple_product_without_media(self):
        """
        # TODO Test retrieve a simple product:
        - with price and stock.
        - with one variant.
        """

        # create a product
        # retrieve the product
        # check response data

    def test_retrieve_variable_product(self):
        """
        # TODO Test retrieve a variable product:
        - with price and stock.
        - with options
        - with variants.
        - with media.
        """

        # create a product
        # create options
        # create media
        # retrieve the product
        # check response data

    def test_retrieve_variable_product_without_media(self):
        """
        # TODO Test retrieve a variable product:
        - with price and stock.
        - with options.
        - with variants.
        """

        # create a product
        # create options
        # retrieve the product
        # check response data


class TestUpdateProduct(ProductTestBase):
    """
    Test update a product on the multi scenario
    """
    ...


class TestDestroyProduct(ProductTestBase):
    """
    Test delete a product on the multi scenario
    """
    ...


class TestProductPayloadFields(ProductTestBase):
    # -----------------------
    # --- Create Payloads ---
    # -----------------------
    def test_create_product_empty_payload(self):
        """
        # TODO Test create a product with empty payload
        """

    def test_create_product_invalid_status(self):
        """
        # TODO Test create a product with invalid status value in the payload
        - test set product `status` to 'draft' by default.
        - if `status` not set or it is not one of (active, draft, archive) then set it value to 'draft'
        """

    def test_create_product_invalid_option(self):
        """
        # TODO Test create a product with:
        - invalid option in the payload
        - invalid option-item in payload
        """
