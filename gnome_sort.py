def gnome_sort(arr):
    """Sort array using gnome sort algorithm"""
    n = len(arr)
    index = 0
    while index < n:
        if index == 0 or arr[index] >= arr[index - 1]:
            index += 1
        else:
            arr[index], arr[index - 1] = arr[index - 1], arr[index]
            index -= 1
    return arr

try:
    user_input = input("Enter numbers separated by a comma:\n").strip()
    unsorted = [int(item) for item in user_input.split(",")]
    print(gnome_sort(unsorted))
except ValueError:
    print("Error: Please enter valid numbers separated by commas")
