<h1>School timetable scheduling web application</h1>

<h3>
This is a work in progress project to provide a timetabling service for schools, 
implemented using django and deployed at
<a href="http://timetable-solutions.com">timetable-solutions.com</a>
</h3>

<h5>
Core functionality:
</h5>
<ol>
    <li>Create an account and register a school with the site</li>
    <li>Upload teacher, pupil and classroom data</li>
    <li>Upload the classes that must take place, for how many periods and double periods per week,
        as well as any classes that must take place at a certain time</li>
    <li>Set preferences for the timetables that will be generated (e.g. when the best times for free periods are)</li>
    <li>View and download the pupil and teacher timetables (eventually email these out too)</li>
</ol>

<h5>Tech stack:</h5>
<ul>
    <li>Django for the web application backend logic</li>
    <li>PuLP for linear programming (a third-party python package) with COIN API configured as the solver,
    to generate the timetable solutions</li>
    <li>Django templates and external css for the frontend</li>
    <li>Pytest-django for running the test suite</li>
    <li>Continuous integration with GitHub actions; running the test suite on git pushes and pull requests </li>
    <li>Continuous deployment with GitHub actions, Docker and Docker Hub, to Digital Ocean</li>
    <li>In production, a PostgreSQL database is used, and for development a SQLite3 database</li>
    <li>In production, gunicorn is used as the application server, and nginx as the web server</li>
</ul>

<hr>


<h2>Project setup</h2>

<h4>System requirements</h4>
<ul>
    <li>Python 3.11</li>
    <li>
        If using a mac with an Apple silicon chip, you will need Rosetta installed:<br>
        <code>softwareupdate --install-rosetta</code>
    </li>
    <li>Optionally, docker for running the production environment locally</li>
    
</ul>

<h4>Basic setup</h4>
<ol>
    <li>Fork and clone repository</li>
    <li>Setup virtual environment at project root (or alternatively, within /timetable_solutions)</li>
    <li>
        <b>pip install</b>
        the dependencies from app-requirements.txt, test-requirements.txt and dev-requirements.txt 
    </li>
    <li>
        Check the tests are passing; wit``h /t``imetable_solutions as the working directory:<br>
        <code>pytest</code>
    </li>
    <li>
        Install the pre-commit hooks, from project root:<br>
        <code>pre-commit install</code>
    </li>
</ol>

<h4>Development setup</h4>
The local development setup uses a SQLite database. So to run the app from the development server, with
timetable_solutions as the working directory:
<ol>    
    <li>
        Migrate the models:<br>
        <code>python manage.py migrate</code>
    </li>
    <li>
        Install the fixtures if you want some dummy data to view 
        (alternatively, create / upload your own data through the app):<br>
        <code>python manage.py load_all_fixtures</code>
    </li>
    <li>
        Run the development server:<br>   
        <code>python manage.py runserver</code><br>
    </li>
</ol>

<h4>Production setup</h4>
You can run an environment equivalent to the production environment, using local docker containers:
<ol>
    <li>
        Create a .env file in the project root, specifying all environment variables referenced in the production
        settings at timetable_solutions/base_files/settings/production.py
    </li>
    <li>
        Build the docker images - with the project root as your working directory:<br>
        <code>docker-compose -f docker-compose.dev.yml build</code>
    </li>
    <li>
        Spin up the docker containers:<br>
        <code>docker-compose -f docker-compose.dev.yml up</code>
    </li>
</ol>

<hr>
