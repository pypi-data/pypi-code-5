"""Factories for the aps_process app."""
import factory

from .. import models


# ======
# Mixins
# ======

class HierarchyFactoryMixin(factory.DjangoModelFactory):
    """Mixin for the ``Hierarchy`` base model."""
    ABSTRACT_FACTORY = True

    name = factory.Sequence(lambda n: 'name_{0}'.format(n))


# =========
# Factories
# =========

class BufferFactory(HierarchyFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``Buffer`` model."""
    FACTORY_FOR = models.Buffer

    item = factory.SubFactory('aps_process.tests.factories.ItemFactory')


class CalendarFactory(factory.DjangoModelFactory):
    """Factory for the ``Calendar`` model."""
    FACTORY_FOR = models.Calendar

    name = factory.Sequence(lambda n: 'name_{0}'.format(n))


class CalendarBucketFactory(factory.DjangoModelFactory):
    """Factory for the ``CalendarBucket`` model."""
    FACTORY_FOR = models.CalendarBucket

    id = factory.Sequence(lambda n: n)
    calendar = factory.SubFactory(CalendarFactory)


class FlowFactory(factory.DjangoModelFactory):
    """Factory for the ``Flow`` model."""
    FACTORY_FOR = models.Flow

    id = factory.Sequence(lambda n: n)
    operation = factory.SubFactory(
        'aps_process.tests.factories.OperationFactory')
    thebuffer = factory.SubFactory(BufferFactory)


class ItemFactory(HierarchyFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``Item`` model."""
    FACTORY_FOR = models.Item


class LocationFactory(HierarchyFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``Location`` model."""
    FACTORY_FOR = models.Location


class OperationFactory(factory.DjangoModelFactory):
    """Factory for the ``Operation`` model."""
    FACTORY_FOR = models.Operation

    name = factory.Sequence(lambda n: 'name_{0}'.format(n))


class ResourceFactory(HierarchyFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``Resource`` model."""
    FACTORY_FOR = models.Resource


class ResourceLoadFactory(factory.DjangoModelFactory):
    """Factory for the ``ResourceLoad`` model."""
    FACTORY_FOR = models.ResourceLoad

    id = factory.Sequence(lambda n: n)
    operation = factory.SubFactory(OperationFactory)
    resource = factory.SubFactory(ResourceFactory)


class SetupMatrixFactory(factory.DjangoModelFactory):
    """Factory for the ``SetupMatrix`` model."""
    FACTORY_FOR = models.SetupMatrix

    name = factory.Sequence(lambda n: 'name_{0}'.format(n))


class SetupRuleFactory(factory.DjangoModelFactory):
    """Factory for the ``SetupRule`` model."""
    FACTORY_FOR = models.SetupRule

    id = factory.Sequence(lambda n: n)
    setupmatrix = factory.SubFactory(SetupMatrixFactory)


class SubOperationFactory(factory.DjangoModelFactory):
    """Factory for the ``SubOperation`` model."""
    FACTORY_FOR = models.SubOperation

    id = factory.Sequence(lambda n: n)
    operation = factory.SubFactory(OperationFactory)
    suboperation = factory.SubFactory(OperationFactory)
