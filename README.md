# Blog Website

A feature-rich blog platform built with Django, designed to enable users to create, publish, and engage with blog content seamlessly. 

---

## Features

### Core Features
- **Blog Creation**: Save drafts or publish blogs instantly.
- **Rich Media Support**: Add images to posts for an engaging experience.
- **User Authentication**: Secure registration and login.
- **Comments and Likes**: Interact with blogs via likes and comments.
- **Follow System**: Follow users and receive updates on their activities.
- **Notifications**: Get real-time updates for likes, comments, and follows.

### Advanced Features
- **Responsive Design**: Optimized for all devices.
- **SEO-Friendly Slugs**: Auto-generated slugs for better search visibility.
- **Draft Management**: Easily manage draft and published blogs.
- **Profile System**: View and manage user profiles.
- **Admin Panel**: Robust admin capabilities for management.

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

4. **Set Up the Database**:
   ```bash
   python manage.py migrate
   ```

5. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the Website**:
   Open your browser at `http://127.0.0.1:8000`.

---

## Usage

1. **Register/Login**: Securely log in or create a new account.
2. **Create Blogs**: Add titles, content, and images, then save as draft or publish.
3. **Interact**: Like and comment on blogs, follow users, and manage notifications.

---

## Project Structure

```
blog-website/
│
├── blog/                     # Main app directory
│   ├── migrations/           # Database migrations
│   ├── static/blog/          # App-specific static files
│   ├── templates/blog/       # App-specific templates
│   ├── models.py             # Data models
│   ├── views.py              # View functions
│   ├── forms.py              # Django forms
│   └── urls.py               # URL routes
│
├── static/                   # Global static files
├── media/                    # Uploaded files
├── templates/                # Global templates
├── .gitignore                # Ignored files for Git
├── LICENSE                   # License for the project
├── README.md                 # Documentation
├── manage.py                 # Django management script
└── requirements.txt          # Python dependencies
```

---

## Technologies Used

- **Framework**: Django 4.2
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default, easily extendable to PostgreSQL/MySQL)
- **Media Handling**: File and image uploads with Django
- **Notification System**: Custom notifications for user interactions

---

## Contributing

1. **Fork the Repository**: Start by forking the repo.
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature-branch-name
   ```
3. **Commit Changes**:
   ```bash
   git commit -m "Add detailed commit message"
   ```
4. **Push Branch**:
   ```bash
   git push origin feature-branch-name
   ```
5. **Submit Pull Request**: Open a pull request for review.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Special thanks to the open-source community and Django contributors for providing tools that make development efficient and enjoyable.

---
