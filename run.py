from gevent import monkey
            
monkey.patch_all()

from app.cli import interface

interface()
