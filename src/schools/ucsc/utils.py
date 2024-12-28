import pickle
import os


def handle_tba(value, field_type="text"):
    """Handle 'TBA' values based on the field type."""
    if value == "TBA":
        if field_type == "time":
            return None  # Use None for TBA times
        elif field_type == "text":
            return None  # Use None for TBA text fields
    return value


def retrieve_list_from_pickle(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as file:
                read_list = pickle.load(file)
        except (EOFError, pickle.UnpicklingError):
            read_list = []  # Handle corrupted or empty file
    else:
        read_list = []

    return read_list


def save_list_to_pickle(file_path, read_list):
    # Ensure the file exists at the end (even if it didn't exist initially)
    if not os.path.exists(file_path):
        print("Creating the file as it does not exist.")
        with open(file_path, "wb") as file:
            pickle.dump(read_list, file)
    else:
        # Save any updates to the list (optional)
        with open(file_path, "wb") as file:
            pickle.dump(read_list, file)
