from setuptools import find_packages, setup

package_name = 'catch_them_all_turtle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='padia',
    maintainer_email='padia@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'catch_turtle = catch_them_all_turtle.catch_turtle:main',
            'spawner_turtle = catch_them_all_turtle.spawner_turtle:main'
        ],
    },
)
