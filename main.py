import requests
import html2text
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

download_folder = './img/'
blog_folder = "./blogs"


if not os.path.exists(blog_folder):
    os.makedirs(blog_folder)

def download_images(soup, base_url, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    images = soup.find_all('img')
    for img in images:
        img_url = img.get('src')
        if img_url:
            img_url = urljoin(base_url, img_url)  
            img_name = os.path.basename(img_url)
            img_path = os.path.join(download_folder, img_name)

            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded: {img_path}")
                img['src'] = os.path.join(download_folder, img_name)
            else:
                print(f"Failed to download image: {img_url}")

def get_single_post(url):
    if "hackvent" in url.lower() or "holidayhack" in url.lower() or "adventofcode" in url or "flare" in url:
        filename = blog_folder + "/" + "-".join(url.split("/")[3:]).rstrip("-") + ".md"
    else:
        filename = blog_folder + "/" + url.split("/")[-1].replace("html", "md")

    if os.path.exists(filename):
        print(f"Already downloaded at {filename}")
        return
        
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return

    
    soup = BeautifulSoup(response.content, 'html.parser')

    download_images(soup, url, download_folder)
    
    article = soup.find('article', class_='post')
    
    if article:
        h = html2text.HTML2Text()
        h.ignore_links = False 
        markdown_content = h.handle(str(article))
        
        markdown_content = fix_file(markdown_content)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Post saved at {filename}")
    else:
        print("No article content found.")

def get_all_posts(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    posts = soup.find_all('li', class_='post-list-li')
    
    data = []
    for post in posts:
        date = post.find('span', class_='post-meta').text.strip()
        title = post.find('h3', class_='post-list-h3').text.strip()
        link = post.find('a', class_='post-link')['href']
        tags = [tag.text.strip() for tag in post.find_all('a', class_='post-tag')]
        description = post.find('p').text.strip()
        
        data.append({
            "date": date,
            "title": title,
            "link": link,
            "tags": tags,
            "description": description
        })
    return data

def fix_file(markdown_content):
    lines = markdown_content.split('\n')

    processed_lines = []
    for line in lines:
        if "0xdfimages" not in line:
            line = line.replace('./img\\\\', '../img/', 1)
            line = line.replace('/img/', '../img/', 1)
            line = line.replace('./icons/', '../img/', 1)
            line = line.replace('/icons/', '../img/', 1)
        processed_lines.append(line)

    markdown_content = '\n'.join(processed_lines)

    return markdown_content

def main():
    url = 'https://0xdf.gitlab.io/'  
    all_posts = get_all_posts(url)
    for post in all_posts:
        post_link = "https://0xdf.gitlab.io" + post['link']
        get_single_post(post_link)

main()