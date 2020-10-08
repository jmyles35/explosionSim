# explosionSim - Explosions and Such

[Project Writeup](project-writeup.pdf)

### Project Members

*   Keenan McConkey
*   Austin Khorram
*   Justin Myles

*   Coleman Kaps
*   Esther Lin

### Project Description

Apart from military applications, various engineered products rely on explosions, or their ability to withstand them, in order to function. The most obvious example is the internal combustion engine, where thousands of controlled explosions happen every minute. Here, knowledge of the force on the seals and piston, as well as the propagation of the shock waves and changes in temperature, is extremely important for design. Even a rocket can be modelled as a controlled explosion.

We intend to model explosions and how they propagate using Lagrangian mechanics, as well as computational fluid dynamics. Using the Eulerian-Lagrangian approach, we will employ point particle simulations to predict the trajectory of particles after detonation. We also will investigate how these explosions affect the motion of free objects.

| Task                                     | Completion | Notes               |
| ---------------------------------------- | ---------- | ------------------- |
| Research explosion propagation           | Week 2     | See research papers |
| Simulate explosion propagation           | Week 4     |                     |
| Simulate Lagrangian for chosen objects   | Week 6     | Sphere              |
| Simulate Lagrangian for arbitrary objects | Week 9     |                     |
| Finalize simulation GUI                  | Week 9     |                     |

### Client - Frontend
The front is a single page application built with Vue.js. All supporting files have been added. Simulation visuals should be developed in the following locations:

-   /frontend/index.html
-   frontend/static/*
    -   Please don't touch the /js/* folder. smh idk I don't know why things don't work without it there. All needed library files are in the static folder though. 

How to develop the frontend:

-   First, download node and npm (node needs an account I think)

-   In order to view any changes applied to the frontend (changes in html files, js, etc.), npm needs to be run. You can choose either or of the commands:

    -   ```shell
        npm run build
        ```

        This command takes a snapshot of the current state of the project and packages it into the dist/ folder. Run this command when you want your frontend changes to be seen/implemented by the backend. 


    -   ```shell
        npm run dev
        ```

        Building your project everytime you make a small change can be slow and tedious. Use the dev feature to see your js/html code implement immediately. Just run this command, and start making changes to your frontend files. You will see them implemented immediately.


-   Viewing your changes: If you run the dev option, head over to the link given 

    ```shell
    Your application is running here: http://localhost:8080
    ```

    This is hosted on your laptop, with a web browser such as chrome or safari. Or, if you want to view your changes after building, run the python server. 

### Server - Backend
How to develop the Backend:

-   Put all files in the backend/
-   Run "python run.py" or "./run.py" in the project root directory to see changes. 
-   Connections between front and back will be implemented in run.py

Resources: Read up on Flask: http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application


### dist/ - the connection between client and server

This is the folder of built features from the front end. It is created when the front end is built with npm. The Python server in run.py will call files in this directory. This folder will get updated and remade everytime the build command is run. Remember to write your code in frontend/, not dist/! Or else they will get deleted!


### References:

*   “An Eulerian–Lagrangian approach for simulating explosions of energetic devices.” Computers & Structures, Pergamon, 26 Mar. 2007, www.sciencedirect.com/science/article/pii/S0045794907000429.
=======

