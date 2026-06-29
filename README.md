# effectz_ai_Assignment

This is a bot automation coded using Selenium with Python for incarnage.com web page from select the items with it's size to fill the basic details in the payment gateway and verify each detail entered through the process.

# How to Setup
Step 1 : Download the files into your local machine
Step 2 : Open the Assignment.py in VS Code
Step 3 : Change *search_items, Checkout_details* dictionaries as needed 
Step 3 : Install/Import the libraries.
Step 4 : Run the bot in terminal by *python Assignment.py*

# Notes
The website was not showing a captcha verification

# Example Demo
[Demo Video](https://github.com/user-attachments/assets/ec7d8481-e04a-49b2-9b3e-1813ccead844)

# Demo Output

***Search***
Logo display success
Search button clicked
Search input Displayed
Entered: tee
Results page is visible
Found 'Seamless crew neck' on page 1
***click the product***
Clicked product: Seamless crew neck
Add to cart icon is visible
Product name: SEAMLESS CREW NECK
***select size***
Size 'M' was selected for 'Seamless crew neck'
***add to cart***
Add to cart button clicked
Cart close button clicked
***search second item***
Search button clicked
Search input Displayed
Entered: shorts
Results page is visible
Found 'Carnage retro short' on page 1
***click on the product***
Clicked product: Carnage retro short
Add to cart icon is visible
Product name: CARNAGE RETRO SHORT
***select size***
Size 'L' was selected for 'Carnage retro short'
Add to cart button clicked
Cart close button clicked
***validate the cart***
Cart is open for validation
[Check 1] Expected items: 2, Actual items: 2 -> OK
[Check 2] Expected products: ['carnage retro short', 'seamless crew neck']
[Check 2] Cart products:     ['carnage retro short', 'seamless crew neck'] -> OK
[Check 3] Calculated sum: 8200.00, Cart total: 8200.00 -> OK
PASS
***checkout***
Checkout button clicked
Buy more popup closed
***enter details***
Email address entered
tab to country
tab to country
tab to country
Tab to first name
Tab to first name
Checkout details entered
***verify checkout details***
[email_address] Expected: 'jithmi328@gmail.com', Actual: 'jithmi328@gmail.com' -> PASS
[first_name] Expected: 'Jithmi', Actual: 'Jithmi' -> PASS
[last_name] Expected: 'Nanayakkara', Actual: 'Nanayakkara' -> PASS
[address] Expected: '180B, Mabodala, Veyangoda', Actual: '180B, Mabodala, Veyangoda' -> PASS
[city] Expected: 'Gampaha', Actual: 'Gampaha' -> PASS
[postal_code] Expected: '11114', Actual: '11114' -> PASS
[phone_number] Expected: '0762443450', Actual: '076 244 3450' -> PASS
[country] Expected: 'Sri Lanka', Actual: 'Sri Lanka' -> PASS
PASS
