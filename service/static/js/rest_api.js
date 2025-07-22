$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.orderId);
        $("#orderItem_id").val(res.itemId)
        $("#product_id").val(res.productId)
        $("#orderItem_quantity").val(res.quantity);
        if (res.status == "canceled") {
            $("#order_status").val("canceled");
        } else if (res.status == "shipped") {
            $("#order_status").val("shipped");
        } else if (res.status == "returned") {
            $("#order_status").val("returned")
        } else {
            $("#order_status").val("canceled");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_id").val("");
        $("#orderItem_id").val("");
        $("#product_id").val("");
        $("#orderItem_quantity").val("");
        $("#order_status").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************
    // TODO: add each CRUD operation here

    // When clicking Create, disable ID fields and do not use their values
    $("#create-btn").click(function () {
        $("#order_id").prop("disabled", true);
        $("#orderItem_id").prop("disabled", true);

        let customer_id = $("#customer_id").val();
        let quantity = $("#orderItem_quantity").val();
        let product_id = $("#product_id").val();
        let status = $("#order_status").val();

        let data = {
            "customer_id": customer_id,
            "status": status,
            "order_items": [
                {
                    "product_id": product_id,
                    "quantity": quantity
                }
            ]
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
            // Render the new order in the results table
            let order = res;
            let items = order.order_items ? order.order_items.map(item =>
                `ID:${item.id}, Product:${item.product_id}, Qty:${item.quantity}`
            ).join("<br>") : "";
            let row = `<tr>
                <td>${order.id}</td>
                <td>${order.customer_id}</td>
                <td>${order.status}</td>
                <td>${items}</td>
            </tr>`;
            $("#search_results tbody").prepend(row);
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

        // Re-enable fields after create
        $("#order_id").prop("disabled", false);
        $("#orderItem_id").prop("disabled", false);
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });



})
