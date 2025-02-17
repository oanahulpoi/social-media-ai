import os
from typing import List, Dict, Union
from datetime import datetime
import json
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
_ = load_dotenv(find_dotenv())

@dataclass
class Content:
    """Data class to store content information"""
    url: str
    title: str
    summary: str
    platform_posts: Dict[str, str]
    keywords: List[str]
    posted: bool = False

class SocialMediaAssistant:
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the Social Media Assistant with OpenAI client and configurations"""
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model = model
        self.content_library: List[Content] = []
        self.platform_specs = {
            'twitter': {'max_length': 280, 'hashtag_limit': 3},
            'linkedin': {'max_length': 3000, 'hashtag_limit': 5},
            'facebook': {'max_length': 2000, 'hashtag_limit': 4}
        }
        
    def extract_content(self, url: str) -> Dict[str, str]:
        """Extract content from a given URL"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and main content
            title = soup.title.string if soup.title else ""
            
            # Get main content (this is a simple implementation)
            article = soup.find('article') or soup.find('main') or soup.find('body')
            content = ' '.join([p.text for p in article.find_all('p')])
            
            return {'title': title, 'content': content}
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            return {'title': '', 'content': ''}

    def generate_platform_posts(self, content: str, title: str) -> Dict[str, str]:
        """Generate platform-specific posts using AI"""
        posts = {}
        
        for platform, specs in self.platform_specs.items():
            prompt = f"""
            Create a {platform} post for the following content:
            Title: {title}
            Content: {content}
            
            Requirements:
            - Maximum length: {specs['max_length']} characters
            - Maximum {specs['hashtag_limit']} relevant hashtags
            - Include a call to action
            - Make it engaging for {platform}'s audience
            """
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional social media manager."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                posts[platform] = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating {platform} post: {str(e)}")
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

    def process_url(self, url: str) -> Content:
        """Process a URL and generate all necessary content"""
        # Extract content from URL
        extracted = self.extract_content(url)
        
        # Generate platform-specific posts
        posts = self.generate_platform_posts(extracted['content'], extracted['title'])
        
        # Extract keywords
        keywords = self.extract_keywords(extracted['content'])
        
        # Create Content object
        content = Content(
            url=url,
            title=extracted['title'],
            summary=extracted['content'][:200] + "...",
            platform_posts=posts,
            keywords=keywords
        )
        
        self.content_library.append(content)
        return content

    def save_library(self, filename: str = 'content_library.json') -> None:
        """Save content library to a JSON file"""
        library_data = []
        for content in self.content_library:
            content_dict = {
                'url': content.url,
                'title': content.title,
                'summary': content.summary,
                'platform_posts': content.platform_posts,
                'keywords': content.keywords,
                'posted': content.posted
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
                content = Content(
                    url=item['url'],
                    title=item['title'],
                    summary=item['summary'],
                    platform_posts=item['platform_posts'],
                    keywords=item['keywords'],
                    posted=item['posted']
                )
                self.content_library.append(content)
        except FileNotFoundError:
            print(f"No existing library found at {filename}")

def main():
    """Main function to demonstrate the Social Media Assistant"""
    assistant = SocialMediaAssistant()
    
    # Load existing library if available
    assistant.load_library()
    
    while True:
        print("\nSocial Media Assistant Menu:")
        print("1. Process new URL")
        print("2. View content library")
        print("3. Save library")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            url = input("Enter URL to process: ")
            content = assistant.process_url(url)
            print("\nProcessed Content:")
            print(f"Title: {content.title}")
            print("\nPlatform Posts:")
            for platform, post in content.platform_posts.items():
                print(f"\n{platform.upper()}:")
                print(post)
            print("\nKeywords:", ", ".join(content.keywords))
            
        elif choice == '2':
            print("\nContent Library:")
            for i, content in enumerate(assistant.content_library, 1):
                print(f"\n{i}. {content.title}")
                print(f"URL: {content.url}")
                print(f"Summary: {content.summary}")
                print(f"Keywords: {', '.join(content.keywords)}")
                print("\nPlatform Posts:")
                for platform, post in content.platform_posts.items():
                    print(f"\n{platform.upper()}:")
                    print(post)
                print("\nPosted:", "Yes" if content.posted else "No")
                print("-" * 80)
                
        elif choice == '3':
            assistant.save_library()
            print("Library saved successfully!")
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()