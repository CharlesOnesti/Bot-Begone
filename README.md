<!-- Documentation for your project in the form of a Markdown file called README.md. This documentation is to be a user’s manual for your project. Though the structure of your documentation is entirely up to you, it should be incredibly clear to the staff how and where, if applicable, to compile, configure, and use your project. Your documentation should be at least several paragraphs in length. It should not be necessary for us to contact you with questions regarding your project after its submission. Hold our hand with this documentation; be sure to answer in your documentation any questions that you think we might have while testing your work. -->

# Directions to setup the website from source code
* Make sure that on your machine you already have git (https://git-scm.com/), python 3, and the Heroku CLI (https://devcenter.heroku.com/articles/heroku-cli) installed and setup.
* Pip install psycopg2 by running the command `pip install psycopg2-binary`.
* Create a Heroku account and add payment information - one of the endpoints will need a paid Heroku dyno because of its memory usage.
* Login to Heroku on you machine using the command `heroku login` and by following prompts.
* Create two Heroku apps by going to the Heroku apps page (https://dashboard.heroku.com/apps) and clicking the "New" button in the top right hand corner and then "Create new app".
* Give the apps any name you'd like but remember them since you will need their URLs later.
* On one of the apps go to its page, the resources tab, and then addons. Search for and add "Heroku Postgres" to the app, making sure that it is attached as "DATABASE".
* Once attached click on the postgres addon to go to its page, navigate to the "Settings" tab, and then click "View Credentials..."
* Copy the URI out of the credentials section and take note of it for later.
* Unzip the project file we submitted. Inside are two files that can each be pushed to Heroku apps using git.
* In the "cs50_final" project take the Postgresql URI and replace the URI on line 20 of app.py with yours and the URI on line 5 of configure_heroku_postgres.py.
* Replace the URL on line 143 with the URL of your app that does not have postgresql, making sure to keep `/checkbot` on the end of it.
* On lines 24 and 25 replace the values of the variables username and password with the username and password of your own Twitter account that you want to use to run the website.
* Go to settings and add these config variables to app with Postgresql:
  * `CHROMEDRIVER_PATH`, `/app/.chromedriver/bin/chromedriver`
  * `DATABASE_URL`, `postgres://mhheszaljfxliv:7cf27297de378774bdff97aadf0daf58cc20aa0dc5336fb27d5a74dac9911244@ec2-107-20-155-148.compute-1.amazonaws.com:5432/d44pn0a1kcts7q`
  * `GOOGLE_CHROME_BIN`, `/app/.apt/usr/bin/google_chrome`
* After, further down on the same page, add these two buildpacks:
  * `https://github.com/heroku/heroku-buildpack-chromedriver`
  * `https://github.com/heroku/heroku-buildpack-google-chrome.git`
* Python should also appear here as a buildpack after the code is pushed to them.
* Push the one named "cs50_final" and push it to the Heroku app with Postgresql attached.
* Push the one named "cs50_final_tensor" and push it to the other app.
* To facilitate this the command `heroku git:remote -a <NAME OF YOUR APP>` will be useful to add your Heroku apps as remotes when run in the same directory as the app you are trying to push. Alternately the git repo links can be found on the app pages as well.
* Return to the same Heroku app with Postgresql attached and under resources select "Change Dyno Type" and choose professional.
* Click on the 1X next to the web process listed on the same page and change the dyno type to "Standard-2X dynos".
* Run the script `configure_heroku_postgres.py` - these changes will take several minutes to become live.
* Everything should now be configured - navigate to the URL of your app with Postgresql attached to see it up!


# Directions for the user of the website
Welcome to our bot hunting game! You, the user, are challenged to find the highest number of Twitter botnets, or fake accounts on Twitter, that you can. Begin by clicking the Register button in the top right corner of the screen where you will be prompted to enter your name, username, and your password twice (in order to confirm your password). If you already have an account you will be prompted right away to log in or can navigate to the login page by clicking the Log In button in the top right corner. After logging in or registering, you will see the leaderboard which will display your placing and score compared with all other users.

You can navigate to the Submit Botnets button near the top left of the page and input a link to an account that you think is a botnet. To find a link, first navigate to a Twitter account on Twitter and copy the url to be the link to the account. An alert will display if the link has already been submitted and it will tell you if it has been identified as a bot or a human. If the link was not already submitted, after about a minute or so, the page will return how many botnets were found and your total number of botnets. If the bot hunting algorithm thinks that the Twitter account you submitted is not a botnet the page will tell you and no other accounts connected to the link you submitted will be searched because the probability of false positives goes up. Upon successful submission and identification of a bot the website will then update your score and the history table.

You can navigate to the history tab on the navigation bar to see a table containing the time you submitted the botnet, the additional botnets found from your 1 botnet submitted, and the number of points you got from that submission. You can navigate once to the leaderboard to see how you now compare against other users after submitting a botnet. You can also go to the Badges page to see what level Botnet Hunter you are (Beginner, Competent, Advanced, and Expert) and what badges you have earned (50 botnets found, 100 botnets found, 250 botnets found, 500 botnets found). You can view the table showing the number of botnets it takes to reach the next level. You can then navigate to the Report Botnets page to submit a link that is a confirmed Twitter botnet to researchers and Twitter so that they hopefully take them down.
