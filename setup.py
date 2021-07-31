from setuptools import find_packages, setup

setup(
    name="whathappened",
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'alembic>=1.6.5',
        'email-validator>=1.1.3',
        'Flask-Assets>=2.0',
        'Flask-Login>=0.5.0',
        'Flask-Mail>=0.9.1',
        'flask-webpackext>=1.0.2',
        'Flask-WTF>=0.15.1',
        'flask>=2.0.1',
        'jsonschema>=3.2.0',
        'markdown2>=2.4.0',
        'packaging>=21.0',
        'Pillow>=8.3.1',
        'PyJWT>=2.1.0',
        'pyScss @ git+git://github.com/gregersn/pyScss.git',
        'python-dotenv>=0.19.0',
        'PyYAML>=5.4.1',
        'SQLAlchemy>=1.4.22',
    ],
)
