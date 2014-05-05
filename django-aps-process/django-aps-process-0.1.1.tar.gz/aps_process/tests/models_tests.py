"""Tests for the models of the aps_process app."""
from django.test import TestCase

from . import factories


class BufferTestCase(TestCase):
    """Tests for the ``Buffer`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Buffer`` model."""
        buf = factories.BufferFactory()
        self.assertTrue(buf.pk)


class CalendarTestCase(TestCase):
    """Tests for the ``Calendar`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Calendar`` model."""
        calendar = factories.CalendarFactory()
        self.assertTrue(calendar.pk)


class CalendarBucketTestCase(TestCase):
    """Tests for the ``CalendarBucket`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``CalendarBucket`` model."""
        calendarbucket = factories.CalendarBucketFactory()
        self.assertTrue(calendarbucket.pk)


class FlowTestCase(TestCase):
    """Tests for the ``Flow`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Flow`` model."""
        flow = factories.FlowFactory()
        self.assertTrue(flow.pk)


class ItemTestCase(TestCase):
    """Tests for the ``Item`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Item`` model."""
        item = factories.ItemFactory()
        self.assertTrue(item.pk)


class LocationTestCase(TestCase):
    """Tests for the ``Location`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Location`` model."""
        location = factories.LocationFactory()
        self.assertTrue(location.pk)


class OperationTestCase(TestCase):
    """Tests for the ``Operation`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Operation`` model."""
        operation = factories.OperationFactory()
        self.assertTrue(operation.pk)


class ResourceTestCase(TestCase):
    """Tests for the ``Resource`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Resource`` model."""
        resource = factories.ResourceFactory()
        self.assertTrue(resource.pk)


class ResourceLoadTestCase(TestCase):
    """Tests for the ``ResourceLoad`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``ResourceLoad`` model."""
        resourceload = factories.ResourceLoadFactory()
        self.assertTrue(resourceload.pk)


class SetupMatrixTestCase(TestCase):
    """Tests for the ``SetupMatrix`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``SetupMatrix`` model."""
        setupmatrix = factories.SetupMatrixFactory()
        self.assertTrue(setupmatrix.pk)


class SetupRuleTestCase(TestCase):
    """Tests for the ``SetupRule`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``SetupRule`` model."""
        setuprule = factories.SetupRuleFactory()
        self.assertTrue(setuprule.pk)


class SubOperationTestCase(TestCase):
    """Tests for the ``SubOperation`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``SubOperation`` model."""
        suboperation = factories.SubOperationFactory()
        self.assertTrue(suboperation.pk)
