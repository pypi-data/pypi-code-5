from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
import logging
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging. 
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

log = logging.getLogger('alembic')

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()

def uliweb_include_object(object, name, type_, reflected, compare_to):
    if type_ == 'table':
        if object.__mapping_only__:
            log.info("{{white|red:Skipped}} added table %r", name)
            return False
    return True

def uliweb_compare_server_default(context, inspected_column,
            metadata_column, inspected_default, metadata_default,
            rendered_metadata_default):
    # return True if the defaults are different,
    # False if not, or None to allow the default implementation
    # to compare these defaults
    pass

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    
    """
    from uliweb.manage import make_simple_application
    from uliweb import orm, settings

#    engine = engine_from_config(
#                config.get_section(config.config_ini_section), 
#                prefix='sqlalchemy.', 
#                poolclass=pool.NullPool)

    name = config.get_main_option("engine_name")
    make_simple_application(project_dir='.')
    target_metadata = orm.get_metadata(name)
    connection = orm.get_connection(engine_name=name).connect()
#    connection = engine.connect()
    
    context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_server_default=True,
                include_object=uliweb_include_object,
#                compare_server_default=uliweb_compare_server_default,
                )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

