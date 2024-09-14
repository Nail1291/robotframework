# Define a simple class
class Car:
    def __init__(self, model, year):
        self.model = model
        self.year = year

    def display_info(self):
        return f"Car Model: {self.model}, Year: {self.year}"

# Function that returns a Car object
def create_car(model, year):
    return Car(model, year)

# Calling the function to return a Car object
my_car = create_car("Toyota", 2022)

# Accessing the returned object's attributes and methods
print(my_car.display_info())  # Output: Car Model: Toyota, Year: 2022
