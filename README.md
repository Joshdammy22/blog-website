```markdown
# Blog Website

A feature-rich blog website built with Django, designed to provide a platform for users to create, publish, and interact with blog content. Users can like posts, comment on them, follow other users, and receive notifications for various interactions.

## Features

### Core Features
- **Blog Creation**: Users can create blogs with options to save as drafts or publish immediately.
- **Rich Media Support**: Add images to blog posts for a visually engaging experience.
- **User Authentication**: Secure user registration and login functionality.
- **Comments**: Users can comment on blog posts, and the author gets notified.
- **Likes**: Users can like/unlike posts, with notifications sent to the author.
- **Follow System**: Follow other users and receive notifications when followed.
- **Notifications**: A real-time notification system for likes, comments, and follows.

### Advanced Features
- **Responsive Design**: Built with mobile-first principles for optimal viewing on any device.
- **Dynamic Slug Generation**: SEO-friendly URLs for each blog post.
- **Draft & Publish Management**: Manage blog post visibility with draft and publish options.
- **Profile System**: View user profiles and follow/unfollow users.
- **Admin Panel**: Manage users, posts, comments, and notifications with Django's built-in admin interface.

---

## Project Setup

### Prerequisites
- Python 3.8+
- Django 4.2+
- Git
- Virtual Environment (e.g., `venv`)

### Installation

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
   Open your browser and go to `http://127.0.0.1:8000`.

---

## Usage

1. **Register and Login**:
   - Create an account or log in to access blogging features.

2. **Create Blogs**:
   - Navigate to the "Create Blog" page.
   - Add a title, content, and an optional image.
   - Choose "Save as Draft" or "Publish."

3. **Interact with Blogs**:
   - Like, comment on posts, and follow other users.

4. **Manage Notifications**:
   - View your notifications for likes, comments, and follows.

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

---

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add a meaningful message"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Create a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Special thanks to the open-source community for their invaluable tools and libraries that made this project possible.
```