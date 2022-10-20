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
<ol>
    <li>Fork and clone repository</li>
    <li>Setup virtual environment</li>
    <li>Install the dependencies from requirements.txt (with pip is fine)</li>
    <li>
        The project is configured to use pytest-django. To check the tests are passing, at src/timetable_solutions/:<br>
        <code>pytest</code>
    </li>
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
</ol>
<hr>
