from app import app
import sys
import os

sys.path.insert(0, '/home/pedrogaszczas/reciperavenapp')
os.environ['FLASK_APP'] = 'your_flask_app'

if __name__ == "__main__":
    app.run()