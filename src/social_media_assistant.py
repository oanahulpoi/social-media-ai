import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading

# Load environment variables
_ = load_dotenv(find_dotenv())

@dataclass
class ScheduledPost:
    """Data class to store scheduling information"""
    platform: str
    content: str
    scheduled_time: datetime
    posted: bool = False

@dataclass
class Content:
    """Data class to store content information"""
    url: str
    title: str
    summary: str
    platform_posts: Dict[str, str]
    keywords: List[str]
    language: str
    scheduled_posts: List[ScheduledPost] = None
    posted: bool = False

    def __post_init__(self):
        if self.scheduled_posts is None:
            self.scheduled_posts = []

class SocialMediaAssistant:
    def __init__(self, model: str = "gpt-4o-mini", default_language: str = "en"):    
        """Initialize the Social Media Assistant with OpenAI client and configurations"""
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model = model
        self.default_language = default_language
        self.content_library: List[Content] = []
        self.platform_specs = {
            'x': {'max_length': 280, 'hashtag_limit': 3},
            'linkedin': {'max_length': 3000, 'hashtag_limit': 5},
            'facebook': {'max_length': 2000, 'hashtag_limit': 4}
        }
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ro': 'Romanian',
        }
        # Start the scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def extract_content(self, url: str) -> Dict[str, str]:
        """Extract content from a given URL"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and main content
            title = soup.title.string if soup.title else ""
            
            # Get main content
            article = soup.find('article') or soup.find('main') or soup.find('body')
            content = ' '.join([p.text for p in article.find_all('p')])
            
            return {'title': title, 'content': content}
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            return {'title': '', 'content': ''}

    def generate_platform_posts(self, content: str, title: str, language: str = None) -> Dict[str, str]:
        """Generate platform-specific posts using AI in specified language"""
        posts = {}
        language = language or self.default_language
        language_name = self.supported_languages.get(language, 'English')
        
        for platform, specs in self.platform_specs.items():
            platform_name = 'X' if platform == 'x' else platform.capitalize()
            prompt = f"""
            Create a {platform_name} post in {language_name} for the following content:
            Title: {title}
            Content: {content}
            
            Requirements:
            - Write the post in {language_name}
            - Maximum length: {specs['max_length']} characters
            - Maximum {specs['hashtag_limit']} relevant hashtags in {language_name}
            - Include a call to action in {language_name}
            - Make it engaging for {platform_name}'s {language_name}-speaking audience
            - Keep hashtags in English for better reach, but the post in {language_name}
            """
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"You are a professional social media manager who creates content in {language_name}."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                posts[platform] = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating {platform_name} post: {str(e)}")
                posts[platform] = ""
                
        return posts

    def extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content using AI"""
        try:
            prompt = f"""
            Extract 5-7 relevant keywords from this content:
            {content}
            
            Return only the keywords as a comma-separated list.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a keyword extraction specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            keywords = [k.strip() for k in response.choices[0].message.content.split(',')]
            return keywords
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            return []

    def is_duplicate(self, title: str, language: str) -> bool:
        """Check if content with same title and language already exists"""
        return any(
            content.title.lower() == title.lower() and content.language == language 
            for content in self.content_library
        )

    def schedule_post(self, content: Content, platform: str, scheduled_time: datetime) -> None:
        """Schedule a post for a specific platform"""
        if platform not in content.platform_posts:
            print(f"No content available for platform: {platform}")
            return

        scheduled_post = ScheduledPost(
            platform=platform,
            content=content.platform_posts[platform],
            scheduled_time=scheduled_time
        )
        content.scheduled_posts.append(scheduled_post)

        # Schedule the post
        schedule.every().day.at(scheduled_time.strftime("%H:%M")).do(
            self.publish_post, content, scheduled_post
        )

        print(f"Post scheduled for {platform} at {scheduled_time}")

    def publish_post(self, content: Content, scheduled_post: ScheduledPost) -> None:
        """Publish a post to the specified platform"""
        try:
            # Here you would implement the actual posting logic for each platform
            # For example, using platform-specific APIs
            platform_name = scheduled_post.platform.upper()
            print(f"Publishing to {platform_name}:")
            print(scheduled_post.content)
            
            scheduled_post.posted = True
            
            # Check if all scheduled posts are published
            if all(post.posted for post in content.scheduled_posts):
                content.posted = True
                
            # Save the updated state
            self.save_library()
            
        except Exception as e:
            print(f"Error publishing to {scheduled_post.platform}: {str(e)}")

    def process_url(self, url: str, language: str = None) -> Content:
        """Process a URL and generate all necessary content"""
        # Extract content from URL
        extracted = self.extract_content(url)
        
        # Use default language if none specified
        language = language or self.default_language
        
        # Check for duplicates
        if self.is_duplicate(extracted['title'], language):
            print(f"Content with title '{extracted['title']}' in {self.supported_languages[language]} already exists.")
            return None
        
        # Generate platform-specific posts
        posts = self.generate_platform_posts(extracted['content'], extracted['title'], language)
        
        # Extract keywords
        keywords = self.extract_keywords(extracted['content'])
        
        # Create Content object
        content = Content(
            url=url,
            title=extracted['title'],
            summary=extracted['content'][:200] + "...",
            platform_posts=posts,
            keywords=keywords,
            language=language
        )
        
        self.content_library.append(content)
        return content

    def save_library(self, filename: str = 'content_library.json') -> None:
        """Save content library to a JSON file"""
        library_data = []
        for content in self.content_library:
            scheduled_posts_data = [
                {
                    'platform': post.platform,
                    'content': post.content,
                    'scheduled_time': post.scheduled_time.isoformat(),
                    'posted': bool(post.posted)  
                }
                for post in content.scheduled_posts
            ]
            
            content_dict = {
                'url': content.url,
                'title': content.title,
                'summary': content.summary,
                'platform_posts': content.platform_posts,
                'keywords': content.keywords,
                'language': content.language,
                'scheduled_posts': scheduled_posts_data,
                'posted': bool(content.posted)
            }
            library_data.append(content_dict)
            
        with open(filename, 'w') as f:
            json.dump(library_data, f, indent=2)

    def load_library(self, filename: str = 'content_library.json') -> None:
        """Load content library from a JSON file"""
        try:
            with open(filename, 'r') as f:
                library_data = json.load(f)
                
            self.content_library = []
            for item in library_data:
                scheduled_posts = [
                    ScheduledPost(
                        platform=post['platform'],
                        content=post['content'],
                        scheduled_time=datetime.fromisoformat(post['scheduled_time']),
                        posted=post['posted']
                    )
                    for post in item.get('scheduled_posts', [])
                ]
                
                content = Content(
                    url=item['url'],
                    title=item['title'],
                    summary=item['summary'],
                    platform_posts=item['platform_posts'],
                    keywords=item['keywords'],
                    language=item.get('language', self.default_language),
                    scheduled_posts=scheduled_posts,
                    posted=item['posted']
                )
                self.content_library.append(content)
                
                # Reschedule any unposted content
                for post in scheduled_posts:
                    if not post.posted and post.scheduled_time > datetime.now():
                        schedule.every().day.at(post.scheduled_time.strftime("%H:%M")).do(
                            self.publish_post, content, post
                        )
                        
        except FileNotFoundError:
            print(f"No existing library found at {filename}")

    def delete_json_and_clear(self, filename: str = 'content_library.json'):
        """Delete the JSON file and clear the content library"""
        try:
            os.remove(filename)
            self.content_library = []
            print(f"Output file {filename} deleted and content library cleared successfully!")
        except FileNotFoundError:
            print(f"No output file found at {filename}, but content library was cleared!")
            self.content_library = []
        except Exception as e:
            print(f"Error deleting file: {str(e)}")

def main():
    """Main function to demonstrate the Social Media Assistant"""
    assistant = SocialMediaAssistant()
    
    # Load existing library if available
    assistant.load_library()
    
    while True:
        current_language = assistant.supported_languages[assistant.default_language]
        print("\nSocial Media Assistant Menu:")
        print(f"Current Language: {current_language}")
        print("-" * 30)
        print("1. Process new URL")
        print("2. View content library")
        print("3. Schedule posts")
        print("4. View scheduled posts")
        print("5. Save library")
        print("6. Delete JSON file and clear library")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            url = input("Enter URL to process: ")
            print("\nAvailable languages:")
            for code, name in assistant.supported_languages.items():
                print(f"{code}: {name}")
            language = input("\nEnter language code (press Enter for English): ").lower() or 'en'
            
            if language not in assistant.supported_languages:
                print(f"Unsupported language code. Using English.")
                language = 'en'
                
            content = assistant.process_url(url, language)
            if content:  # Only show content if it's not a duplicate
                print("\nProcessed Content:")
                print(f"Title: {content.title}")
                print(f"Language: {assistant.supported_languages[content.language]}")
                print("\nPlatform Posts:")
                for platform, post in content.platform_posts.items():
                    platform_name = 'X' if platform == 'x' else platform.upper()
                    print(f"\n{platform_name}:")
                    print(post)
                print("\nKeywords:", ", ".join(content.keywords))
            
        elif choice == '2':
            print("\nContent Library:")
            for i, content in enumerate(assistant.content_library, 1):
                print(f"\n{i}. {content.title}")
                print(f"URL: {content.url}")
                print(f"Language: {assistant.supported_languages[content.language]}")
                print(f"Summary: {content.summary}")
                print(f"Keywords: {', '.join(content.keywords)}")
                print("\nPlatform Posts:")
                for platform, post in content.platform_posts.items():
                    platform_name = 'X' if platform == 'x' else platform.upper()
                    print(f"\n{platform_name}:")
                    print(post)
                print("\nPosted:", "Yes" if content.posted else "No")
                print("-" * 80)
                
        elif choice == '3':
            if not assistant.content_library:
                print("No content available to schedule. Please process some URLs first.")
                continue
                
            print("\nAvailable content:")
            for i, content in enumerate(assistant.content_library, 1):
                print(f"{i}. {content.title} ({assistant.supported_languages[content.language]})")
            
            try:
                content_idx = int(input("\nSelect content number: ")) - 1
                content = assistant.content_library[content_idx]
                
                print("\nAvailable platforms:")
                for platform in content.platform_posts.keys():
                    platform_name = 'X' if platform == 'x' else platform.upper()
                    print(f"- {platform_name}")
                
                platform = input("\nEnter platform: ").lower()
                if platform not in content.platform_posts:
                    print("Invalid platform selected.")
                    continue
                
                # Get scheduling time
                try:
                    hour = int(input("Enter hour (0-23): "))
                    if hour < 0 or hour > 23:
                        raise ValueError("Hour must be between 0 and 23")
                    
                    minute = int(input("Enter minute (0-59): "))
                    if minute < 0 or minute > 59:
                        raise ValueError("Minute must be between 0 and 59")
                    
                    scheduled_time = datetime.now().replace(hour=hour, minute=minute)
                    
                    # If the time is in the past, schedule for tomorrow
                    if scheduled_time < datetime.now():
                        scheduled_time += timedelta(days=1)
                    
                    assistant.schedule_post(content, platform, scheduled_time)
                    print(f"\nPost scheduled successfully for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                    
                except ValueError as e:
                    print(f"Invalid time format: {str(e)}")
                
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")
                
        elif choice == '4':
            if not any(content.scheduled_posts for content in assistant.content_library):
                print("No scheduled posts found.")
                continue
                
            print("\nScheduled Posts:")
            for content in assistant.content_library:
                if content.scheduled_posts:
                    print(f"\nContent: {content.title}")
                    for post in content.scheduled_posts:
                        platform_name = post.platform.upper()
                        status = "Posted" if post.posted else "Pending"
                        print(f"- {platform_name}: Scheduled for {post.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                        print(f"  Status: {status}")
                        
        elif choice == '5':
            assistant.save_library()
            print("Library saved successfully!")
            
        elif choice == '6':
            confirmation = input("Are you sure you want to delete the JSON file and clear the library? (yes/no): ").lower()
            if confirmation == 'yes':
                assistant.delete_json_and_clear()
            else:
                print("Operation cancelled.")
                
        elif choice == '7':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()