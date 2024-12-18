# User Management (Final Project)

## Reflection

Throughout this course, I was exposed to many useful software development tools and techniques actively used in the industry. These encompassed aspects of the Twelve-Factor App methodology that allow production-grade applications to be scalable, portable, and maintainable.

In this course we explored source control best practices and environment configurations. These are essential to working collaboratively on a project with other developers and testers. This was also pertinent for keeping a clean and working production environment that can be deployed via a CI/CD pipeline.

Working out of feature branches when developing new functionality or working out of an issue branch allows for appropriate separation that restricts collaborators from breaking important parts of the working program. Submitting pull requests to resolve issues or integrate new features offers a layer of quality control in which another collaborator can review changes before the decision is made to merge. 

Environment variables and secrets are one of the most significant security-related features between local and cloud environments. Putting sensitive information such as access tokens, keys, and login information is a security risk that could potentially put companies in danger of losing their data. That is why it is standard practice to store these values safely and securely.

Perhaps one of the most important parts of this course as far as code structure goes, was implementing Object Oriented Programming in a Read-Evaluate-Print-Loop program. Creating REPL applications serve as powerful tools for other developers or system administrators that may have to conduct tasks such as database migrations. Developing this with an object-oriented approach helped build a solid understanding of OOP principles. 

Since object-oriented design emulates to real-world concepts, it is considered a reasonable way to organize a program, keeping all related data and operations together and abstracting implementation from other parts of the program. This, combined with sufficient logging streamlines the debugging process across an application.

The value and knowledge gained from this project and this course is useful because it exposes students to the some of the gaps in knowledge that exist even after completing an undergraduate degree in a related field. The knowledge jump from school to industry is significant and this exposure definitely aids in that effort.

## Feature
[User Profile Picture Uploading with MinIO](https://github.com/adrianaska0/user_management/blob/main/app/routers/user_routes.py)

## Tests
[Minio Tests](https://github.com/adrianaska0/user_management/blob/main/tests/test_minio.py)
<br/><br/>
[Upload User Profile Picture Tests](https://github.com/adrianaska0/user_management/blob/main/tests/test_api/test_users_api.py)

## Issues
[Profile Picture Endpoint](https://github.com/adrianaska0/user_management/issues/1)
<br></br>
[Upload Profile Pic Error (Workflow)](https://github.com/adrianaska0/user_management/issues/3)
<br/><br/>
[NameError in Profile Pic Test](https://github.com/adrianaska0/user_management/issues/6)
<br/><br/>
[User Profile Pic Endpoint Missing Response Model](https://github.com/adrianaska0/user_management/issues/8)
<br/><br/>
[Delete User Endpoint Missing Response Model](https://github.com/adrianaska0/user_management/issues/10)

## Docker
[User Management Repo (Docker)](https://hub.docker.com/repository/docker/adrianaska0/user_management/general)
