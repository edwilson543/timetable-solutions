<h2>Timetable scheduling solutions web application implemented in django</h2>

<p>
This is a WIP project, to create a timetabling service for schools.<br>
The core functionality of the application is / will be:
</p>
<ol>
    <li>Create an account and register the school</li>
    <li>Upload teacher/pupils/classrooms data for the year</li>
    <li>Upload the classes that must take place, and any classes that must take place at a certain time</li>
    <li>Set priorities for the timetable structure (e.g. to maximise spread of each class throughout week)</li>
    <li>Formulate the timetabling problem as a linear programming problem</li>
    <li>Call a linear optimisation API</li>
    <li>Make the timetables created available for viewing / download in the app</li>
</ol>
<br>



<h2>Project setup</h2>
<ol>
    <li>Fork and clone repository</li>
    <li>Setup virtual environment</li>
    <li>Install the dependencies from requirements.txt (with pip is fine)</li>
    <li>
        Check tests are working - once in the timetable directory:<br>
        <code>python manage.py test</code>
    </li>
    <li>
        Migrate the models (the migrations are all committed)<br>
        <code>python manage.py migrate</code>
    </li>
    <li>Install the fixtures if you want some dummy data to view, in the following order:
        <ol>
            <li>users.json</li>
            <li>pupils.json, teachers.json, classrooms.json, timetable.json</li>
            <li>classes.json</li>
        </ol>
    </li>
    <li>
        Alternatively, create/upload your own data through the app. Note that not all functionality has been
        implemented yet.
    </li>
</ol>