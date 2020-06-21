<!-- A “design document” for your project in the form of a Markdown file called DESIGN.md that discusses, technically, how you implemented your project and why you made the design decisions you did. Your design document should be at least several paragraphs in length. Whereas your documentation is meant to be a user’s manual, consider your design document your opportunity to give the staff a technical tour of your project underneath its hood. -->

# Website Design
When designing the webpage, we focused on making a fun game that would also serve an important function in identifying and reporting Twitter botnets (which will later be reported to researchers for their possible takedown). We made our theme blue and red with a robot as our icon on the tab. When the user tries to log in or register and does not input all the required elements an alert will appear directly below the input box. Having the alerts immediately display below the input box was a deliberate choice to notify the user of their mistake soon and not waste time by redirecting them to a new page.

Immediately after logging in, the leaderboard is displayed to show the user where they stand against other users. The leaderboard incorporates a placing that will automatically increment the number of places in the leaderboard. We included a page where the user can submit links to botnets and had the page return the botnets found in that submission as well as their current total. We thought as it was a game that the user would want to know as soon as possible how many botnets they had found rather than navigating to the history tab. We thought it was still important that the user could see a history of the times they submitted bots, how many botnets they found, and their points, perhaps to see which submission was most successful comparatively. We incorporated a Report Botnets page as well to give the user the opportunity to report botnet links to researchers. By having this page we hoped to give the website greater purpose and use than just a game. With users finding these fake accounts, we hope something useful can come of the game. An error immediately below the input box will display if someone does not input the link when reporting. An error also displays if the link submitted is not a bot or has not been submitted to the Submit Botnet page already.

To add to the game nature of the website, we created a badges page where the user could see what level of expertise they were at and what badges they had achieved so far. The purpose of the badges was to incentivize users to submit as many bots as they can. On the badges page it will read whether the user is a beginner, competent, advanced, or expert bot hunter and change the color of only beginner, competent, advanced, or expert keeping the rest of the sentence black. This was a purposeful choice to make the level stick out. We considered using bootstrap badges for the level title but thought just changing color appeared the best. For the badges, we changed the opacity so that it would be faded on the screen until the user earns the badge to make it more clear what they had achieved. We included a bootstrap table below the badges so the user can see where they stand in terms of expertise and how much more they need to increase their score to move levels.

We chose to use Flask, HTML, CSS, and JavaScript because for our website because of time constraints. A lot of the original setup is from the Finance pset.




# Algorithm Design
For the algorithm portion, we used the Keras and Tensorflow libraries to build an artificial neural network.  Our network had 8 input parameters and 2 hidden layers with 100 nodes and 50 nodes respectively.  Our inputs took Twitter account data along the metrics of tweet count, follower count, following count, like count, verified, default profile image, default profile background, and protected.  The output layer had 2 nodes normalized with a softmax function.  The output nodes are associated with a guess of bot or human and the guess is whichever has the higher activation.  The hidden layers are dense layers and are normalized with a Relu function.  To calculate loss, our model uses categorical crossentropy and the Adam optimizer.  

To train the AI we used 2,436 Twitter accounts that we found in online datasets.  The dataset we found online had a tsv file with Twitter account id's in one column and a 'human' or 'bot' string in the other column. We built a script (convert.py) to convert the account id's to twitter handles using the twitter API.  The twitter handles were used in the scraping_helpers.py to navigate to their account page with a web driver and scrape the relevant training data.  The data was then moved to the learn.py script where it was fed into the training algorithm for 400 epochs.  To test the classifier we then sent in the same dataset into the trained network and reached a 76% accuracy rate.

There are many reasons why the classifier is not perfectly accurate.  There is significant noise in the data, not all bots exhibit the same behavior and not all human accounts are similar either.  The machine algorithm is picking up on lots of unknown strong and weak correlations that indicate bot or human and it can sometimes be fooled.  The classifier is used to determine if an account that a user submits is a bot, and if so, if any of its followers are also bots.

We are picky about links we accept as bots because we don't want to lose trust of Twitter and the community that we are part of.

# Web Driver and Backend Design
The backend is composed of two Heroku Apps that work together, handling different parts of the processing to handle hosting the flask app and serving the website with gunicorn as our WSGI server, pulling data from Twitter via a custom scraper developed using BeautifulSoup and Selenium to let us get access to data Twitter would not usually let us have, and then checking if the account submitted is or is not a bot. We chose to use Heroku since the platform itself is relatively simple to use, scalable, stable, and had some of the groundwork already done that would allow us to get Selenium and TensorFlow working in a cloud environment in a timeframe that fit within the constraints of this project via its buildpack system. In this project, aside from the basic Python buildpack we also included two that allowed us to create an instance of the Google Chrome browser on one of our Heroku nodes, operating in a special gpu-disabled headless mode, and another that allowed us to connect Selenium to it via the webdriver. This allowed us to control the actions of Google Chrome with Python as if we were a user.

So why did we use Selenium instead of the Twitter API or a simpler way to fetch HTML code like requests? The Twitter API was not able to give us the type of data that we wanted in the quantity that we wanted it at since privacy reasons dictate that things we are able to scrape (such as follower count, like count, who the followers are, etc.) are not available via the API. Requests was not a feasible solutions since much of the data that we need was locked behind a login barrier and even if we did manage to log in with some smart cookie usage the JS on the page still wouldn't load when using requests, making it so we couldn't get all of the data that we needed because essential elements would not be displayed yet. I wrote a set of functions that streamline the scraping process in the app.py file and make it so that a browser only has to be initialized once on the server, enhancing speed. The speed of scraping is still relatively slow, constraining how many accounts we can look through before the connection with the user times out. However, all libraries are scalable and with some restructuring scraping could be done at scale, provided no overruns that trigger Twitters rate limiting. The scraper has been stability tested on over 2500 accounts and can deal with all types of failure cases, such as rate limiting, accounts being suspended, restricted content, and more. These 2500 scraped accounts were used to train the AI that makes the decision of if a submitted account is a bot or not. The account reporting feature is also implemented with Selenium on the backend, making the browser got and report the account while also sending a direct message to a researcher that specializes in the takedown of phishing accounts and botnets.

