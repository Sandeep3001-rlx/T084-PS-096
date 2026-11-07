
class Farmer:
    def __init__(self, farmer_id, name):
        self.farmer_id = str(farmer_id).strip()
        self.name = str(name).strip()

        if not self.farmer_id:
            raise ValueError("Farmer ID cannot be empty")

        if not self.name:
            raise ValueError("Farmer name cannot be empty")

    def __repr__(self):
        return f"Farmer(farmer_id='{self.farmer_id}', name='{self.name}')"


if __name__ == "__main__":
    farmer = Farmer("F001", "Ramesh Kumar")
    print(farmer)
