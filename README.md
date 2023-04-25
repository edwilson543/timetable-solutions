<h1>School timetable scheduling web app</h1>

<h3>
This is a project I did between 2022/23 to provide a timetabling service for schools,
implemented using django and deployed at
<a href="https://timetable-solutions.com">timetable-solutions.com</a>
</h3>

<h5>Core functionality:</h5>
<ol>
    <li>Register as a user to the site and register a school</li>
    <li>Add and manage school data - pupils, teachers, lessons, etc.</li>
    <li>Define one or more timetable structures (when lessons can take place)</li>
    <li>Define how many slots within these structures each lesson needs per week</li>
    <li>Create different sets of timetables that can be browsed in the site</li>
</ol>

<h5>Core teach stack:</h5>
<ul>
    <li>Django in the backend</li>
    <li>Django templates, htmx and bootstrap for the frontend</li>
    <li>PuLP / COIN API for linear programming, which is how the timetabling problems are expressed / solved</li>
    <li>Pytest / webtest (django) / factory boy for testing</li>
    <li>CI / CD with GitHub actions and dockerhub</li>
    <li>
        Production environment is hosted on Digital Ocean, using PostgreSQL for the db, gunicorn as the WSGI server,
        and nginx as the web server. The app runs in a few docker containers, including a container running
        Let's Encrypt for certification
    </li>
</ul>

<hr>


<h2>Setup</h2>

<h4>System requirements</h4>
<ul>
    <li>Python 3.11</li>
    <li>
        If using a mac with an Apple silicon chip, you will need Rosetta installed:<br>
        <code>softwareupdate --install-rosetta</code>
    </li>
    <li>Optionally, docker for running a production-like environment locally</li>

</ul>

<h4>Basic setup</h4>
<ol>
    <li>Fork and clone repository</li>
    <li>Setup a virtual environment at project root (or alternatively, within /timetable_solutions)</li>
    <li>
        <b>pip install</b>
        the dependencies from app-requirements.txt, test-requirements.txt and dev-requirements.txt
    </li>
    <li>
        Check the tests are passing; with `timetable_solutions` as the working directory:<br>
        <code>pytest</code>
    </li>
    <li>
        Install the pre-commit hooks, from project root:<br>
        <code>pre-commit install</code>
    </li>
</ol>

<h4>Development setup</h4>
Local development works with SQLite, so no db setup is needed.
To run the app locally, again with
`timetable_solutions` as the working directory:
<ol>
    <li>
        Migrate the models:<br>
        <code>python manage.py migrate</code>
    </li>
    <li>
        Create some dummy data, if you want it:<br>
        <code>python manage.py create_dummy_data --school-access-key=1</code>
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
        settings at `timetable_solutions/base_files/settings/production.py`
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