Storage is also handled by Heroku via its Postgresql addon. This was a fast, drop-in solutions but it did require some time to adjust the code to. When moving from SQLite3 to Postgres there need to be some syntactic changes since datatypes were not all directly analogous between the two databases and moving away from the cs50 library to psycopg2 required some adaptation as well. The reason for splitting our application between two apps was because when using TensorFlow, Keras, and Chrome webdriver on a single dyno while also trying to host the webserver at the same time things got more than just a little bit resource constrained. All packages included the approximate final size of our app was 340MB, shattering the 300MB soft cap that Heroku puts into place. Memory usage was also very high, at one point attempting to consume 171% of available memory. By splitting TensorFlow and Chrome webdriver tasks between the two servers and sending information between them using requests as well as upgrading the memory on the dyno that runs chrome we were able to resolve these issues and make an overall more stable app. When segmented the classification AI could also at some point be easily modified to be an API so anyone could check if a Twitter account is likely a bot.

# Sources
* Heroku environment configuration information for remote selenium found here: https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
* Assert documentation: https://lat.sk/2017/03/type-checking-assertions-exceptions-mypy/
* Beautiful soup documentation: https://www.dataquest.io/blog/web-scraping-tutorial-python/
* Selenium documentation: https://selenium-python.readthedocs.io/index.html
* Selenium scrolling: https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
* Dev tools xpath lookup command: https://testerlive.wordpress.com/2016/07/02/how-to-search-by-xpathcss-in-chrome-developer-tools/
* Join function: https://stackoverflow.com/questions/12453580/concatenate-item-in-list-to-strings
* Requests status code: https://realpython.com/python-requests/
* Selenium text only: https://stackoverflow.com/questions/12325454/how-to-get-text-of-an-element-in-selenium-webdriver-without-including-child-ele
* Selenium page source: https://stackoverflow.com/questions/7861775/python-selenium-accessing-html-source
* CSV documentation: https://docs.python.org/3/library/csv.html
* Heroku Postgres: https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python
* TensorFLow: https://www.tensorflow.org/
* SKLearn: https://scikit-learn.org/stable/documentation.html
* Numpy: https://numpy.org/doc/
* Pandas: https://pandas.pydata.org/pandas-docs/stable/
* Keras: https://keras.io/
* Training Datasets: https://botometer.iuni.iu.edu/bot-repository/datasets.html
* Heroku SQL documentation: https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python
* Heroku SQL connection documentation: https://devcenter.heroku.com/articles/connecting-to-heroku-postgres-databases-from-outside-of-heroku
* Psycopg documentation: http://initd.org/psycopg/docs/usage.html
* Pickle documentation: https://docs.python.org/3/library/pickle.html
* Buildpacks for Heroku: https://github.com/heroku/heroku-buildpack-chromedriver, https://github.com/heroku/heroku-buildpack-google-chrome
* Buildpack integration video: https://www.youtube.com/watch?v=Ven-pqwk3ec
* Buildpack integration documentation: https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-google-chrome, https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-chromedriver
* Psycopg documentation: http://initd.org/psycopg/docs/usage.html
* Autoincrementing key for Postgresql: https://chartio.com/resources/tutorials/how-to-define-an-auto-increment-primary-key-in-postgresql/
* Date datatypes documentation: https://www.postgresql.org/docs/9.1/datatype-datetime.html
* Floating pictures on Badges Page: https://owlcation.com/stem/how-to-align-images-side-by-side
* Bootstrap Table on Badges Page:-https://getbootstrap.com/docs/4.0/content/tables/
* Autoincrement Table on index.html: https://stackoverflow.com/questions/11026258/html-and-javascript-auto-increment-number
* Robot icon: http://newsphonereview.xyz/robot-cartoon-pictures/
* Help from this Ed post on not logging in constantly: atom://teletype/portal/0e709166-b91b-4748-b94f-2ebbc51f7bc2
* Converting strings into JSON: https://www.geeksforgeeks.org/python-convert-string-dictionary-to-dictionary/
* Flask response documentation: https://flask.palletsprojects.com/en/1.1.x/api/#flask.Response
* Request headers documentation: https://requests.readthedocs.io/en/master/user/quickstart/
* Report Phishing information: https://decentsecurity.com/malware-web-and-phishing-investigation/
* Requests usage documentation: https://realpython.com/python-requests/
* How to handle dropped connections with SQL: https://stackoverflow.com/questions/35651586/psycopg2-cursor-already-closed
* Building a Keras neural net: https://towardsdatascience.com/building-our-first-neural-network-in-keras-bdc8abbc17f5
* Learning about twitter bot detection: https://www.sciencedirect.com/science/article/pii/S0925231218308798#bib0009 and https://medium.com/@robhat/identifying-propaganda-bots-on-twitter-5240e7cb81a9
* How to send emails with Python: https://devanswers.co/allow-less-secure-apps-access-gmail-account/
* How to enable less secure apps: https://www.geeksforgeeks.org/send-mail-gmail-account-using-python/
* CS50 Finance Pset
