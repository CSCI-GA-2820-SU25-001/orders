Feature: The Order service back-end
    As a Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my orders

    Background:
        Given the following orders
            | order_id | customer_id | product_id | orderItem_quantity | status   | orderItem_id |
            | 1        | 101         | 1          | 10                 | Placed   | 11           |
            | 2        | 102         | 2          | 20                 | Shipped  | 12           |
            | 3        | 103         | 3          | 1                  | Returned | 13           |
            | 4        | 104         | 4          | 50                 | Canceled | 15           |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Order Demo RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create a Order
        When I visit the "Home Page"
        And I select "Create" in the "operation-select" dropdown
        And I set the "customer_id" to "101"
        And I set the "product_id" to "1"
        And I set the "orderItem_quantity" to "10"
        And I select "Placed" in the "order_status" dropdown
        And I press the "Apply" button
        Then I should see the message "Success"

    Scenario: Update an Order (only customer_id changed)
        When I visit the "Home Page"
        And I select "Update" in the "operation-select" dropdown
        When I get the first order id from the results
        And I set the "order_id" to "{first_order_id}"
        And I set the "customer_id" to "888"
        And I select "Unchanged" in the "order_status" dropdown
        And I press the "Apply" button
        Then I should see "successful" in the message

    Scenario: Update an Order (only status changed)
        When I visit the "Home Page"
        And I select "Update" in the "operation-select" dropdown
        When I get the first order id from the results
        And I set the "order_id" to "{first_order_id}"
        And I select "Shipped" in the "order_status" dropdown
        And I press the "Apply" button
        Then I should see "successful" in the message

    Scenario: Update an Order (no changes)
        When I visit the "Home Page"
        And I select "Update" in the "operation-select" dropdown
        When I get the first order id from the results
        And I set the "order_id" to "{first_order_id}"
        And I select "Unchanged" in the "order_status" dropdown
        And I press the "Apply" button
        Then I should see "successful" in the message
    
    Scenario: Cancel an Order
        When I visit the "Home Page"
        And I select "Update" in the "operation-select" dropdown
        When I get the first order id from the results
        And I set the "order_id" to "{first_order_id}"
        And I select "Canceled" in the "order_status" dropdown
        And I press the "Apply" button
        Then I should see "successful" in the message
