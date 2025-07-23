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
        When I copy the "order_id" field
        And I press the "Clear" button
        Then the "order_id" field should be empty
        And the "product_id" field should be empty
        And the "orderItem_quantity" field should be empty
        When I paste the "order_id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "1" in the "product_id" field
        And I should see "10" in the "orderItem_quantity" field
        And I should see "Placed" in the "order_status" dropdown
        And I should see "11" in the "orderItem_id" dropdown


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

Scenario: Retrieve an existing Order by order_id
    When I visit the "Home Page"
    And I get the first order id from the results
    And I select "Retrieve" in the "operation-select" dropdown
    And I set the "order_id" to "{first_order_id}"
    And I press the "Retrieve" button
    Then I should see "Order retrieved successfully" in the message
    And the "customer_id" field should not be empty
    And the "product_id" field should not be empty
    And the "orderItem_quantity" field should not be empty
    And the "order_status" field should not be empty
    And the "orderItem_id" field should not be empty