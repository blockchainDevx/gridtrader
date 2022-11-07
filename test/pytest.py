class Decoter():
    def __init__(self):
        print('init')
    
    def __call__(self,name):
        print('call',name)

class Singleton(object):
    def __init__(self, cls):
        print('init')
        self._cls = cls
        self._instance = {}
    def __call__(self, *args):
        print('call')
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls(*args)
        return self._instance[self._cls]

@Singleton
class singleobj():
    def __init__(self):
        print('single')


sing=singleobj()

singleobj=Singleton(singleobj)
sing2=singleobj()