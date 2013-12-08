from setuptools import setup
setup(
    name='reahl-dev',
    version=u'2.0.0a3',
    description='The core Reahl development tools.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language. . Reahl-dev is the component containing general Reahl development tools. ',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.dev'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-component>=2.0.0a3,<2.1', u'reahl-tofu>=2.0.0a3,<2.1', u'reahl-bzrsupport>=2.0.0a3,<2.1', u'Babel>=0.9,<0.10'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0.0a3,<2.1', u'reahl-stubble>=2.0.0a3,<2.1'],
    test_suite=u'reahl.dev_dev',
    entry_points={
        u'reahl.dev.xmlclasses': [
            u'MetaInfo = reahl.dev.devdomain:MetaInfo',
            u'HardcodedMetadata = reahl.dev.devdomain:HardcodedMetadata',
            u'DebianPackageMetadata = reahl.dev.devdomain:DebianPackageMetadata',
            u'BzrSourceControl = reahl.dev.devdomain:BzrSourceControl',
            u'Project = reahl.dev.devdomain:Project',
            u'ChickenProject = reahl.dev.devdomain:ChickenProject',
            u'EggProject = reahl.dev.devdomain:EggProject',
            u'DebianPackage = reahl.dev.devdomain:DebianPackage',
            u'DebianPackageSet = reahl.dev.devdomain:DebianPackageSet',
            u'SshRepository = reahl.dev.devdomain:SshRepository',
            u'PythonSourcePackage = reahl.dev.devdomain:PythonSourcePackage',
            u'PythonSourcePackageSet = reahl.dev.devdomain:PythonSourcePackageSet',
            u'PackageIndex = reahl.dev.devdomain:PackageIndex',
            u'Dependency = reahl.dev.devdomain:Dependency',
            u'ThirdpartyDependency = reahl.dev.devdomain:ThirdpartyDependency',
            u'XMLDependencyList = reahl.dev.devdomain:XMLDependencyList',
            u'ExtrasList = reahl.dev.devdomain:ExtrasList',
            u'EntryPointExport = reahl.dev.devdomain:EntryPointExport',
            u'ScriptExport = reahl.dev.devdomain:ScriptExport',
            u'NamespaceList = reahl.dev.devdomain:NamespaceList',
            u'NamespaceEntry = reahl.dev.devdomain:NamespaceEntry',
            u'PersistedClassesList = reahl.dev.devdomain:PersistedClassesList',
            u'OrderedPersistedClass = reahl.dev.devdomain:OrderedPersistedClass',
            u'FileList = reahl.dev.devdomain:FileList',
            u'AttachmentList = reahl.dev.devdomain:AttachmentList',
            u'ShippedFile = reahl.dev.devdomain:ShippedFile',
            u'MigrationList = reahl.dev.devdomain:MigrationList',
            u'ConfigurationSpec = reahl.dev.devdomain:ConfigurationSpec',
            u'ScheduledJobSpec = reahl.dev.devdomain:ScheduledJobSpec',
            u'ExcludedPackage = reahl.dev.devdomain:ExcludedPackage',
            u'TranslationPackage = reahl.dev.devdomain:TranslationPackage',
            u'CommandAlias = reahl.dev.devdomain:CommandAlias',
            u'ExtraPath = reahl.dev.devdomain:ExtraPath',
            u'ProjectTag = reahl.dev.devdomain:ProjectTag'    ],
        'console_scripts': [
            u'reahl = reahl.dev.devshell:WorkspaceCommandline.execute_one'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.dev.commands': [
            u'Refresh = reahl.dev.devshell:Refresh',
            u'ExplainLegend = reahl.dev.devshell:ExplainLegend',
            u'List = reahl.dev.devshell:List',
            u'Select = reahl.dev.devshell:Select',
            u'ClearSelection = reahl.dev.devshell:ClearSelection',
            u'ListSelections = reahl.dev.devshell:ListSelections',
            u'Save = reahl.dev.devshell:Save',
            u'Read = reahl.dev.devshell:Read',
            u'DeleteSelection = reahl.dev.devshell:DeleteSelection',
            u'Shell = reahl.dev.devshell:Shell',
            u'Setup = reahl.dev.devshell:Setup',
            u'Build = reahl.dev.devshell:Build',
            u'ListMissingDependencies = reahl.dev.devshell:ListMissingDependencies',
            u'DebInstall = reahl.dev.devshell:DebInstall',
            u'Upload = reahl.dev.devshell:Upload',
            u'MarkReleased = reahl.dev.devshell:MarkReleased',
            u'SubstVars = reahl.dev.devshell:SubstVars',
            u'Debianise = reahl.dev.devshell:Debianise',
            u'Info = reahl.dev.devshell:Info',
            u'ExtractMessages = reahl.dev.devshell:ExtractMessages',
            u'MergeTranslations = reahl.dev.devshell:MergeTranslations',
            u'CompileTranslations = reahl.dev.devshell:CompileTranslations',
            u'AddLocale = reahl.dev.devshell:AddLocale',
            u'UpdateAptRepository = reahl.dev.devshell:UpdateAptRepository',
            u'ServeSMTP = reahl.dev.mailtest:ServeSMTP'    ],
                 },
    extras_require={}
)
