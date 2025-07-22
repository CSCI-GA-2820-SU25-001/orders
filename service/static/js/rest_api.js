$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#orderItem_id").val(res.itemId)
        $("#product_id").val(res.productId)
        $("#quantity").val(res.quantity);
        if (res.status == "canceled") {
            $("#order_status").val("canceled");
        } else if(res.status == "shipped"){
            $("#order_status").val("shipped");
        } else if(res.status == "returned"){
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
        $("#quantity").val("");
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

    $("#create-btn").click(function () {

        let order_id = $("#order_id").val();
        let orderItem_id = $("#orderItem_id").val();\
        let quantity = $("#quantity").val();
        let product_id = $("#product_id").val();
        let status = $("#order_status").val() == "placed" || "shipped" || "returned" || "canceled";

        let data = {
            "order_id": order_id,
            "orderItem_id": orderItem_id,
            "quantity": quantity,
            "product_id": product_id,
            "status": status
        };

        $("#flash_message").empty();

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
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });



})
