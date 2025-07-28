const headers = {
    'X-Api-Key': 'bdd-test-key'
};

$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id || "");
        $("#customer_id").val(res.customer_id || "");
        // Only fill the first order_item if present
        if (res.order_items && res.order_items.length > 0) {
            $("#orderItem_id").val(res.order_items[0].id || "");
            $("#product_id").val(res.order_items[0].product_id || "");
            $("#orderItem_quantity").val(res.order_items[0].quantity || "");
        } else {
            $("#orderItem_id").val("");
            $("#product_id").val("");
            $("#orderItem_quantity").val("");
        }
        $("#order_status").val(res.status || "");
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_id").val("");
        $("#customer_id").val("");
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
            $("#customer_id").prop("disabled", false);
            $("#product_id").prop("disabled", false);
            $("#orderItem_quantity").prop("disabled", false);
            $("#order_status").prop("disabled", false);
        } else if (operation === "update") {
            $("#order_id").prop("disabled", false);
            $("#orderItem_id").prop("disabled", true);
            $("#customer_id").prop("disabled", false);
            $("#product_id").prop("disabled", true);
            $("#orderItem_quantity").prop("disabled", true);
            $("#order_status").prop("disabled", false);
        } else if (operation === "retrieve") {
            // Only order_id is enabled, others are disabled
            $("#order_id").prop("disabled", false);
            $("#orderItem_id").prop("disabled", true);
            $("#customer_id").prop("disabled", true);
            $("#product_id").prop("disabled", true);
            $("#orderItem_quantity").prop("disabled", true);
            $("#order_status").prop("disabled", true);
        } else {
            $("#order_id").prop("disabled", false);
            $("#orderItem_id").prop("disabled", false);
            $("#customer_id").prop("disabled", false);
            $("#product_id").prop("disabled", false);
            $("#orderItem_quantity").prop("disabled", false);
            $("#order_status").prop("disabled", false);
        }
    }

    $("#operation-select").change(function () {
        clear_form_data();
        setIdFieldsState($(this).val());

        // Auto-select "unchanged" for update operation
        if ($(this).val() === "update") {
            $("#order_status").val("unchanged");
        }
    });
    setIdFieldsState($("#operation-select").val()); // initial state

    // On page load, fetch and display all orders
    function loadAllOrders() {
        // $("#flash_message").empty(); //for showing update success message
        let ajax = $.ajax({
            type: "GET",
            url: `/orders`,
            contentType: "application/json",
            headers
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
                    <td>${order.created_at ? order.created_at : ""}</td>
                    <td>${order.shipped_at ? order.shipped_at : ""}</td>
                </tr>`;
                $("#search_results tbody").append(row);
            });
            // flash_message("Orders loaded."); //commented out to avoid showing message on page load when update is successful
        });
        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    }

    // Call this function on page load
    loadAllOrders();

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
                headers
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

            if (!order_id) {
                flash_message("Order ID is required for update.");
                return;
            }

            // First, get the current order data
            let getAjax = $.ajax({
                type: "GET",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                headers
            });

            getAjax.done(function (currentOrder) {
                // Prepare update data - only include fields that are not empty
                let updateData = {};

                // Only update customer_id if it's not empty
                if (customer_id && customer_id.trim() !== "") {
                    updateData.customer_id = customer_id;
                } else {
                    updateData.customer_id = currentOrder.customer_id;
                }

                // Only update status if it's not "unchanged"
                if (status && status !== "unchanged") {
                    updateData.status = status;
                } else {
                    updateData.status = currentOrder.status;
                }

                // Keep existing order_items
                updateData.order_items = currentOrder.order_items || [];

                // Send update request
                let updateAjax = $.ajax({
                    type: "PUT",
                    url: `/orders/${order_id}`,
                    contentType: "application/json",
                    data: JSON.stringify(updateData),
                    headers
                });

                updateAjax.done(function (res) {
                    update_form_data(res);

                    // Compare changes and show detailed message
                    let changes = [];
                    function capitalize(s) {
                        if (!s) return s;
                        return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
                    }
                    if (customer_id && customer_id.trim() !== "" && customer_id != currentOrder.customer_id) {
                        changes.push(`customer_id from "${currentOrder.customer_id}" to "${customer_id}"`);
                    }
                    if (status && status !== "unchanged" && status != currentOrder.status) {
                        changes.push(`status from "${capitalize(currentOrder.status)}" to "${capitalize(status)}"`);
                    }

                    if (changes.length > 0) {
                        flash_message(`Update successful. Modified: ${changes.join(", ")}`);
                    } else {
                        flash_message("Update successful. No changes were made.");
                    }

                    // Refresh the results table after a short delay to let user see the message
                    setTimeout(function () {
                        loadAllOrders();
                    }, 2000); // 2 second delay
                });

                updateAjax.fail(function (res) {
                    flash_message(res.responseJSON.message);
                });
            });

            getAjax.fail(function (res) {
                flash_message("Order not found: " + res.responseJSON.message);
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
                headers
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
                contentType: "application/json",
                headers
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
                contentType: "application/json",
                headers
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
    // Retrieve order by order_id when clicking the retrieve button next to order_id
    // ****************************************
    $("#retrieve-btn").click(function (e) {
        e.preventDefault();
        let order_id = $("#order_id").val();
        if (!order_id) {
            flash_message("Order ID is required for retrieve.");
            return;
        }
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            headers
        });
        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Order retrieved successfully");
        });
        ajax.fail(function (res) {
            flash_message(res.responseJSON.message);
        });
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
