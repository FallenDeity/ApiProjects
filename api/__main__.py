from api.setup import API
from dotenv import load_dotenv

load_dotenv()
session = API()
app = session.get_app

if __name__ == "__main__":
    session.run()
