from api.setup import API
from dotenv import load_dotenv


session = API()

if __name__ == "__main__":
    load_dotenv()
    # session.run()
