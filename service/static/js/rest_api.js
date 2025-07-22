$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#customer_id").val(res.customer_id);
        $("#order_status").val(res.status);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_id").val("");
        $("#customer_id").val("");
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

    $("#create-btn").click(function () {
        let customer_id = $("#customer_id").val();
        let status = $("#order_status").val();

        let data = {
            "order_items": []
        };

        if (customer_id) {
            data.customer_id = parseInt(customer_id);
        }

        if (status) {
            data.status = status;
        }

        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {
        let order_id = $("#order_id").val();
        if (order_id == "") {
            flash_message("Please enter an Order ID")
            return;
        }
        let customer_id = $("#customer_id").val();
        let status = $("#order_status").val();

        let data = {};
        if (customer_id) {
            data.customer_id = parseInt(customer_id);
        }
        if (status) {
            data.status = status;
        }

		if (Object.keys(data).length === 0) {
			flash_message("Please fill out one or more fields to update");
			return;
		}

        let ajax = $.ajax({
			type: "PUT",
			url: "/orders/" + order_id,
			contentType: "application/json",
			data: JSON.stringify(data)
		})

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {
        let order_id = $("#order_id").val();

        if (order_id) {
            let ajax = $.ajax({
                type: "GET",
                url: "/orders/" + order_id,
                contentType: "application/json"
            })

            ajax.done(function(res){
                update_form_data(res)
                flash_message("Success")
            });

            ajax.fail(function(res){
                clear_form_data()
                flash_message(res.responseJSON.message)
            });
        } else {
            flash_message("Please enter an Order ID")
        }
    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {
        let order_id = $("#order_id").val();

        if (order_id) {
            let ajax = $.ajax({
            type: "DELETE",
            url: "/orders/" + order_id,
            contentType: "application/json"
            })

            ajax.done(function(res){
                clear_form_data()
                flash_message("Order has been Deleted!")
            });

            ajax.fail(function(res){
                flash_message("Server error!")
            });
        } else {
            flash_message("Please enter an Order ID")
        }
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        clear_form_data();
        $("#search_results_body").empty();
        flash_message("");
    });

    // ****************************************
    // Search for an Order
    // ****************************************

    $("#search-btn").click(function () {
        let customer_id = $("#customer_id").val();
        let status = $("#order_status").val();
        let queryString = ""
        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&'
            }
            queryString += 'status=' + status
        }

        let ajax = $.ajax({
            type: "GET",
            url: "/orders?" + queryString,
            contentType: "application/json"
        })

        ajax.done(function(res){
            $("#search_results_body").empty();
            let table = $("#search_results_body");
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                let row = `<tr><td>${order.id}</td><td>${order.customer_id}</td><td>${order.status}</td><td>${order.created_at}</td><td>${order.shipped_at || ''}</td></tr>`;
                table.append(row);
            }
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
})
