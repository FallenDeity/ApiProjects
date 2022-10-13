from dotenv import load_dotenv

from api import session

if __name__ == "__main__":
    load_dotenv()
    session.run()
