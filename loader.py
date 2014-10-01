from stockpile import app, db
from stockpile.models import Physical, StockPile
from trickle import reader




with app.app_context():
    # Load the physical count into the stockpile.
    # Isolate a result-set that shows just the shop-floor count (IGA)
    # Load the sales we care about from the 30th IGA into the stockpile.
    # Isolate a result-set that shows just the perishable shop-floor count (IGA)
    # Load the sales we care about from the 1st GG into the stockpile.
    # Load the sales