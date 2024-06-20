# Long Short-Term Memory Neural Network Stock Market Price Predictor.

### STACK
<ul> 
    <li> Python 3.10 </li>
    <li> Flask </li>
    <li> Tensorflow </li>
    <li> Keras </li>
    <li> Pandas </li>
    <li> Alpaca Markets Trade API </li>
</ul>

## How to run this application
<ol>
    <li> Create virtual environment </li>
    <li> Install requirements </li>
    <li> Create .env file with </br>
    * ALPACA_API_KEY = '(your alpaca api key)'</br>
    * ALPACA_SECRET_KEY = '(your alpaca api secret key)'</br>
    * BASE_URL = 'https://paper-api.alpaca.markets'
    <li> FLASK_APP=app </li>
    <li> FLASK_ENV=development </li>
    <li> $flask run </li>
    <li> http://127.0.0.1:5000/ </li>
    <li> Input stock symbol and press predict, if you have multiple symbols click Add Another Symbol button </li>
</ol>

