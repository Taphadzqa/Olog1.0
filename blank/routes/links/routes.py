from flask import Blueprint, request, abort
from blank.core.models import SystemActivities
from flask_cors import CORS
# Create blueprint handler
links = Blueprint('links', __name__)

CORS(links)


@links.route('/webhook/869029d45aab61d00ee18c9e1434775e', methods=['GET', 'POST'])
def knack_webhook():
    if request.method == 'POST':
        print(request.json)
        return 'Olog says:- success', 200
    else:
        print("No Data")
        return abort(400)
