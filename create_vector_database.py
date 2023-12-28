from memory_chat_utils.vector_database import VectorDatabase

def main():
    
    # Create vectordatabase and store it in the local path:
    VectorDatabase(data_path="data/data_by_sections", action="store")

if __name__ == "__main__":
    main()