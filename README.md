# MEET Website

IAP 2019 Project


## Getting Started

If you are on a Unix based system, and have python3 installed, simply type:
```
./build.sh
```
to deploy the site on your localhost. Please note that this WILL INSTALL virtualenv using pip3. 

If you are on a Windows based system, please check out the Installing section below.


### Prerequisites

You need python3 installed. Check out the instructions [here](https://realpython.com/installing-python/) to install python3 if you do not already have it on your system. 


### Installing

Once again, on a Unix based system, simply run (from terminal):

```
./build.sh
```

And open the localhost url that is printed out. 

However, on a Windows based system, you must do the following:

First, spend at least 20 minutes contemplating why you have made such a horrible decision.

Next, make sure that python3 is installed, by opening a command prompt and typing:

```
where python
```
or (depending on how many python versions you have on your machine)
```
where python3
```

You should see a file path printed, containing a python version of AT LEAST 3.0. 

Next, you need to install virtualenv:

```
pip install virtualenv
```
or (depending on how many python versions you have on your machine)
```
pip3 install virtualenv
```

Next (if you have not already done so), clone this repository:

```
git clone git@github.com/alexanderroot/meet-site
```

Hopefully, you already have git configured on your machine to allow for cloning (and have access to this repository). If not, follow the ssh directions [here](https://dev.to/landonp1203/how-to-properly-set-up-git-on-your-computer-33eo) and then repeat the above step. 

Next, we want to create a virtual environment that you can host the site on:

```
virtualenv meet-web
```

Please don't add that virtualenv to the github repository, I will always delete it in merge requests and I really don't want to deal with that. I.E. Don't do this in the meet-site directory.

Next, activate the virtual environment:
```
\path\to\env\Scripts\activate
```

Next, enter the meet-site directory and install the requirements into the virtual environment:

```
cd meet-site
```
and 
```
pip install -r requirements.txt
```
or (depending on how many python versions you have on your machine)
```
pip3 install -r requirements.txt
```

You should be all set for deployment now!


## Running the tests

Hah you think I'm this together already? Think again.


### Break down into end to end tests

Nope.


### And coding style tests

HAHAHAHAHA


## Deployment

```
python3 app.py
```
or
```
python app.py
```
(Assuming python is version 3).


## Website Deployment

Here's where some things get SUPER jank. Due to restirctions from Heroku's LOVELY service, there is no way (that I have found) to extract the database that has been updated via user interactions with the site. Therefore, I have installed a horrifyingly insecure backdoor. The url ending "/admin-problem-database" allows a GET request to receive the binary representation of the databse (yes I am aware of how horribly insecure that is). Luckily, there is no real reason this site needs to be entirely secure, though this backdoor makes me extremely nervous. Anyhoo, to extract the database at any given time, simply run:

```
curl -X POST -F "password=secretbackdoor" https://meet-website.herokuapp.com/admin-problem-database > storage.db
```

Commit this to master before the next deployment.


## Built With

* [Flask](http://flask.pocoo.org) - The web framework used
* [SQLAlchemy](https://www.sqlalchemy.org) - Database system


## Contributing

Please read [CONTRIBUTING.md](somelink) for details on our code of conduct, and the process for submitting pull requests to us.


## Versioning

IDK man.


## Authors

* **Alexander Root** - *Initial work* - [alexanderroot](https://github.com/alexanderroot)

* **Arnav Patel** - *Frontend Updates* - [arnav0312](https://github.com/arnav0312)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Acknowledgments

* Caleb
* Hope
* Arnav
* MEET


