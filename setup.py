from setuptools import find_packages, setup

setup(
    name="whathappened",
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "migrations": ["migrations/*"]
    },
    zip_safe=False,
    install_requires=[
        'email-validator',
        'flask',
        'flask-assets',
        'flask-login',
        'Flask-Mail',
        'flask-webpackext',
        'Flask-WTF',
        'alembic',
        'jsonschema',
        'markdown2',
        'packaging',
        'Pillow',
        'PyJWT',
        'python-dotenv',
        'pyScss @ git+git://github.com/gregersn/pyScss.git',
        'PyYAML',
        'SQLAlchemy',
    ],
)
