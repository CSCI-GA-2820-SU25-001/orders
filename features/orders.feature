Feature: The Order service back-end
    As a Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my orders

Background:
    Given the following orders
        | order_id       | product_id | quantity | status   | orderItem_id |
        | 1              | 1          | 10       | placed   | 11           |
        | 2              | 2          | 20       | shipped  | 12           |
        | 3              | 3          | 1        | returned | 13           |
        | 4              | 4          | 50       | canceled | 15           |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Order
    When I visit the "Home Page"
    And I set the "OrderId" to "1"
    And I set the "ProductId" to "1"
    And I set the "Quantity" to "10"
    And I set the "OrderItemId" to "10"
    And I select "Placed" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "ProductId" field should be empty
    And the "Quantity" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1" in the "ProductId" field
    And I should see "10" in the "Quantity" field
    And I should see "Placed" in the "Status" dropdown
    And I should see "11" in the "OrderItemId" dropdown