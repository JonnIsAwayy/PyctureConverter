import warnings
warnings.filterwarnings("ignore", message=".*Given image is not CTkImage.*")

from src.gui import PyctureApp

def main():
    app = PyctureApp()
    app.run()

if __name__ == "__main__":
    main()
