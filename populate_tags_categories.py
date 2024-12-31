# populate_tags_categories.py

import os
import django

# Set the environment variable for the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myblog.settings")  # Replace 'myblog' with your project name

# Initialize Django
django.setup()

# Now import your models after initializing Django
from blog.models import Tag, Category  # Replace 'blog' with your app name

def populate_tags_and_categories():
    # Tags to insert
    tags = [
        "Remote Work",
        "Artificial Intelligence",
        "Sustainable Fashion",
        "Personal Finance",
        "Healthcare Innovation",
        "Technology Trends",
        "Marketing Strategy",
        "Data Science",
        "AI in Healthcare",
        "Future of Work"
    ]
    
    # Categories to insert
    categories = [
        {"name": "Technology", "description": "Blogs related to the latest in technology, innovations, and tools."},
        {"name": "Healthcare", "description": "Exploring advancements in healthcare, including AI, medical technology, and treatments."},
        {"name": "Finance", "description": "Personal finance, investment, and financial management tips."},
        {"name": "Fashion", "description": "Sustainable fashion trends and the intersection of technology and fashion."},
        {"name": "Marketing", "description": "Strategies and insights on effective marketing and branding."},
        {"name": "Remote Work", "description": "Insights and tools to enhance productivity and efficiency in remote work settings."},
        {"name": "AI & Machine Learning", "description": "The role of AI and machine learning across industries, particularly in healthcare, finance, and more."},
        {"name": "Entrepreneurship", "description": "Tips and guidance on building and managing a business, especially in the tech space."},
        {"name": "Career Development", "description": "Career tips, growth strategies, and the evolution of the modern workplace."},
        {"name": "Innovation", "description": "Exploring the impact of emerging technologies and innovations in various industries."}
    ]

    # Insert tags into the database
    for tag_name in tags:
        Tag.objects.get_or_create(name=tag_name)
        print(f"Tag '{tag_name}' inserted successfully.")

    # Insert categories into the database
    for category in categories:
        Category.objects.get_or_create(
            name=category["name"],
            description=category["description"]
        )
        print(f"Category '{category['name']}' inserted successfully.")

if __name__ == "__main__":
    populate_tags_and_categories()
