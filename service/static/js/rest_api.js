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

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });



})
