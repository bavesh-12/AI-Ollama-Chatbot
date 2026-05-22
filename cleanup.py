import os
import shutil

def cleanup():
    print("Cleaning up...")
    
    folders_to_clear = ["conversations", "vector_store", "uploads"]
    
    for folder in folders_to_clear:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            os.makedirs(folder)
            print(f"Cleared: {folder}")
    
    print("Cleanup complete!")

if __name__ == "__main__":
    cleanup()