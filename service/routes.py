######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import YourResourceModel
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...

@app.post("/item")
def create_item():
    """Create an item"""
    app.logger.info(
        f"Create item endpoint called with body:\n{request.get_data(as_text=True)}"
    )
    item = Item()
    item.deserialize(request.get_json())

    if not item.customer_id:
        abort(status.HTTP_400_BAD_REQUEST, "customer_id not present")

    item.create()
    return make_response(
        jsonify(item.serialize()),
        status.HTTP_201_CREATED,
        {"Location": order.self_url()},
    )


@app.get("/item/<id>")
def get_item(id: int):
    """Get an item"""
    app.logger.info(f"Get item endpoint called with id={id}")
    item = Ietm.find(id)

    if not item:
        abort(status.HTTP_404_NOT_FOUND)

    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)