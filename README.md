<h2>Timetable scheduling solutions web application implemented in django</h2>

<p>
This is a WIP project, to create a timetabling service for schools.<br>
The core functionality of the application is / will be:
</p>
<ol>
    <li>Create an account and register a school</li>
    <li>Upload teacher/pupils/classrooms data for the year</li>
    <li>Upload the classes that must take place, and any classes that must take place at a certain time</li>
    <li>Set preferences for the timetable structure (e.g. when the best times for free periods are)</li>
    <li>The requirements / preferences are then formulated as a linear programming problem and a solver API is called</li>
    <li>Pupil and teacher timetables are available for viewing / download in the app</li>
</ol>
For more info, see the project wiki.
<hr>


<h2>Project setup</h2>

<h4>System requirements</h4>
<ul>
    <li>Python 3.11</li>
    <li>
        If using a mac with an Apple silicon chip, you will need Rosetta installed:<br>
        <code>softwareupdate --install-rosetta</code>
    </li>
    <li>Optionally, docker for running the production environment</li>
    
</ul>

<h4>Basic setup</h4>
<ol>
    <li>Fork and clone repository</li>
    <li>Setup virtual environment at project root (or alternatively, within /timetable_solutions)</li>
    <li>Install the dependencies from app-requirements.txt and test-requirements.txt with pip</li>
    <li>
        The project is configured to use pytest-django. To check the tests are passing, at src/timetable_solutions/:<br>
        <code>pytest</code>
    </li>
</ol>

<h4>Development setup</h4>
The local development setup uses a sqlite database, so to use the development server you just need to:
<ol>    
    <li>
        Migrate the models (the migrations are all committed)<br>
        <code>python manage.py migrate</code>
    </li>
    <li>Install the fixtures if you want some dummy data to view, by:<br>
        <code>cd timetable_solutions</code><br>
        <code>python manage.py load_all_fixtures</code>
    <li>
        Alternatively, create/upload your own data through the app.
    </li>
    <li>
        <code>python manage.py runserver</code><br>
    </li>
</ol>

<h4>Production setup</h4>
To run the production environment locally:
<ol>
    <li>
        Create a .env file in the project root, specifying all environment variables referenced in docker-compose.yml
    </li>
    <li>
        Note that the default docker platform on some macs is different to on linux / other macs, and therefore
        <a href="https://stackoverflow.com/questions/65612411/forcing-docker-to-use-linux-amd64-platform-by-default-on-macos">
            requires special treatment of the DEFAULT_DOCKER_PLATFORM environment variable. 
        </a>Note also running docker-compose build before docker-compose up seems to be a requirement.<br>
        From the project root build the docker images and spin up the containers:<br>
        <code>docker-compose build</code><br>
        <code>docker-compose up</code>
    </li>
</ol>

<hr>
