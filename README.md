---

# Blog Website

A feature-packed blog website designed to make sharing ideas, insights, and stories easy and enjoyable. Whether you’re a casual writer or an experienced blogger, this platform allows users to create, publish, interact with, and explore content in a vibrant community.

---

## Description

The Blog Website is a user-friendly platform for creating, sharing, and interacting with blog posts. It offers features like liking, commenting, following, and reacting to blog content. The platform also provides insightful analytics on blog performance, making it easier to enhance content and grow an audience. This website aims to provide a comprehensive toolset for bloggers, empowering them to manage their content, engage with readers, and expand their online presence.

---

## Why

Blogging is more than just publishing posts—it’s about building a community and tracking growth. The platform combines essential tools for successful blogging, such as secure authentication, social login, notifications, blog analytics, and a seamless interface. Designed to empower bloggers at any stage of their journey, this platform provides the necessary resources to manage blogs, interact with readers, and track performance. Whether starting out or scaling up, this tool offers everything needed to succeed in the blogging world.

---

## Quickstart

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/oladokedamilola/blog-website.git
   cd blog-website
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv env
   source env/bin/activate    # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Database**:
   - Apply migrations to initialize the database:
     ```bash
     python manage.py migrate
     ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**:
   Open the browser and go to `http://127.0.0.1:8000`.

---

## Usage

1. **Register and Login**:
   - Create an account or log in to access blogging features.
   - Use email/password or sign up with Google for a faster registration experience.

2. **Create Blogs**:
   - Navigate to the "Create Blog" page.
   - Add a title, content, and optional images.
   - Choose between "Save as Draft" or "Publish."

3. **Interact with Blogs**:
   - Like and comment on posts to engage with other bloggers.
   - Follow users and receive notifications for new content or interactions.

4. **View Analytics**:
   - Analyze blog post performance with charts generated using ApexCharts.

5. **Manage Notifications**:
   - Stay up to date with notifications for likes, comments, and follows.

---

## Contributing

Contributions are welcome to improve the platform. Here’s how to contribute:

1. **Fork the repository** to your own GitHub account.
2. **Create a new branch** for the feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. **Make the changes**: Ensure the code is clean, readable, and that documentation is updated as necessary.
4. **Commit the changes**:
   ```bash
   git commit -m "Add a meaningful message"
   ```
5. **Push the changes**:
   ```bash
   git push origin feature-name
   ```
6. **Open a pull request** with a detailed description of the changes.

---

## Project Structure

```
blog-website/
│
├── blog/                       # Blog app
│   ├── migrations/             # Database migrations
│   ├── static/blog/            # Static files (CSS, JS, Images)
│   ├── templates/blog/         # HTML templates
│   ├── models.py               # Data models
│   ├── views.py                # View functions
│   ├── forms.py                # Django forms
│   └── urls.py                 # URL routing
│
├── users/                      # User authentication app
│   ├── migrations/             # Database migrations
│   ├── models.py               # User models (Admin, Normal users, Social logins)
│   ├── forms.py                # Forms for registration, login, etc.
│   ├── views.py                # View functions for user management
│   └── urls.py                 # URL routing
│
├── static/                     # Global static files
├── media/                      # Uploaded files
├── templates/                  # Global templates
├── .gitignore                  # Git ignore file
├── README.md                   # Project documentation
├── manage.py                   # Django project management script
└── requirements.txt            # Python dependencies
```

---

## Technologies Used

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (default, can be replaced with PostgreSQL/MySQL)
- **Media Handling**: Django's File and Image fields
- **Notifications**: Custom notification model
- **Charts**: ApexCharts for blog analytics
- **Authentication**: Built-in Django auth, Google OAuth for social login
- **CAPTCHA**: Google reCAPTCHA for email verification and security

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Special thanks to @codewithsadee for providing the frontend repository, which served as the foundation for this project. The backend was integrated with Django, and additional frontend features and pages were added to enhance the platform. Acknowledgment also goes to the open-source community for their invaluable tools and libraries that made this project possible.

---
