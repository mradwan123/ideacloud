
```
  _____      _                 _____  _                    _ 
 |_   _|    | |               / ____|| |                  | |
   | |    __| |  ___   __ _  | |     | |  ___   _   _   __| |
   | |   / _` | / _ \ / _` | | |     | | / _ \ | | | | / _` |
  _| |_ | (_| ||  __/| (_| | | |____ | || (_) || |_| || (_| |
 |_____| \__,_| \___| \__,_|  \_____||_| \___/  \__,_| \__,_|
```

## Project Overview

**Idea Cloud is a collaborative web platform designed to bridge the gap between people with ideas and people able to implement those ideas. 
It provides an environment where non-technical users can pitch project ideas, while developers and creators can form organized groups to bring those visions to life.**

**Project Context:** This application serves as the final capstone project for a 1-year Python backend development course. It was built collaboratively by a team of 5 developers over a period of 6 weeks.

This project was developed over a 6-week timee frame by a team of 5 developers.
Our goal was to create a robust, scalable backend using Django. It was a learning experience for all of us and there's still a lot of features that could be added.

_Note: The primary focus of this project is the backend architecture, API design, and database management. The included frontend is strictly presentational to show what the website could look like.


## Core Features & Functionality

- **Project Pitching & Collaboration:** 
	- Users can post detailed project ideas and form dedicated groups to bring those ideas to life with other collaborators.

- **Social System & Moderation:**
	- Includes a full "Like" and comment system for community feedback, protected by a custom profanity filter to keep content clean.

- **Optimized Database Queries:**
	- We used `.annotate()`, `exists`, and `OuterRef` subqueries to handle like counts and user-status flags efficiently, avoiding the "N+1" performance issues that slow down APIs.

- **User Management & Security:** 
	- Built a custom user model and implemented Token-based authentication (DRF) for secure registration and login flows.

- **Automated File Cleanup:** 
	- Custom logic overrides the model's `delete()` method to automatically remove orphaned image files from the server's storage when a project is deleted.

- **Base64 Image Processing:** 
	- The backend accepts Base64 strings for images, validates that they are actually JPGs, and saves them directly to the server.

- **Input Sanitization:** 
	- We use `to_internal_value()` in our serializers to strip HTML tags and trim unnecessary whitespace before any data hits the database.

- **Smart Permission Logic:** 
	- Implemented a 15-minute window for editing comments and a relational locking system that prevents projects or groups from being modified once they are marked as "Finished".

- **Live API Documentation:** 
	- Integrated Swagger so anyone can explore and test the backend endpoints directly through the browser.


## Tech Stack

| Component<br>       | Technology                    |
| ------------------- | ----------------------------- |
| **Backend**         | Python 3.14+, Django 6.0+     |
| **API Framework**   | Django REST Framework (DRF)   |
| **Frontend**        | HTML5, CSS3, Django Templates |
| **Database**        | PostgreSQL (Production/Local) |
| **Documentation**   | Swagger, Postman              |
| **Authentication:** | DRF Authtoken                 |

---

## Setup & Installation

### Prerequisites

- Python 3.14+
- PostgreSQL (Ensure a local instance is running)
- Git

### Installation Steps

1. **Clone the Repository**
```bash
git clone https://github.com/SlimariusSlimus/dci_final_project.git
cd idea_cloud
```

2. **Set up the Virtual Environment**
```bash
python -m venv env       # may be python3 on your system
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables** Rename the provided `example_dotenv` to `.env` in the root directory and update your configuration:
```bash
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=True
DATABASE_URL="local"
DB_NAME=final_project
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

5. **Initialize the Database** Create the database in PostgreSQL before running migrations:
```bash
# In your psql terminal or pgAdmin
CREATE DATABASE final_project;
```

Then create and apply the Django migrations:
(you may have to delete old migrations first)
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Static Files & Initial Data**
```bash
python manage.py collectstatic --noinput
```

7. **Run the Server**
```
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/'

---

## Testing & Quality Assurance

The backend features a comprehensive test suite with **91% code coverage**, ensuring the reliability of serializers, custom permissions, query logic, and user flows.

To execute the automated test suite and check coverage:

```bash
python manage.py test
coverage run manage.py test   # to run the test
coverage report               # to get a report of the testing in the console; add --skip-covered to only show files that don't have 100% coverage
coverage html                 # to get a browsable html file
```

---

## API Documentation & Integration

We designed the API to be easily consumed by any frontend or mobile application.

**Postman Collection:** 
	A fully configured Postman collection (`IdeaCloud.postman_collection.json`) is included in the root directory. 
	Import it into Postman to test all available endpoints, complete with example request bodies and authorization headers. (You will have to create tokens for the users manually and add them in the variables tab)

**Interactive Documentation:** 
	Once the local server is running, you can explore the Open API endpoints interactively via Swagger UI at `http://127.0.0.1:8000/swagger/`.

---

## Project Structure

- `projects/`: Core business logic for managing ideas, group formation, image handling, likes, and comments.

- `users/`: Custom user models, token authentication, and profile management.

- `config/`: Main project settings, URL routing, and custom image processing helpers.

- `front_end/`: Django views and templates serving the web UI.

- `static/` & `media/`: Storage for CSS, JS, global assets, and user-uploaded content.


## The Team

| Name      | GitHub Name                                           | Role(s) in the Project              |
| --------- | ----------------------------------------------------- | ----------------------------------- |
|           | [mamasitta](https://github.com/mamasitta)             | Teacher & Mentor                    |
| Mattis M. | [SlimariusSlimus](https://github.com/SlimariusSlimus) | Backend<br>Tech Lead                |
|           | [mradwan123](https://github.com/mradwan123)           | Scrum Master<br>Backend<br>Frontend |
|           | [Lamarr12345](https://github.com/Lamarr12345)         | Backend<br>Frontend                 |
|           | [LarkaFenrir](https://github.com/LarkaFenrir)         | Frontend                            |
|           | [alaakaroum](https://github.com/alaakaroum)           | Backend                             |
