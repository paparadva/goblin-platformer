
class ObjectGroup(object):
    def __init__(self):
        self.objects = list()
        self._deleted_objs = set()

    def __iter__(self):
        for obj in self.objects:
            yield obj

    def update(self, *args):
        for obj in self.objects:
            obj.update(*args)

        if self._deleted_objs:
            for obj in self._deleted_objs:
                self.objects.remove(obj)
            self._deleted_objs = set()

    def del_obj(self, obj):
        self._deleted_objs.add(obj)

    def append(self, obj):
        self.objects.append(obj)
