class InventoryManager:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def has_item(self, name):
        for item in self.items:
            if item.name == name:
                return True

    def get_item(self, name):
        results = []
        for item in self.items:
            if item.name == name:
                results.append(item)
        return results

    def update(self, dt):
        for i, item in reversed(list(enumerate(self.items))):
            item.update(dt)
            if item.is_expired():
                del self.items[i]