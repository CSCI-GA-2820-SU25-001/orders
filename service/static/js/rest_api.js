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

    // Handle operation selection and apply
    function setIdFieldsState(operation) {
        if (operation === "create") {
            $("#order_id").prop("disabled", true);
            $("#orderItem_id").prop("disabled", true);
        } else {
            $("#order_id").prop("disabled", false);
            $("#orderItem_id").prop("disabled", false);
        }
    }

    $("#operation-select").change(function () {
        setIdFieldsState($(this).val());
    });
    setIdFieldsState($("#operation-select").val()); // initial state

    $("#apply-btn").click(function (e) {
        e.preventDefault();
        let operation = $("#operation-select").val();
        if (operation === "create") {
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
        } else if (operation === "update") {
            let order_id = $("#order_id").val();
            let customer_id = $("#customer_id").val();
            let status = $("#order_status").val();
            let product_id = $("#product_id").val();
            let quantity = $("#orderItem_quantity").val();
            if (!order_id) {
                flash_message("Order ID is required for update.");
                return;
            }
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
                type: "PUT",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                data: JSON.stringify(data),
            });
            ajax.done(function (res) {
                update_form_data(res)
                flash_message("Order updated successfully");
            });
            ajax.fail(function (res) {
                flash_message(res.responseJSON.message)
            });
        } else if (operation === "delete") {
            let order_id = $("#order_id").val();
            if (!order_id) {
                flash_message("Order ID is required for delete.");
                return;
            }
            $("#flash_message").empty();
            let ajax = $.ajax({
                type: "DELETE",
                url: `/orders/${order_id}`,
            });
            ajax.done(function () {
                flash_message("Order deleted successfully");
                clear_form_data();
            });
            ajax.fail(function (res) {
                flash_message(res.responseJSON.message)
            });
        } else if (operation === "retrieve") {
            let order_id = $("#order_id").val();
            if (!order_id) {
                flash_message("Order ID is required for retrieve.");
                return;
            }
            $("#flash_message").empty();
            let ajax = $.ajax({
                type: "GET",
                url: `/orders/${order_id}`,
                contentType: "application/json"
            });
            ajax.done(function (res) {
                update_form_data(res)
                flash_message("Order retrieved successfully");
            });
            ajax.fail(function (res) {
                flash_message(res.responseJSON.message)
            });
        } else if (operation === "search") {
            // Example: search all orders
            $("#flash_message").empty();
            let ajax = $.ajax({
                type: "GET",
                url: `/orders`,
                contentType: "application/json"
            });
            ajax.done(function (res) {
                $("#search_results tbody").empty();
                res.forEach(function (order) {
                    let items = order.order_items ? order.order_items.map(item =>
                        `ID:${item.id}, Product:${item.product_id}, Qty:${item.quantity}`
                    ).join("<br>") : "";
                    let row = `<tr>
                        <td>${order.id}</td>
                        <td>${order.customer_id}</td>
                        <td>${order.status}</td>
                        <td>${items}</td>
                    </tr>`;
                    $("#search_results tbody").append(row);
                });
                flash_message("Orders loaded.");
            });
            ajax.fail(function (res) {
                flash_message(res.responseJSON.message)
            });
        } else if (operation === "clear") {
            clear_form_data();
            $("#flash_message").empty();
        }
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
