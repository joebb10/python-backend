import math
import time
import random

def time_dilation_special_relativity(t, v):
    """Calculate time dilation due to special relativity."""
    return t / math.sqrt(1 - v**2)

def time_dilation_general_relativity(t, M, r):
    """Calculate time dilation due to general relativity."""
    G = 6.67430e-11
    c = 299792458
    return t * math.sqrt(1 - (2 * G * M) / (r * c**2))

def receive_message_from_future():
    choice = input("Choose a method (special/general): ").lower()
    t = float(input("Enter the proper time (time for stationary observer) in seconds: "))
    
    if choice == "special":
        v = float(input("Enter the velocity as a fraction of the speed of light (0 <= v < 1): "))
        t_dilated = time_dilation_special_relativity(t, v)
    elif choice == "general":
        M = float(input("Enter the mass of the object in kilograms: "))
        r = float(input("Enter the distance from the center of the mass in meters: "))
        t_dilated = time_dilation_general_relativity(t, M, r)
    else:
        print("Invalid choice.")
        return
    
    time_difference = t_dilated - t
    if time_difference > 0:
        question = input(f"\nAsk a question to receive an answer from the future: ")
        print(f"\nWaiting {time_difference} seconds to receive the message from the future...\n")
        time.sleep(time_difference)
        
        # Generate a random answer
        answers = ["Yes", "No", "Maybe", "It's uncertain", "Definitely!", "Ask again later"]
        response = random.choice(answers)
        
        print(f"Message from the future: {response}")
    else:
        print("\nCannot receive a message from the future with the given parameters.")

if __name__ == "__main__":
    receive_message_from_future()
