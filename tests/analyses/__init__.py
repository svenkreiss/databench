'''Automatically created by `scaffold-databench`.'''
# flake8: noqa


from .simple1.analysis import Simple1
from .simple2.analysis import Simple2
from .simple3.analysis import Simple3
from .parameters.analysis import Parameters


analyses = [
    ('simple1', Simple1),
    ('simple2', Simple2),
    ('simple3', Simple3),
    ('parameters', Parameters)
]
