from setuptools import setup

setup(
    name="manga_dl",
    version="1.0",
    description="",
    author="simon987",
    author_email="me@simon987.net",
    packages=["manga_dl"],
    include_package_data=True,
    install_requires=[
        "bs4", "requests", "pycryptodome", "js2py", "Pillow"
    ]
)