from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from beat.benchmarks.models import Comparison, ModelComparison, Tool, Algorithm

class MyComparisonDeleteTest(TestCase):
	def setUp(self):
		# Create TestClient object
		self.client = Client()
		# Create dummy user
		self.u = User.objects.create_user('john', 'lennon@thebeatles.com', 'smith')
		# Log the user in
		self.client.post('/login/', {'username': 'john', 'password': 'smith'})
		# Create other required dummy objects
		self.a = Algorithm.objects.create(name="TestAlgorithm")
		self.t = Tool.objects.create(name="TestTool", version=1)
		self.c = Comparison.objects.create(user=self.u, benchmarks=1, date_time="01-01-2000 00:00:00")
		self.m = ModelComparison.objects.create(user=self.u, type="states", tool=self.t, algorithm=self.a, date_time="01-01-2000 00:00:00")
	
	def test_delete(self):
		# Delete the ModelComparison and check if the Comparison still exists (by counting all (Model)Comparison objects)
		response = self.client.get('/user/compare/model/delete/1/')
		self.assertEqual(ModelComparison.objects.all().count(), 0)
		self.assertEqual(Comparison.objects.all().count(),1)

		# Now delete the remaining Comparison as well
		response = self.client.get('/user/compare/delete/1/')
		self.assertEqual(ModelComparison.objects.all().count(),0)
		self.assertEqual(Comparison.objects.all().count(),0)

