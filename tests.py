from unittest import TestCase

from app import app
from models import db, Cupcake

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()


CUPCAKE_DATA = {
    "flavor": "TestFlavor",
    "size": "TestSize",
    "rating": 5,
    "image": "http://test.com/cupcake.jpg"
}

CUPCAKE_DATA_2 = {
    "flavor": "TestFlavor2",
    "size": "TestSize2",
    "rating": 10,
    "image": "http://test.com/cupcake2.jpg"
}


class CupcakeViewsTestCase(unittest.TestCase):
    """Tests for views of API."""

    @classmethod
    def setUpClass(cls):
        """Setup the application and test client only once."""
        with app.app_context():
            db.drop_all()
            db.create_all()

    def setUp(self):
        """Make demo data and setup transaction."""
        self.app = app.test_client()
        with app.app_context():
            Cupcake.query.delete()
            cupcake = Cupcake(**CUPCAKE_DATA)
            db.session.add(cupcake)
            db.session.commit()
            self.cupcake = cupcake

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        """Teardown the application after all tests."""
        with app.app_context():
            db.drop_all()

    def test_list_cupcakes(self):
        with app.test_client() as client:
            resp = client.get("/api/cupcakes")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "cupcakes": [
                    {
                        "id": self.cupcake.id,
                        "flavor": "TestFlavor",
                        "size": "TestSize",
                        "rating": 5,
                        "image": "http://test.com/cupcake.jpg"
                    }
                ]
            })

    def test_get_cupcake(self):
        with app.test_client() as client:
            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcake": {
                    "id": self.cupcake.id,
                    "flavor": "TestFlavor",
                    "size": "TestSize",
                    "rating": 5,
                    "image": "http://test.com/cupcake.jpg"
                }
            })

    def test_create_cupcake(self):
        with app.test_client() as client:
            url = "/api/cupcakes"
            resp = client.post(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json

            # don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor2",
                    "size": "TestSize2",
                    "rating": 10,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

            self.assertEqual(Cupcake.query.count(), 2)

    def test_patch_cupcake(self):
        # Use the Flask test client to send a PATCH request to update the cupcake
        with app.test_client() as client:
            response = client.patch(f'/api/cupcakes/{self.cupcake.id}', json={
                'flavor': 'Updated Flavor', 'size': 'Medium', 'rating': 4.5})

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the cupcake was updated
        updated_cupcake = Cupcake.query.get(self.cupcake.id)
        self.assertEqual(updated_cupcake.flavor, 'Updated Flavor')
        self.assertEqual(updated_cupcake.size, 'Medium')
        self.assertEqual(updated_cupcake.rating, 4.5)
