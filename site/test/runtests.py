import tests
import threading
import unittest

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from app import app

def flask_run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    

if __name__ == "__main__":
    flask_thread = threading.Thread(target=flask_run)
    flask_thread.start()
    
    suite = unittest.TestLoader().loadTestsFromModule(tests)
    unittest.TextTestRunner().run(suite)
    
    sys.exit(0)
    