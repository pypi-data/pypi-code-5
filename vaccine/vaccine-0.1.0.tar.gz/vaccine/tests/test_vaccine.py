import unittest

from vaccine import VaccineException, Vaccine


class VaccineTests(unittest.TestCase):

  def setUp(self):
    self.vaccine = Vaccine()

  def setup_constants(self):
    self.vaccine.register("HOST", "localhost")

  def test_register_success(self):
    self.vaccine.register("key", "value")
    self.assertEqual("value", self.vaccine.get("key"))

  def test_register_already_registered(self):
    self.vaccine.register("key", "value")
    self.assertRaises(VaccineException, self.vaccine.register, "key", "another value")

  def test_provides_success(self):
    @self.vaccine.provides("URI")
    def credentials():
      return object()

    # ensure that 2 objects are the same
    o1 = self.vaccine.get("URI")
    o2 = self.vaccine.get("URI")

    self.assertIs(o1, o2)

  def test_provides_already_registered_failure(self):
    def example():
      # register under "URI" once...
      @self.vaccine.provides("URI")
      def credentials():
        return 1

      # register under "URI" again (this will fail)
      @self.vaccine.provides("URI")
      def credentials2():
        return 2

    self.assertRaises(VaccineException, example)

  def test_provides_class_success(self):

    @self.vaccine.provides(SomeServiceInterface)
    class SomeService(SomeServiceInterface):
      def __init__(self):
        self.name = "boop"

    self.assertEqual("boop", self.vaccine.get(SomeServiceInterface).name)

  def test_chaining_success(self):

    # class / needs dependencies
    @self.vaccine.provides(SomeServiceInterface)
    @self.vaccine.requires(host="HOST", credentials="CREDENTIALS")
    class SomeService(SomeServiceInterface):
      def __init__(self, host, credentials):
        self.host        = host
        self.credentials = credentials

    # function / needs no dependencies
    @self.vaccine.provides("CREDENTIALS")
    def credentials():
      return {"user": object(), "password": "XXXX"}

    # register constrant
    self.vaccine.register("HOST", "localhost")

    result = self.vaccine.get(SomeServiceInterface)

    self.assertEqual("localhost", result.host)
    self.assertTrue("user"     in result.credentials)
    self.assertTrue("password" in result.credentials)


class SomeServiceInterface(object):
  pass
