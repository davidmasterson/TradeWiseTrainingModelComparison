# Random Forest Model Neural Network Stock Market Purchase Recommender.
<p>About:
    This application is broken up into three different segments.
        1. A Random Forest Model Trainer
            Based on stock transaction data from a database
        2. A Predictor
            Based on current open positions in your database
        3. An Input your own Stock Symbols Section
            Input your own stock symbols and run them against the Trained Random Forest Model.
</p>
</hr>
<p> Future Additions:
    Add this into the already existing functionality of my automated algorithmic trading application.
    1. Determine purchase probability and automatically execute those purchases and sells.
    2. Configure the app to rerun the model trainer every time a new sell is executed , this makes the app learn over
    time and increase its success rate.
</p>
### STACK
<ul> 
    <li> Python 3.10 </li>
    <li> Flask </li>
    <li> Pandas </li>
    <li> Matplotlib</li>
    <li> Yahoo Finance API </li>
    <li> Alpaca Markets Trade API </li>
</ul>

## How to run this application
<ol>
    <li>Create a MySQL database</li>
    <li> Create virtual environment </li>
    <li> Install requirements </li>
    <li> Create .env file with </br>
    * ALPACA_API_KEY = '(your alpaca api key)'</br>
    * ALPACA_SECRET_KEY = '(your alpaca api secret key)'</br>
    * BASE_URL = 'https://paper-api.alpaca.markets'
    * SECRET = 'SET YOUR OWN SECRET KEY'
    <li> FLASK_APP=app </li>
    <li> FLASK_ENV=development </li>
    <li> $flask run </li>
    <li> http://127.0.0.1:5000/ </li>
</ol>


Just checking to see if Jenkins will auto 