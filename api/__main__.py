from api.setup import API
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    session = API()
    session.run()
